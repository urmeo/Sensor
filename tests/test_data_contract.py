"""Check source schemas and each resource's own clock."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pandas.api.types as pdt
import pytest

from scripts.derive import DERIVED_COLUMNS

ROOT = Path(__file__).resolve().parents[1]
PKG = json.loads((ROOT / "datapackage.json").read_text())
RESOURCES = {r["name"]: r for r in PKG["resources"]}


def _dtype_ok(series, declared_type):
    """Version-stable type check (pandas 2.x object strings and 3.x str dtype)."""
    if declared_type == "integer":
        return pdt.is_integer_dtype(series)
    if declared_type == "number":
        return pdt.is_numeric_dtype(series) and not pdt.is_bool_dtype(series)
    if declared_type == "boolean":
        return pdt.is_bool_dtype(series)
    if declared_type == "string":
        return pdt.is_string_dtype(series) or series.dtype == object
    return False


def _load(resource):
    return pd.read_csv(ROOT / resource["path"])


@pytest.mark.parametrize("name", list(RESOURCES), ids=list(RESOURCES))
def test_resource_shape_and_columns(name):
    r = RESOURCES[name]
    df = _load(r)
    fields = [f["name"] for f in r["schema"]["fields"]]
    assert df.shape[0] == r["rowCount"], f"{name}: expected {r['rowCount']} rows, got {df.shape[0]}"
    assert list(df.columns) == fields, f"{name}: columns/order drifted from schema"


@pytest.mark.parametrize("name", list(RESOURCES), ids=list(RESOURCES))
def test_field_types_required_ranges_enums(name):
    r = RESOURCES[name]
    df = _load(r)
    for f in r["schema"]["fields"]:
        col, typ, cons = f["name"], f["type"], f.get("constraints", {})
        series = df[col]
        assert _dtype_ok(series, typ), f"{name}.{col}: {series.dtype} not a {typ}"
        if cons.get("required"):
            assert series.notna().all(), f"{name}.{col}: has nulls but is required"
        valued = series.dropna()
        if typ in {"number", "integer"}:
            assert np.isfinite(valued.to_numpy()).all(), f"{name}.{col}: nonfinite value"
        if "minimum" in cons:
            assert valued.min() >= cons["minimum"], f"{name}.{col}: below minimum {cons['minimum']}"
        if "maximum" in cons:
            assert valued.max() <= cons["maximum"], f"{name}.{col}: above maximum {cons['maximum']}"
        if "enum" in cons:
            extra = set(valued.unique()) - set(cons["enum"])
            assert not extra, f"{name}.{col}: unexpected values {extra}"


def test_eye_metrics_is_88_questions_times_3_sessions():
    df = _load(RESOURCES["eye_metrics"])
    assert len(df) == 264
    assert df["Test"].value_counts().to_dict() == {"Test 01": 88, "Test 02": 88, "Test 03": 88}


def test_psychometric_test_composition():
    df = _load(RESOURCES["psych"])
    assert df["Test"].value_counts().to_dict() == {
        "FQ": 24,
        "STAI-S": 20,
        "STAI-T": 20,
        "HADS": 14,
        "BFI": 10,
    }


def test_sensor_recordings_each_have_the_documented_date_and_span():
    for name in ("hr", "ibi", "sed", "sed_fix"):
        df = _load(RESOURCES[name])
        dt = pd.to_datetime(df["datetime"])
        assert dt.min().date().isoformat() == "2024-06-13"
        assert 530 < (df["reltime"].max() - df["reltime"].min()) < 536


def test_sed_fix_is_a_superset_of_sed():
    sed = _load(RESOURCES["sed"])
    sed_fix = _load(RESOURCES["sed_fix"])
    derived_cols = set(DERIVED_COLUMNS)
    assert len(sed) == len(sed_fix)
    assert set(sed.columns).issubset(sed_fix.columns)
    assert set(sed_fix.columns) - set(sed.columns) == derived_cols
    pd.testing.assert_frame_equal(sed, sed_fix[sed.columns])


def _timestamps(df, column, aware):
    assert df[column].notna().all(), f"{column}: missing timestamp"
    try:
        stamps = pd.to_datetime(df[column], format="mixed")
    except (ValueError, TypeError, OverflowError) as exc:
        raise AssertionError(f"{column}: invalid timestamp") from exc
    assert pdt.is_datetime64_any_dtype(stamps), f"{column}: inconsistent clocks"
    zone = stamps.dt.tz
    if aware:
        assert str(zone) == "UTC", f"{column}: expected UTC clock"
    else:
        assert zone is None, f"{column}: expected unspecified naive clock"
    assert stamps.is_monotonic_increasing, f"{column}: decreasing timestamps"
    return stamps


def _check_times(df, name):
    if name in {"hr", "ibi", "sed", "sed_fix"}:
        stamps = _timestamps(df, "datetime", aware=False)
        relative = df["reltime"]
        assert np.isfinite(relative).all() and (relative >= 0).all()
        assert relative.is_monotonic_increasing, "decreasing recording time"
        if len(df):
            offsets = (stamps - stamps.iloc[0]).dt.total_seconds() - (relative - relative.iloc[0])
            assert np.allclose(offsets, 0, rtol=0, atol=1e-6), "datetime/reltime drift"
        if name == "sed_fix":
            spans = df.loc[df["fixation"], "duration"]
            assert np.isfinite(spans).all() and (spans >= 0).all()
            assert df.loc[~df["fixation"], "duration"].isna().all()
        return
    start_column, end_column = (
        ("Start Time", "End Time")
        if name == "eye_metrics"
        else ("Question Start Time", "Question Answer Time")
    )
    starts = _timestamps(df, start_column, aware=name == "psych")
    ends = _timestamps(df, end_column, aware=name == "psych")
    assert (ends >= starts).all(), "end precedes start"
    if name == "psych":
        duration = df["Time(s)"]
        assert np.isfinite(duration).all() and (duration >= 0).all()
        actual = (ends - starts).dt.total_seconds()
        assert np.allclose(actual, duration, rtol=0, atol=0.001 + 1e-12), "duration mismatch"


@pytest.mark.parametrize("name", list(RESOURCES))
def test_resource_temporal_contract(name):
    _check_times(_load(RESOURCES[name]), name)


@pytest.mark.parametrize("name", list(RESOURCES))
def test_source_clock_metadata(name):
    resource = RESOURCES[name]
    assert resource["timeZone"] == ("UTC" if name == "psych" else "unspecified")
    assert resource["timestampAwareness"] == ("aware" if name == "psych" else "naive")
    fields = (
        ["Start Time", "End Time"]
        if name == "eye_metrics"
        else ["Question Start Time", "Question Answer Time"]
        if name == "psych"
        else ["datetime"]
    )
    assert resource["timestampFields"] == fields
    assert resource["relativeTimeOrigin"]


@pytest.fixture
def sensor_clock():
    return pd.DataFrame(
        {"reltime": [0.2, 1.2], "datetime": ["2024/01/01 10:00:00", "2024/01/01 10:00:01"]}
    )


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("datetime", None),
        ("datetime", "not a timestamp"),
        ("datetime", "2024-01-01T10:00:00Z"),
        ("datetime", "2023-12-31 10:00:00"),
        ("reltime", np.inf),
        ("reltime", np.nan),
        ("reltime", -1),
        ("reltime", 0.1),
        ("reltime", 1.21),
    ],
)
def test_sensor_temporal_checks_reject_invalid_mutations(sensor_clock, column, value):
    sensor_clock.loc[1, column] = value
    with pytest.raises(AssertionError):
        _check_times(sensor_clock, "hr")


def test_equal_sensor_timestamps_remain_valid(sensor_clock):
    sensor_clock.loc[1] = sensor_clock.iloc[0]
    _check_times(sensor_clock, "hr")


@pytest.fixture
def question_clock():
    return pd.DataFrame(
        {
            "Question Start Time": ["2024-01-01T10:00:00Z", "2024-01-01T10:00:01Z"],
            "Question Answer Time": ["2024-01-01T10:00:00.500Z", "2024-01-01T10:00:01.500Z"],
            "Time(s)": [0.5, 0.5],
        }
    )


@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("Question Start Time", None),
        ("Question Start Time", "invalid"),
        ("Question Start Time", "2024-01-01 10:00:01"),
        ("Question Start Time", "2024-01-01T12:00:01+02:00"),
        ("Question Start Time", "2024-01-01T09:00:00Z"),
        ("Question Answer Time", "2024-01-01T10:00:00.900Z"),
        ("Time(s)", np.nan),
        ("Time(s)", np.inf),
        ("Time(s)", -1),
        ("Time(s)", 0.502),
    ],
)
def test_question_temporal_checks_reject_invalid_mutations(question_clock, column, value):
    question_clock.loc[1, column] = value
    with pytest.raises(AssertionError):
        _check_times(question_clock, "psych")


def test_question_duration_allows_millisecond_rounding(question_clock):
    question_clock["Time(s)"] = 0.499
    _check_times(question_clock, "psych")


@pytest.mark.parametrize("end", [None, "invalid", "2024-01-01T10:00:01Z", "2024-01-01 09:00:00"])
def test_eye_temporal_checks_reject_invalid_end(end):
    eye = pd.DataFrame({"Start Time": ["2024-01-01 10:00:00"], "End Time": [end]})
    with pytest.raises(AssertionError):
        _check_times(eye, "eye_metrics")
