# Sensor

Review of **10 sensors** and **2 software platforms** used in our anxiety detection research — eye tracking, heart rate, skin conductance, video, and motion capture. Includes specs, comparisons, and sample data.

---

## Sensors & Tools

### Eye Tracking

<table>
  <tr>
    <td align="center" valign="top" width="33%">
      <br>
      <img src="images/pupil-labs-core.jpg" width="250" alt="Pupil Labs Core"><br>
      <b>Pupil Labs Core</b><br>
      <sub>Head-mounted eye tracker</sub><br>
      <sub>Dark pupil + 3D model · 5-point calibration</sub><br>
      <sub>1080p @30 Hz · 720p @60 Hz · 480p @120 Hz</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <br>
      <img src="images/tobii-pro-glasses-3.jpg" width="250" alt="Tobii Pro Glasses 3"><br>
      <b>Tobii Pro Glasses 3</b><br>
      <sub>Wearable eye tracker</sub><br>
      <sub>100 Hz gaze sampling</sub><br>
      <sub>&nbsp;</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <br>
      <img src="images/smi-eye-tracking.jpg" width="250" alt="SMI Eye Tracking"><br>
      <b>SMI Eye Tracking Systems</b><br>
      <sub>Research-grade eye tracker</sub><br>
      <sub>60 Hz sampling</sub><br>
      <sub>&nbsp;</sub>
    </td>
  </tr>
</table>

---

### Cardiac & Electrodermal

<table>
  <tr>
    <td align="center" valign="top" width="25%">
      <br>
      <img src="images/polar-h10.jpg" width="200" alt="Polar H10+"><br>
      <b>Polar H10+</b><br>
      <sub>Chest strap — HR, HRV, IBI</sub><br>
      <sub>64 MHz microprocessor · ECG sensor</sub>
    </td>
    <td align="center" valign="top" width="25%">
      <br>
      <img src="images/moofit-hw401.jpg" width="200" alt="Moofit HW401"><br>
      <b>Moofit HW401</b><br>
      <sub>Wearable heart rate monitor</sub><br>
      <sub>64 MHz microprocessor · ECG sensor</sub>
    </td>
    <td align="center" valign="top" width="25%">
      <br>
      <img src="images/empatica-e4.jpg" width="200" alt="Empatica E4"><br>
      <b>Empatica E4 Wristband</b><br>
      <sub>Wrist wearable — EDA, BVP, temp, accel</sub><br>
      <sub>Multi-sensor (EDA + BVP + temp + accel)</sub>
    </td>
    <td align="center" valign="top" width="25%">
      <br>
      <img src="images/tea-captiv-t-sens-gsr.jpg" width="200" alt="TEA CAPTIV T-SENS GSR"><br>
      <b>TEA CAPTIV T-SENS GSR</b><br>
      <sub>Skin conductance (wireless)</sub><br>
      <sub>32 Hz sampling · 20 g · 8 hr battery</sub>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top" width="25%">
      <br>
      <img src="images/biopac-eda.jpg" width="200" alt="BioPac EDA"><br>
      <b>BioPac EDA Sensors</b><br>
      <sub>Electrodermal activity measurement</sub><br>
      <sub>&nbsp;</sub>
    </td>
    <td></td>
    <td></td>
    <td></td>
  </tr>
</table>

---

### Video & Motion Capture

<table>
  <tr>
    <td align="center" valign="top" width="33%">
      <br>
      <img src="images/axis-p1275.jpg" width="250" alt="AXIS P1275"><br>
      <b>AXIS P1275 Camera</b><br>
      <sub>Network surveillance camera</sub><br>
      <sub>HDTV 1080p · WDR-Forensic capture</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <br>
      <img src="images/axis-p1245.jpg" width="250" alt="AXIS P1245"><br>
      <b>AXIS P1245 Camera</b><br>
      <sub>Compact network camera</sub><br>
      <sub>HDTV 1080p</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <br>
      <img src="images/optitrack-slim-x13.jpg" width="250" alt="OptiTrack Slim X13"><br>
      <b>OptiTrack (Slim X13)</b><br>
      <sub>Motion capture system</sub><br>
      <sub>&nbsp;</sub>
    </td>
  </tr>
</table>

---

### Software

<table>
  <tr>
    <td align="center" valign="top" width="50%">
      <br>
      <img src="images/openface.jpg" width="420" alt="OpenFace Gaze Estimation"><br>
      <b>OpenFace</b><br>
      <sub>Open-source facial analysis</sub><br>
      <sub>Landmark detection · Head pose · Action unit recognition · Gaze estimation</sub>
    </td>
    <td align="center" valign="top" width="50%">
      <br>
      <img src="images/noldus-facereader.jpg" width="420" alt="Noldus FaceReader"><br>
      <b>Noldus FaceReader</b><br>
      <sub>Commercial facial analysis</sub><br>
      <sub>468-point face model · 20 Action Units · 99% accuracy on ADFES</sub>
    </td>
  </tr>
