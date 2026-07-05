"""Enforce datapackage.json as a checked contract over the CSVs.

Every column's type, required-ness, range, and allowed values declared in the
Frictionless data package is verified against the real data, plus a handful of
cross-file invariants the data dictionary asserts. If the data drifts from its
documented schema, these tests fail.
"""

import json
from pathlib import Path

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
        if "minimum" in cons:
            assert valued.min() >= cons["minimum"], f"{name}.{col}: below minimum {cons['minimum']}"
        if "maximum" in cons:
            assert valued.max() <= cons["maximum"], f"{name}.{col}: above maximum {cons['maximum']}"
        if "enum" in cons:
            extra = set(valued.unique()) - set(cons["enum"])
            assert not extra, f"{name}.{col}: unexpected values {extra}"


def test_hrv_is_88_questions_times_3_sessions():
    df = _load(RESOURCES["hrv"])
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


def test_sensor_files_share_one_recording_window():
    windows = {}
    for name in ("hr", "ibi", "sed", "sed_fix"):
        df = _load(RESOURCES[name])
        dt = pd.to_datetime(df["datetime"])
        windows[name] = dt.min().date()
        assert dt.min().date().isoformat() == "2024-06-13"
        assert 530 < (df["reltime"].max() - df["reltime"].min()) < 536
    assert len(set(windows.values())) == 1


def test_sed_fix_is_a_superset_of_sed():
    sed = _load(RESOURCES["sed"])
    sed_fix = _load(RESOURCES["sed_fix"])
    derived_cols = set(DERIVED_COLUMNS)
    assert len(sed) == len(sed_fix)
    assert set(sed.columns).issubset(sed_fix.columns)
    assert set(sed_fix.columns) - set(sed.columns) == derived_cols
