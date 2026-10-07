"""Relative copies preserve observations and reject malformed clocks."""

import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import sensor_data as sd
from scripts import shift_time


def test_sensor_variant_drops_absolute_datetime():
    for name in ("hr", "ibi", "sed", "sed_fix"):
        out = shift_time.to_relative(sd.load(name), name)
        assert "datetime" not in out.columns
        assert "reltime" in out.columns


def test_hrv_variant_is_relative_seconds():
    out = shift_time.to_relative(sd.load("eye_metrics"), "eye_metrics")
    assert {"Start Time", "End Time"}.isdisjoint(out.columns)
    assert {"Start (s)", "End (s)"} <= set(out.columns)
    assert (out["Start (s)"] >= 0).all()
    assert (out["End (s)"] >= out["Start (s)"]).all()


def test_psych_variant_is_relative_seconds():
    out = shift_time.to_relative(sd.load("psych"), "psych")
    assert {"Question Start Time", "Question Answer Time"}.isdisjoint(out.columns)
    assert {"Question Start (s)", "Question Answer (s)"} <= set(out.columns)
    assert (out["Question Start (s)"] >= 0).all()


def sensor_frame():
    return pd.DataFrame(
        {
            "datetime": ["2026-01-01 08:00:00.100", "2026-01-01 08:00:00.200"],
            "reltime": [0.1, 0.2],
            "observation": [11, 22],
        },
        index=[4, 7],
    )


def eye_frame():
    return pd.DataFrame(
        {
            "Test": [1, 2, 1, 2],
            "Start Time": [
                "2026-01-01 08:00:00",
                "2026-01-02 09:00:00",
                "2026-01-01 08:00:03",
                "2026-01-02 09:00:05",
            ],
            "End Time": [
                "2026-01-01 08:00:01",
                "2026-01-02 09:00:00.25",
                "2026-01-01 08:00:04.5",
                "2026-01-02 09:00:05",
            ],
            "observation": [11, 22, 33, 44],
        },
        index=[4, 7, 10, 12],
    )


def psych_frame():
    return pd.DataFrame(
        {
            "Question Start Time": ["2026-01-01T08:00:00+05:30", "2026-01-01T08:00:02+05:30"],
            "Question Answer Time": ["2026-01-01T08:00:01.25+05:30", "2026-01-01T08:00:02.5+05:30"],
            "observation": [11, 22],
        },
        index=[4, 7],
    )


def write_inputs(directory, invalid_late=False):
    directory.mkdir()
    frames = {name: sensor_frame() for name in shift_time.SENSOR_FILES}
    frames.update(eye_metrics=eye_frame(), psych=psych_frame())
    if invalid_late:
        frames["psych"].loc[4, "Question Answer Time"] = "not-a-time"
    for name, filename in sd.CSV_FILES.items():
        frames[name].to_csv(directory / filename, index=False)


def run_cli(*arguments):
    return subprocess.run(
        [sys.executable, "-m", "scripts.shift_time", *map(str, arguments)],
        cwd=Path(shift_time.__file__).parents[1],
        capture_output=True,
        text=True,
        check=False,
    )


def test_unknown_resource_is_not_returned_unchanged():
    with pytest.raises(KeyError, match="unknown dataset"):
        shift_time.to_relative(sensor_frame(), "unknown")


@pytest.mark.parametrize(
    "name,make", [("hr", sensor_frame), ("eye_metrics", eye_frame), ("psych", psych_frame)]
)
def test_relative_copy_preserves_non_time_columns_and_input(name, make):
    frame = make()
    original = frame.copy(deep=True)
    out = shift_time.to_relative(frame, name)
    assert out.index.equals(frame.index)
    pd.testing.assert_series_equal(out["observation"], frame["observation"])
    pd.testing.assert_frame_equal(frame, original)
    if name == "hr":
        pd.testing.assert_series_equal(out["reltime"], frame["reltime"])


def test_eye_sessions_have_distinct_zero_points_and_preserved_intervals():
    frame = eye_frame()
    out = shift_time.to_relative(frame, "eye_metrics")
    assert out["Start (s)"].tolist() == [0, 0, 3, 5]
    np.testing.assert_allclose(out["End (s)"] - out["Start (s)"], [1, 0.25, 1.5, 0])
    assert out.groupby("Test")["Start (s)"].min().tolist() == [0, 0]


def test_aware_questionnaire_preserves_elapsed_intervals_without_localizing():
    frame = psych_frame()
    parsed = shift_time.parse_timestamps(frame["Question Start Time"], "start")
    assert str(parsed.dt.tz) == "UTC+05:30"
    out = shift_time.to_relative(frame, "psych")
    assert out["Question Start (s)"].tolist() == [0, 2]
    np.testing.assert_allclose(out["Question Answer (s)"] - out["Question Start (s)"], [1.25, 0.5])
    assert shift_time.parse_timestamps(sensor_frame()["datetime"], "datetime").dt.tz is None


@pytest.mark.parametrize(
    "values",
    [
        [None, "2026-01-01"],
        ["NaT", "2026-01-01"],
        ["invalid", "2026-01-01"],
        [1, 2],
        ["2026-01-01", "2026-01-01T08:00:00Z"],
        ["2026-01-01T08:00:00+00:00", "2026-01-01T08:00:00+01:00"],
    ],
)
def test_timestamp_validation_rejects_missing_invalid_and_mixed_zone_values(values):
    with pytest.raises(ValueError, match="timestamp"):
        shift_time.parse_timestamps(pd.Series(values), "start")