</table>

---

## Experiment Protocol

From `Experiment Scenario.pdf` — a 5-phase, 30-minute session:

| Phase | Duration | Description |
|-------|----------|-------------|
| **1. Interview** | 10 min | Semi-structured demographic interview, informed consent |
| **2. Sensor Setup** | 5 min | Fit Pupil Labs Core, Polar H10+, and Moofit HW401; calibrate |
| **3. Baseline** | — | Reading task to get resting-state measurements |
| **4. Psychometric Testing** | 15 min | HADS, STAI, BFI-10, and FQ on screen while sensors record |
| **5. Debrief** | — | Participant feedback; mental health resources provided if needed |

---

## Anxiety Detection Thresholds

From `Threshold.pdf` — literature-based thresholds used for detecting anxiety:

| Sensor | Measure | Anxiety Threshold | Source |
|--------|---------|-------------------|--------|
| Pupil Labs Core | Fixation duration | < 250 ms | Laeng et al. (2012) |
| Pupil Labs Core | Saccade peak velocity | > 500 deg/s (for ≥ 15° saccades) | Di Stasi et al. (2013); van der Lans et al. (2013) |
| OpenFace | Brow furrowing (AU 4) | ≥ 3.0 on 0–5 intensity scale (FACS C) | Ekman & Friesen (1978); Gavrilescu & Vizireanu (2019) |
| OpenFace | Lip tightening (AU 24) | ≥ 3.0 on 0–5 intensity scale (FACS C) | Ekman & Friesen (1978); Gavrilescu & Vizireanu (2019) |
| TEA GSR | Skin conductance response | > 0.05 µS | Boucsein (1992) |
| Polar H10+ / Moofit | RMSSD | < 50 ms | ESC/NASPE Task Force (1996) |
| Polar H10+ / Moofit | SDNN | < 50 ms | ESC/NASPE Task Force (1996) |

---

## Documentation

| Document | What's in it |
|----------|-------------|
| `List of Sensors.pdf` | Specs and capabilities for each sensor |
| `Sensor Comparison.pdf` | Side-by-side comparison |
| `Sensors (Eye-tracking, HRV, GSR, Camera).pdf` | Overview by measurement type |
| `OpenFace vs Noldus.pdf` | Facial analysis software comparison |
| `Experiment Scenario.pdf` | Experimental protocol |
| `Threshold.pdf` | Anxiety detection thresholds with references |

---

## Sample Data

The `Sensor's data/` folder has CSVs from psychometric testing sessions (2024-06-13 to 2024-06-24). Full column definitions are in the [data dictionary](Sensor's%20data/DATA_DICTIONARY.md).

| File | Rows | Description |
|------|------|-------------|
| `HRV.csv` | 265 | Per-question biometric summary — pupil dilation & blink rates aggregated per question across all 3 sessions. **Note:** despite the filename, this file contains eye tracking metrics, not raw HRV data. See [`DATA_DICTIONARY.md`](Sensor's%20data/DATA_DICTIONARY.md) for column details. |
| `hr.csv` | 4033 | Heart rate from multiple sensors (Polar H10+, Moofit) with confidence scores |
| `ibi.csv` | 2395 | Inter-beat interval series |
| `Psychometric_Test_Results.csv` | 88 | Question-level responses (HADS, STAI-S, STAI-T, FQ, BFI) with timestamps |
| `sed.csv` | 34172 | Raw eye tracking — head position, gaze direction, pupil size, eye openness |
| `sed_fix.csv` | 34172 | Processed eye tracking — adds gaze difference, fixation detection, fixation duration |

---

## Quick Start

See [`analysis/explore_data.ipynb`](analysis/explore_data.ipynb) for a walkthrough that loads each CSV and plots heart rate, pupil dilation, fixation durations, and HRV metrics from the sample session.

---

## What You Can Use This For

- Picking sensors for a multimodal physiology study
- Comparing what each device can actually do
- Designing experiments with multiple concurrent sensors
- Understanding the data formats each platform outputs

---

## Related Repos

- [Multimodal-Multisensor](https://github.com/urme-b/Multimodal-Multisensor) — Longitudinal study using these sensors
- [Multimodal](https://github.com/urme-b/Multimodal) — Analysis of the collected data
- [CalmSense](https://github.com/urme-b/CalmSense) — Stress detection system built on multimodal signals

---

## Tech Stack

Pupil Labs Core · Polar H10+ · Moofit HW401 · TEA CAPTIV T-SENS · Empatica E4 · OpenFace · Noldus FaceReader · OptiTrack · AXIS Cameras

## Topics

Biometric Sensors · Eye Tracking · Heart Rate Variability · Galvanic Skin Response · Electrodermal Activity · Anxiety Detection · Psychometric Testing · Multimodal Sensing · OpenFace · Pupil Labs

## License

[MIT](LICENSE)
