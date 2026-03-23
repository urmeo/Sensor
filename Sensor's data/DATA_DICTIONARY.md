# Data Dictionary

Column-level reference for every CSV in this folder. All files come from a single participant recorded across three sessions (2024-06-13, 2024-06-20, 2024-06-24). The raw sensor files (`hr.csv`, `ibi.csv`, `sed.csv`, `sed_fix.csv`) only cover Session 1 (June 13). `HRV.csv` covers all three.

---

## HRV.csv

Per-question biometric summary with eye tracking metrics aggregated for each psychometric question. Despite the filename, this file does **not** contain raw HRV data — it stores pupil dilation and blink rate summaries computed from the eye tracker during each question interval.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `Test` | string | `Test 01`, `Test 02`, `Test 03` | Session identifier (01 = June 13, 02 = June 20, 03 = June 24) |
| `Type` | string | `HADS`, `STAI-S`, `STAI-T`, `BFI`, `FQ` | Psychometric test being administered |
| `Start Time` | datetime | — | Timestamp when the question appeared on screen |
| `End Time` | datetime | — | Timestamp when the participant answered |
| `Score` | int | 0–6 | Numeric score for that question |
| `Average Pupil Dilation` | float | 1.22–3.13 | Mean pupil diameter (mm) during the question interval |
| `Average Left Blink Rate` | float | 0.0–254.05 | Left-eye blink rate (blinks/min) during the interval |
| `Average Right Blink Rate` | float | 0.0–458.43 | Right-eye blink rate (blinks/min) during the interval |
| `Pupil Dilation Increase` | string | `Yes` / `No` | Whether dilation increased relative to baseline |
| `Left Blink Rate Increase` | string | `Yes` / `No` | Whether left blink rate increased relative to baseline |
| `Right Blink Rate Increase` | string | `Yes` / `No` | Whether right blink rate increased relative to baseline |

**Notes:**
- 264 data rows: 88 questions × 3 sessions.
- Test 01 shows `Pupil Dilation Increase = Yes` for all 88 questions, while Tests 02–03 are mostly `No` — likely a baseline calibration or lighting difference across sessions.
- Some blink rate values exceed 400 blinks/min. Normal resting blink rate is ~15–20 blinks/min. The extreme values may be artifacts from short measurement windows or signal noise.

---

## hr.csv

Continuous heart rate readings from chest-strap sensors, sampled at ~2 Hz per sensor (~4 Hz combined).

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `reltime` | float | 0.001–534.892 | Seconds since recording start |
| `datetime` | datetime | — | Absolute timestamp (ms precision) |
| `iSensor` | int | 0–5 | Sensor index (see mapping below) |
| `confidence` | float | 0.0 or 1.0 | Signal quality — 1.0 = valid reading, 0.0 = no signal |
| `heart_rate` | float | 0.0–73.0 | Heart rate in BPM. Zero means no lock. |

**Sensor mapping:**
- `iSensor 3` and `iSensor 5` are the two active heart rate channels (likely Polar H10+ and Moofit HW401).
- `iSensor 0, 1, 2, 4` each have a single initialization row at `reltime = 0.001` with `confidence = 0.0` — these channels did not produce valid data.

**Notes:**
- 4,032 data rows spanning ~535 seconds (~8 min 55 sec).
- Heart rate stays in a narrow 59–73 BPM range, consistent with a seated participant answering questionnaires.

---

## ibi.csv

Beat-to-beat inter-beat intervals from the chest-strap sensors. These are the raw intervals between successive heartbeats, used to derive HRV metrics like RMSSD and SDNN.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `reltime` | float | 0.001–534.892 | Seconds since recording start |
| `datetime` | datetime | — | Absolute timestamp (ms precision) |
| `iSensor` | int | 0–5 | Sensor index (same mapping as `hr.csv`) |
| `ibi` | int | 0–1093 | Inter-beat interval in milliseconds. Zero = initialization row. |

**Notes:**
- 2,394 data rows. Sensor 5 contributed 1,809 readings, sensor 3 contributed 581.
- Non-zero IBI values range from 478–1,093 ms, corresponding to ~55–125 BPM.
- Typical values cluster around 800–1,000 ms (60–75 BPM), consistent with `hr.csv`.

---

## Psychometric_Test_Results.csv