@pytest.mark.parametrize(
    "name,make,start,end",
    [
        ("eye_metrics", eye_frame, "Start Time", "End Time"),
        ("psych", psych_frame, "Question Start Time", "Question Answer Time"),
    ],
)
def test_reversed_intervals_and_missing_timestamp_columns_are_rejected(name, make, start, end):
    frame = make()
    frame.loc[4, end] = "2025-01-01T00:00:00+05:30" if name == "psych" else "2025-01-01"
    with pytest.raises(ValueError, match="precede"):
        shift_time.to_relative(frame, name)
    with pytest.raises(ValueError, match="Missing required"):
        shift_time.to_relative(make().drop(columns=start), name)


def test_paired_start_end_zones_must_match():
    frame = psych_frame()
    frame["Question Answer Time"] = ["2026-01-01T08:00:01Z", "2026-01-01T08:00:03Z"]
    with pytest.raises(ValueError, match="same timezone"):
        shift_time.to_relative(frame, "psych")


@pytest.mark.parametrize(
    "bad_times", [[0.2, 0.1], [-1, 0], [0, np.inf], [0, np.nan], [True, False]]
)
def test_sensor_relative_time_guards(bad_times):
    frame = sensor_frame()
    frame["reltime"] = bad_times
    with pytest.raises(ValueError, match="reltime"):
        shift_time.to_relative(frame, "hr")


def test_sensor_calendar_clock_must_not_decrease_before_removal():
    frame = sensor_frame()
    frame["datetime"] = frame["datetime"].tolist()[::-1]
    with pytest.raises(ValueError, match="datetime must be nondecreasing"):
        shift_time.to_relative(frame, "hr")


def test_large_integer_relative_times_do_not_hide_decreasing_order():
    frame = sensor_frame()
    frame["reltime"] = np.array([2**60 + 1, 2**60], dtype=np.uint64)
    with pytest.raises(ValueError, match="nondecreasing"):
        shift_time.to_relative(frame, "hr")
    frame["reltime"] = np.array([2**60, 2**60 + 1], dtype=np.uint64)
    pd.testing.assert_series_equal(shift_time.to_relative(frame, "hr")["reltime"], frame["reltime"])


@pytest.mark.parametrize(
    "name,make", [("hr", sensor_frame), ("eye_metrics", eye_frame), ("psych", psych_frame)]
)
def test_empty_known_schema_is_a_valid_copy(name, make):
    frame = make().iloc[:0]
    out = shift_time.to_relative(frame, name)
    assert out.empty and out.index.equals(frame.index)


@pytest.mark.parametrize(
    "arguments,status",
    [(["--help"], 0), ([], 2), (["--ouput-dir", "unused"], 2), (["--output-d", "unused"], 2)],
)
def test_actual_module_help_and_argument_errors_do_not_export(tmp_path, arguments, status):
    missing = tmp_path / "missing-input"
    result = run_cli("--data-dir", missing, *arguments)
    assert result.returncode == status
    assert not missing.exists()


def test_actual_module_validates_every_resource_before_any_output(tmp_path):
    data = tmp_path / "input"
    write_inputs(data, invalid_late=True)
    output = tmp_path / "outputs" / "relative"
    result = run_cli("--data-dir", data, "--output-dir", output)
    assert result.returncode == 1 and "timestamp" in result.stderr
    assert not output.exists()


def test_actual_module_export_routes_files_and_preserves_sources(tmp_path):
    data = tmp_path / "input"
    write_inputs(data)
    before = {file.name: hashlib.sha256(file.read_bytes()).digest() for file in data.iterdir()}
    output = tmp_path / "outputs" / "relative"
    result = run_cli("--data-dir", data, "--output-dir", output)
    assert result.returncode == 0, result.stderr
    assert {file.name for file in output.iterdir()} == set(sd.CSV_FILES.values())
    assert before == {
        file.name: hashlib.sha256(file.read_bytes()).digest() for file in data.iterdir()
    }
    assert "datetime" not in pd.read_csv(output / "hr.csv").columns
    assert "Question Start Time" not in pd.read_csv(output / sd.CSV_FILES["psych"]).columns
    result = run_cli("--data-dir", data, "--output-dir", data)
    assert result.returncode == 1 and "overwrite source CSV" in result.stderr
    assert before == {
        file.name: hashlib.sha256(file.read_bytes()).digest() for file in data.iterdir()
    }


def test_output_directory_symlink_cannot_alias_source(tmp_path):
    data = tmp_path / "input"
    write_inputs(data)
    alias = tmp_path / "alias"
    alias.symlink_to(data, target_is_directory=True)
    result = run_cli("--data-dir", data, "--output-dir", alias)
    assert result.returncode == 1 and "overwrite source CSV" in result.stderr


def test_cyclic_output_directory_cli_gives_no_traceback(tmp_path):
    cycle = tmp_path / "cycle"
    cycle.symlink_to("cycle")
    result = run_cli("--data-dir", tmp_path, "--output-dir", cycle)
    assert result.returncode == 1 and "Cannot resolve" in result.stderr
    assert "Traceback" not in result.stderr
