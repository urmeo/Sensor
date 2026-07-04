"""Reproduce the derived data files from the raw sensor recordings.

Right now this covers the eye-tracking fixation pipeline, which is fully
reproducible from the shipped raw file:

    data/sed.csv  --detect_fixations-->  data/sed_fix.csv

`detect_fixations` adds the four derived columns (`gaze_diff`, `fixation`,
`fixation_id`, `duration`) and is verified to reproduce the committed
`sed_fix.csv` exactly (see tests/test_derive.py).

Algorithm
---------
- gaze_diff : Euclidean distance between consecutive gaze-direction unit
  vectors (`gazeDir.{x,y,z}`); undefined (NaN) on the first row.
- fixation  : True when gaze_diff < THRESHOLD (0.01), i.e. the gaze barely
  moved between samples; NaN gaze_diff counts as not-a-fixation.
- fixation_id : a 1-based segment counter that increments at every transition
  between fixation and non-fixation, so each contiguous run (of either kind)
  gets its own id.
- duration  : for each fixation run, the elapsed time (last - first reltime)
  of that run, broadcast to every row in the run; NaN on non-fixation rows.

Not covered
-----------
`HRV.csv` (per-question pupil/blink summaries) is NOT reproduced here: it spans
three sessions but only Session 1 raw data is shipped, and its timestamps sit on
a different clock offset from `sed.csv` (the notebook aligns them with a fitted
offset). Blink-rate extraction from eye-openness is also undocumented upstream.
Reproducing it would be guesswork, so it is intentionally left out rather than
shipped as an unverifiable derivation.

Run `python scripts/derive.py --check` to confirm the pipeline still matches the
committed file.
"""

import sys

import numpy as np

import sensor_data as sd

THRESHOLD = 0.01
DERIVED_COLUMNS = ["gaze_diff", "fixation", "fixation_id", "duration"]


def detect_fixations(sed, threshold=THRESHOLD):
    """Add fixation columns to a raw `sed` frame and return the `sed_fix` frame."""
    df = sed.copy()

    vectors = df[["gazeDir.x", "gazeDir.y", "gazeDir.z"]].to_numpy()
    step = np.sqrt(((vectors[1:] - vectors[:-1]) ** 2).sum(axis=1))
    df["gaze_diff"] = np.concatenate([[np.nan], step])

    df["fixation"] = df["gaze_diff"] < threshold

    transition = df["fixation"].ne(df["fixation"].shift()).to_numpy()
    transition[0] = False
    df["fixation_id"] = np.cumsum(transition) + 1

    reltime = df.groupby("fixation_id")["reltime"]
    span = reltime.transform("last") - reltime.transform("first")
    df["duration"] = span.where(df["fixation"])

    return df


def check(base=None):
    """Return True if detect_fixations(sed) reproduces the committed sed_fix."""
    derived = detect_fixations(sd.load("sed", base))
    committed = sd.load("sed_fix", base)
    if list(derived.columns) != list(committed.columns):
        return False
    for col in committed.columns:
        a, b = derived[col], committed[col]
        if col in ("gaze_diff", "duration"):
            ok = np.allclose(a.to_numpy(), b.to_numpy(), rtol=0, atol=1e-9, equal_nan=True)
        else:
            ok = a.equals(b)
        if not ok:
            return False
    return True


if __name__ == "__main__":
    if "--check" in sys.argv:
        print("reproduces sed_fix.csv exactly:", check())
    else:
        out = detect_fixations(sd.load("sed"))
        dest = sd.DATA_DIR / "sed_fix.csv"
        out.to_csv(dest, index=False)
        print(f"wrote {dest} ({len(out)} rows)")
