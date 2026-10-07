"""Smoke-test only the six declared source CSVs."""

import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = json.loads((ROOT / "datapackage.json").read_text())
CSV_FILES = [ROOT / resource["path"] for resource in PACKAGE["resources"]]


def test_csv_files_present():
    assert len(CSV_FILES) == 6
    assert len(set(CSV_FILES)) == len(CSV_FILES)
    assert all(path.is_file() for path in CSV_FILES)


@pytest.mark.parametrize("path", CSV_FILES, ids=[str(p.relative_to(ROOT)) for p in CSV_FILES])
def test_csv_loads_and_is_non_trivial(path):
    rel = path.relative_to(ROOT)
    assert path.stat().st_size > 0, f"{rel} is a zero-byte file"
    df = pd.read_csv(path)
    assert df.shape[0] >= 1, f"{rel} has no data rows"
    assert df.shape[1] >= 1, f"{rel} has no columns"
