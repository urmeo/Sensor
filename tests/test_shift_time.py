"""The de-identified variant must contain no absolute calendar timestamps."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import shift_time
import sensor_data as sd


def test_sensor_variant_drops_absolute_datetime():
    for name in ("hr", "ibi", "sed", "sed_fix"):
        out = shift_time.to_relative(sd.load(name), name)
        assert "datetime" not in out.columns
        assert "reltime" in out.columns


def test_hrv_variant_is_relative_seconds():
    out = shift_time.to_relative(sd.load("hrv"), "hrv")
    assert {"Start Time", "End Time"}.isdisjoint(out.columns)
    assert {"Start (s)", "End (s)"} <= set(out.columns)
    assert (out["Start (s)"] >= 0).all()
    assert (out["End (s)"] >= out["Start (s)"]).all()


def test_psych_variant_is_relative_seconds():
    out = shift_time.to_relative(sd.load("psych"), "psych")
    assert {"Question Start Time", "Question Answer Time"}.isdisjoint(out.columns)
    assert {"Question Start (s)", "Question Answer (s)"} <= set(out.columns)
    assert (out["Question Start (s)"] >= 0).all()
