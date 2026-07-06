"""Loaders and quality filters for the Sensor sample dataset.

Keeps data-access logic in one place so the analysis notebook and the test
suite share the same loading and filtering rules instead of copy-pasting them.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA_DIR: Path = Path(__file__).resolve().parent / "data"

CSV_FILES: dict[str, str] = {
    "hr": "hr.csv",
    "ibi": "ibi.csv",
    "sed": "sed.csv",
    "sed_fix": "sed_fix.csv",
    "eye_metrics": "eye_metrics.csv",
    "psych": "Psychometric_Test_Results.csv",
}


def data_dir(base: str | Path | None = None) -> Path:
    return Path(base) if base is not None else DATA_DIR


def load(name: str, base: str | Path | None = None) -> pd.DataFrame:
    if name not in CSV_FILES:
        raise KeyError(f"unknown dataset {name!r}; valid names: {sorted(CSV_FILES)}")
    return pd.read_csv(data_dir(base) / CSV_FILES[name])


def load_all(base: str | Path | None = None) -> dict[str, pd.DataFrame]:
    return {name: load(name, base) for name in CSV_FILES}


def valid_hr(hr: pd.DataFrame) -> pd.DataFrame:
    """Heart-rate rows the sensor was confident about."""
    return hr[hr["confidence"] == 1.0].copy()


def valid_pupil(eye: pd.DataFrame, min_quality: float = 0.5) -> pd.DataFrame:
    """Eye-tracking rows with a real pupil reading (drops tracking loss)."""
    return eye[(eye["pupil"] > 0) & (eye["pupilQ"] > min_quality)].copy()


def fixation_durations(sed_fix: pd.DataFrame) -> pd.Series:
    """Duration (seconds) of each multi-sample fixation; single-sample runs
    (which have zero measured span) are excluded."""
    durations = sed_fix[sed_fix["fixation"]].groupby("fixation_id")["duration"].max()
    return durations[durations > 0]
