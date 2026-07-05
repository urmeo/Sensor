# Data & Ethics Statement

This repository includes sample human physiological and psychometric data (heart
rate, inter-beat intervals, eye-tracking (pupil/blink) metrics, and psychometric
test results) recorded
from a single consenting participant during anxiety-detection sensor evaluation.
Because it includes health-related measurements, it is handled as
special-category personal data.

## Legal basis and data protection
The data were collected, and are shared, in compliance with the EU General Data
Protection Regulation (Regulation (EU) 2016/679, "GDPR") and the French Data
Protection Act (Loi n° 78-17 du 6 janvier 1978, "Informatique et Libertés", as
amended). No separate institutional review board (IRB) number applies;
governance rests on the data-protection framework above together with the
participant's explicit consent.

- Lawful basis: the participant's explicit, informed consent (GDPR Art. 6(1)(a)
  and, for special-category health data, Art. 9(2)(a)).
- Principles applied: data minimisation, purpose limitation, and release of only
  pseudonymised records (GDPR Art. 5).

## Informed consent
The participant gave written informed consent, including explicit consent for
the pseudonymised sample data to be shared openly for research and educational
purposes, and was free to withdraw at any time without penalty.

## De-identification
- No direct identifiers are included (no names, contact details, dates of birth,
  or device identifiers).
- With a single participant, the released files contain no identifier or
  pseudonymous code column; records can be linked back to the participant only
  through consent documentation held separately by the data controller (the
  pseudonymisation key under GDPR Art. 4(5)).
- Recording timestamps are retained for time-series analysis; they carry no
  location or identity information and present low re-identification risk, and
  can be shifted to relative session time by running `scripts/shift_time.py`,
which writes a timestamp-free (relative-time) copy to `data/relative/`.

## Data-subject rights
The participant retains their GDPR rights of access, rectification, erasure, and
objection, exercisable via the contact below.

## Permitted use
Released under the repository's license for **research and educational
purposes** only. Do not attempt to re-identify the participant.

## Contact
Data controller / questions about this statement: Urme Bose — urme.bose1@gmail.com.
