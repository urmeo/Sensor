"""Produce a de-identified, relative-time copy of the dataset.

The shipped CSVs keep absolute wall-clock timestamps for time-series work. That
carries a small re-identification surface (a precise date/time anchor). This
script writes a variant under `data/relative/` in which every absolute calendar
timestamp is replaced by seconds-since-session-start:

- sensor files (hr, ibi, sed, sed_fix): drop the absolute `datetime` column and
  keep the already-relative `reltime`.
- HRV.csv: replace `Start Time` / `End Time` with `Start (s)` / `End (s)`,
  measured from the earliest timestamp of that session (`Test`).
- Psychometric_Test_Results.csv: replace the two absolute question timestamps
  with seconds from the first question.

Run: `python scripts/shift_time.py`  (writes data/relative/, git-ignored).
"""
import pandas as pd

import sensor_data as sd

SENSOR_FILES = {"hr", "ibi", "sed", "sed_fix"}


def to_relative(df, name):
    """Return a copy of `df` with absolute calendar timestamps removed."""
    df = df.copy()
    if name in SENSOR_FILES:
        return df.drop(columns=[c for c in ["datetime"] if c in df.columns])
    if name == "hrv":
        start = pd.to_datetime(df["Start Time"], format="mixed")
        end = pd.to_datetime(df["End Time"], format="mixed")
        base = start.groupby(df["Test"]).transform("min")  # session start, shared by both
        df["Start (s)"] = (start - base).dt.total_seconds()
        df["End (s)"] = (end - base).dt.total_seconds()
        return df.drop(columns=["Start Time", "End Time"])
    if name == "psych":
        base = pd.to_datetime(df["Question Start Time"], format="mixed").min()
        for src, dst in [("Question Start Time", "Question Start (s)"),
                         ("Question Answer Time", "Question Answer (s)")]:
            df[dst] = (pd.to_datetime(df[src], format="mixed") - base).dt.total_seconds()
        return df.drop(columns=["Question Start Time", "Question Answer Time"])
    return df


def main():
    out_dir = sd.DATA_DIR / "relative"
    out_dir.mkdir(exist_ok=True)
    for name, filename in sd.CSV_FILES.items():
        to_relative(sd.load(name), name).to_csv(out_dir / filename, index=False)
    print(f"wrote de-identified variant to {out_dir}")


if __name__ == "__main__":
    main()
