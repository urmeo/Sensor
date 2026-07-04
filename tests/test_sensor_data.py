"""Tests for the shared sensor_data loader module."""

import sensor_data as sd


def test_load_all_returns_every_csv():
    data = sd.load_all()
    assert set(data) == set(sd.CSV_FILES)
    assert data["hrv"].shape[0] == 264
    assert data["psych"].shape[0] == 88


def test_valid_hr_keeps_only_confident_rows():
    hr = sd.load("hr")
    kept = sd.valid_hr(hr)
    assert (kept["confidence"] == 1.0).all()
    assert 0 < len(kept) <= len(hr)


def test_valid_pupil_drops_tracking_loss():
    kept = sd.valid_pupil(sd.load("sed_fix"))
    assert (kept["pupil"] > 0).all()
    assert (kept["pupilQ"] > 0.5).all()


def test_fixation_durations_are_positive_and_per_fixation():
    durations = sd.fixation_durations(sd.load("sed_fix"))
    assert (durations > 0).all()
    assert durations.index.name == "fixation_id"
