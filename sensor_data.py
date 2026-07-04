"""Loaders and quality filters for the Sensor sample dataset.

Keeps data-access logic in one place so the analysis notebook and the test
suite share the same loading and filtering rules instead of copy-pasting them.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"

CSV_FILES = {
    "hr": "hr.csv",
    "ibi": "ibi.csv",
    "sed": "sed.csv",
    "sed_fix": "sed_fix.csv",
    "hrv": "HRV.csv",
    "psych": "Psychometric_Test_Results.csv",
}


def data_dir(base=None):
    return Path(base) if base is not None else DATA_DIR


def load(name, base=None):
    return pd.read_csv(data_dir(base) / CSV_FILES[name])


def load_all(base=None):
    return {name: load(name, base) for name in CSV_FILES}


def valid_hr(hr):
    """Heart-rate rows the sensor was confident about."""
    return hr[hr["confidence"] == 1.0].copy()


def valid_pupil(sed, min_quality=0.5):
    """Eye-tracking rows with a real pupil reading (drops tracking loss)."""
    return sed[(sed["pupil"] > 0) & (sed["pupilQ"] > min_quality)].copy()


def fixation_durations(sed_fix):
    """One duration in seconds per detected fixation."""
    durations = sed_fix[sed_fix["fixation"]].groupby("fixation_id")["duration"].max()
    return durations[durations > 0]
