"""The derivation pipeline must reproduce the committed sed_fix.csv exactly."""

import runpy
import sys

import numpy as np
import pandas as pd
import pytest

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


def test_detect_fixations_accepts_empty_recording():
    empty = pd.DataFrame(columns=["gazeDir.x", "gazeDir.y", "gazeDir.z", "reltime"], dtype=float)
    out = derive.detect_fixations(empty)
    assert out.empty
    assert list(out.columns) == list(empty.columns) + derive.DERIVED_COLUMNS


@pytest.mark.parametrize("matches", [True, False])
def test_check_command_exit_status(monkeypatch, capsys, matches):
    raw = pd.DataFrame(
        {
            "gazeDir.x": [0.0, 0.0],
            "gazeDir.y": [0.0, 0.0],
            "gazeDir.z": [1.0, 1.0],
            "reltime": [0.0, 1.0],
        }
    )
    committed = derive.detect_fixations(raw)
    if not matches:
        committed.loc[1, "duration"] = 99.0
    monkeypatch.setattr(sd, "load", lambda name, base=None: raw if name == "sed" else committed)
    monkeypatch.setattr(sys, "argv", ["scripts/derive.py", "--check"])
    with pytest.raises(SystemExit) as result:
        runpy.run_path(derive.__file__, run_name="__main__")
    assert result.value.code == (0 if matches else 1)
    assert str(matches) in capsys.readouterr().out
