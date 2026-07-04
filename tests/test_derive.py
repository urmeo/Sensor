"""The derivation pipeline must reproduce the committed sed_fix.csv exactly."""

import numpy as np

import sensor_data as sd
from scripts import derive


def test_detect_fixations_reproduces_committed_file():
    derived = derive.detect_fixations(sd.load("sed"))
    committed = sd.load("sed_fix")

    assert list(derived.columns) == list(committed.columns)
    for col in committed.columns:
        a, b = derived[col], committed[col]
        if col in ("gaze_diff", "duration"):
            assert np.allclose(a.to_numpy(), b.to_numpy(), rtol=0, atol=1e-9, equal_nan=True), col
        else:
            assert a.equals(b), col


def test_check_helper_passes():
    assert derive.check() is True
