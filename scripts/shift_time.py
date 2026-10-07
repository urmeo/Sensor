"""Write relative-time copies with calendar timestamp columns removed.

Sensors retain recording-relative reltime; eye summaries use each Test's earliest
start; questionnaire rows use their earliest start. These origins differ and do
not establish synchronization or anonymity. Naive timestamps remain unspecified.
"""

from __future__ import annotations

import argparse
import sys
from numbers import Real
from pathlib import Path

import numpy as np
import pandas as pd

import sensor_data as sd

SENSOR_FILES: set[str] = {"hr", "ibi", "sed", "sed_fix"}


def parse_timestamps(values: pd.Series, column: str) -> pd.Series:
    """Parse non-null timestamps with one consistent zone or no zone."""
    if values.isna().any():
        raise ValueError(f"{column} must contain non-null timestamps")
    if any(isinstance(value, (Real, np.bool_)) for value in values):
        raise ValueError(f"{column} must contain calendar timestamps, not numbers")
    try:
        parsed = [pd.Timestamp(value) for value in values]
        zones = {str(value.tzinfo) if value.tzinfo is not None else None for value in parsed}
        if len(zones) > 1:
            raise ValueError("mixed timezone values")
        result = pd.Series(pd.DatetimeIndex(parsed), index=values.index, name=values.name)
    except (ValueError, TypeError, OverflowError) as error:
        raise ValueError(f"{column} must contain parseable timestamps with one timezone") from error
    if result.isna().any():
        raise ValueError(f"{column} must contain non-null timestamps")
    return result


def to_relative(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Return a validated copy using the resource's documented relative origin."""
    if name not in sd.CSV_FILES:
        raise KeyError(f"unknown dataset {name!r}; valid names: {sorted(sd.CSV_FILES)}")
    if not df.columns.is_unique:
        raise ValueError("Input columns must be unique")
    if name in SENSOR_FILES:
        required = {"datetime", "reltime"}
    elif name == "eye_metrics":
        required = {"Test", "Start Time", "End Time"}
    else:
        required = {"Question Start Time", "Question Answer Time"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns for {name}: {sorted(missing)}")
    out = df.copy()
    if name in SENSOR_FILES:
        clock = parse_timestamps(df["datetime"], "datetime")
        if (clock.diff().dropna() < pd.Timedelta(0)).any():
            raise ValueError("datetime must be nondecreasing")
        if df.empty:
            return out.drop(columns=["datetime"])
        if (
            not pd.api.types.is_numeric_dtype(df["reltime"])
            or pd.api.types.is_bool_dtype(df["reltime"])
            or pd.api.types.is_complex_dtype(df["reltime"])
        ):
            raise ValueError("reltime must contain finite real numeric values")
        if (
            (df["reltime"] < 0).any()
            or not df["reltime"].is_monotonic_increasing
            or not np.isfinite(df["reltime"].to_numpy(dtype=float, na_value=np.nan)).all()
        ):
            raise ValueError("reltime must be finite, nonnegative and nondecreasing")
        return out.drop(columns=["datetime"])
    if name == "eye_metrics":
        if df["Test"].isna().any():
            raise ValueError("Test must contain non-null session labels")
        start = parse_timestamps(df["Start Time"], "Start Time")
        end = parse_timestamps(df["End Time"], "End Time")
    else:
        start = parse_timestamps(df["Question Start Time"], "Question Start Time")
        end = parse_timestamps(df["Question Answer Time"], "Question Answer Time")
    if start.dt.tz != end.dt.tz:
        raise ValueError("Start and end timestamps must use the same timezone")
    if (end < start).any():
        raise ValueError("End timestamps must not precede their start")
    if name == "eye_metrics":
        base = start.groupby(df["Test"]).transform("min")
        out["Start (s)"] = (start - base).dt.total_seconds()
        out["End (s)"] = (end - base).dt.total_seconds()
        out = out.drop(columns=["Start Time", "End Time"])
    else:
        out["Question Start (s)"] = (start - start.min()).dt.total_seconds()
        out["Question Answer (s)"] = (end - start.min()).dt.total_seconds()
        out = out.drop(columns=["Question Start Time", "Question Answer Time"])
    relative_columns = (
        ["Start (s)", "End (s)"]
        if name == "eye_metrics"
        else ["Question Start (s)", "Question Answer (s)"]
    )
    if not np.isfinite(out[relative_columns].to_numpy(dtype=float)).all():
        raise ValueError("Elapsed intervals must be finite")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write validated relative-time copies to an explicit output directory.",
        allow_abbrev=False,
    )
    parser.add_argument("--data-dir", type=Path, help="Directory containing the source CSVs")
    parser.add_argument("--output-dir", type=Path, required=True, help="Separate output directory")
    args = parser.parse_args(argv)
    try:
        destinations = {
            name: sd.validate_output_path(args.output_dir / filename, args.data_dir)
            for name, filename in sd.CSV_FILES.items()
        }
        converted = {name: to_relative(df, name) for name, df in sd.load_all(args.data_dir).items()}
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, out in converted.items():
            out.to_csv(destinations[name], index=False)
        print(f"wrote relative-time copies to {args.output_dir}")
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f"shift_time: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
