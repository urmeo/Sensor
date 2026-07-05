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


def test_fixation_durations_match_independent_per_fixation_max():
    sed_fix = sd.load("sed_fix")
    durations = sd.fixation_durations(sed_fix)
    fixation_rows = sed_fix[sed_fix["fixation"]]
    expected = fixation_rows.groupby("fixation_id")["duration"].max()
    expected = expected[expected > 0]
    assert durations.equals(expected)
    assert durations.index.name == "fixation_id"