Question-level responses from Session 1 (June 13 only).

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `Test` | string | `HADS`, `STAI-S`, `STAI-T`, `BFI`, `FQ` | Psychometric test name |
| `Question` | string | — | Full question text |
| `Answer` | string | — | Selected answer (text) |
| `Score` | int | 1–6 | Numeric score for that question |
| `Time(s)` | float | 2.016–22.737 | Response time in seconds |
| `Question Start Time` | ISO datetime | — | When the question was displayed |
| `Question Answer Time` | ISO datetime | — | When the participant submitted their answer |

**Notes:**
- 88 rows: HADS (14), STAI-S (20), STAI-T (20), BFI (10), FQ (24).
- Only Session 1 data. Sessions 2 and 3 questionnaire data is not in this folder.
- 7 columns including Score.

---

## sed.csv

Raw eye tracking data from the Pupil Labs Core, recorded at ~60 Hz. The "sed" filename stands for Smart Eye Data.

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `reltime` | float | 0.001–534.979 | Seconds since recording start |
| `datetime` | datetime | — | Absolute timestamp |
| `iSensor` | int | always 0 | Eye tracker sensor index |
| `headPos.x`, `headPos.y`, `headPos.z` | float | all 0.0 | Head position in 3D space (not tracked in this setup) |
| `headPosQ` | float | 0.0 | Head position quality |
| `headYaw`, `headPitch`, `headRoll` | float | all 0.0 | Head rotation angles (not tracked) |
| `headRotQ` | float | 0.0 | Head rotation quality |
| `gazeSrc.x`, `gazeSrc.y`, `gazeSrc.z` | float | ~−0.02 to 0.01 | Gaze origin point (eye position in tracker coordinates) |
| `gazeDir.x`, `gazeDir.y`, `gazeDir.z` | float | ~−0.3 to 1.0 | Gaze direction unit vector |
| `gazeQ` | float | 0.11–1.0 | Gaze tracking quality (1.0 = best) |
| `leftEyeOpen` | float | 0.0–10.0 | Left eye openness (0 = closed, 10 = fully open) |
| `leftEyeOpenQ` | float | 0.0–1.0 | Left eye openness quality |
| `rightEyeOpen` | float | 0.0–10.0 | Right eye openness |
| `rightEyeOpenQ` | float | 0.0–1.0 | Right eye openness quality |
| `pupil` | float | 0.0–3.88 | Pupil diameter in mm |
| `pupilQ` | float | 0.0–1.0 | Pupil measurement quality |

**Notes:**
- 34,171 data rows at ~60 Hz over ~535 seconds.
- Head position and rotation are all zeros — either the setup used a fixed head rest or head tracking was disabled.
- Pupil diameter typically falls in the 2.0–3.5 mm range. Values of 0.0 indicate tracking loss.

---

## sed_fix.csv

Post-processed version of `sed.csv` with fixation detection applied. Contains all the same raw columns plus four derived columns for gaze analysis.

All columns from `sed.csv` carry over, plus:

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `gaze_diff` | float | 0.0–1.583 | Euclidean distance between consecutive gaze direction vectors — a saccade/movement metric |
| `fixation` | bool | `True` / `False` | Whether the gaze point is part of a fixation (`True`) or a saccade (`False`) |
| `fixation_id` | int | 1–4958 | Sequential ID for each detected fixation |
| `duration` | float | 0.0–1.938 | Fixation duration in seconds (only populated when `fixation = True`) |

**Notes:**
- Same 34,171 rows as `sed.csv`.
- 88.6% of samples are classified as fixations (30,289 of 34,171).
- 4,958 distinct fixation events were detected.
- Fixation durations range from near-zero to ~1.94 seconds.

---

## Cross-File Relationships

All sensor files share the same recording window: **2024-06-13, 11:30:10 – 11:39:05** (~535 seconds, Session 1 only).

```
Psychometric_Test_Results.csv   (question-level answers, Session 1)
        ↕ aligned timestamps
HRV.csv                         (per-question biometric summaries, Sessions 1–3)
        ↑ aggregated from
sed.csv / sed_fix.csv           (~60 Hz eye tracking)
hr.csv                          (~4 Hz heart rate)
ibi.csv                         (beat-to-beat intervals)
```

**Sensor index (`iSensor`) mapping across files:**

| iSensor | Device | Files |
|---------|--------|-------|
| 0 | Eye tracker (Pupil Labs Core) | sed.csv, sed_fix.csv |
| 3 | Heart rate sensor (likely Polar H10+ or Moofit) | hr.csv, ibi.csv |
| 5 | Heart rate sensor (likely Polar H10+ or Moofit) | hr.csv, ibi.csv |
| 1, 2, 4 | Unused / no valid data | initialization rows only |
