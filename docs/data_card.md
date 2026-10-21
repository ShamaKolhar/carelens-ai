# Data Card — CareLens AI

## Dataset

**UCI Diabetes 130-US Hospitals for Years 1999–2008**
Clore, J., Cios, K., DeShazo, J., & Strack, B. (2014). *Diabetes 130-US Hospitals for
Years 1999-2008* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5230J

Introductory paper: Strack, B., DeShazo, J. P., Gennings, C., et al. (2014).
*Impact of HbA1c Measurement on Hospital Readmission Rates: Analysis of 70,000
Clinical Database Patient Records*. BioMed Research International.

License: **CC BY 4.0** (attribution required — given above and in the project README).

## Provenance

- Collected from 130 US hospitals and integrated delivery networks, 1999–2008, via the
  Health Facts database (Cerner Corporation).
- Downloaded from the UCI page on 2026-10-19; raw zip SHA-256 recorded in
  `data/raw/SHA256SUMS.txt` (`f82ac129da2ddd2299391ff6fbae3a6a58b3edcf59ac9d7bd480c00fe453112a`).
- Raw files kept immutable in `data/raw/`; all cleaning happens in `data/interim/` →
  `data/processed/`, never in place. See `docs/data_dictionary.md` for per-column detail.
- 101,766 encounters, 50 columns as distributed (47 features + `encounter_id` +
  `patient_nbr` + `readmitted`). Each row is one inpatient encounter for a diabetic
  patient, not one patient — 71,518 unique patients, mean 1.42 encounters/patient,
  23.45% of patients appear more than once.

## Intended use

- A **portfolio / learning project** demonstrating an explainable, patient-grouped,
  fairness-audited, monitored 30-day readmission risk model and a document-grounded
  policy assistant, for entry-level data scientist / applied ML / AI evaluation
  interviews.
- Supports a *hypothetical* care-team prioritization workflow: ranking already-admitted
  diabetic inpatients by estimated 30-day readmission risk so follow-up effort could, in
  principle, be targeted.

## Out of scope / not permitted

- **Not a validated clinical tool.** Never to be presented as, or used for, real patient
  care, real clinical decision-making, or real care-team prioritization. This is stated
  here, and will be restated in the README, the app UI, and the model card.
- Not generalizable beyond the source population: US hospitals, 1999–2008, diabetic
  inpatients only. Clinical practice, coding systems (ICD-9), and patient populations
  have changed materially since 2008.
- Not validated for use outside the US healthcare system.
- The dataset has no encounter dates, so no time-based validation (e.g. "does this model
  still work on next year's patients") is possible — see Limitations.

## Target definition (scope decision)

- `readmitted` is recorded as three classes: `<30`, `>30`, `NO`.
- Binary target `readmitted_30d`: positive = `<30` (11.16% of all 101,766 encounters,
  11.39% of the 99,343 encounters remaining after exclusions below). `>30` and `NO` are
  merged into the negative class.
- Rationale: *action-equivalence* — the hypothetical care-team action is the same whether
  a patient is never readmitted or readmitted after day 30. Modeling three classes would
  add complexity without changing that action. This means the model is explicitly
  **not** trained to distinguish "never readmitted" from "readmitted after 30 days" — a
  deliberate scope choice, documented so it is never mistaken for an oversight.

## Exclusions

Two discharge-disposition groups are excluded from `model_df` before any modeling,
identified via `data/raw/IDS_mapping.csv`:

| Excluded group | `discharge_disposition_id` | Rows | Reason |
|---|---|---|---|
| Expired | 11, 19, 20, 21 | 1,652 | Patient died — cannot be readmitted. Leaving these in would label genuinely critical illness as "low risk" (`readmitted_30d=0`), teaching the model a backwards association. |
| Hospice | 13, 14 | 771 | Patient is alive, but hospice care plans actively avoid further hospitalization regardless of clinical trajectory. Verified empirically, not assumed: hospice rows have a `<30` readmission rate of 5.58% vs. 11.16% overall — a confound, not genuine low risk. |

Net effect: 101,766 → 99,343 rows (−2,423, −2.4%). Positive rate shifts from 11.16% to
11.39% as a direct consequence of removing disproportionately-negative-labeled rows, not
from any adjustment to the target itself.

No other rows are dropped. `weight` (96.9% missing, structural/hospital-level, not
patient-level — see data dictionary) is the only column dropped outright; all other
high-missingness columns are kept with `"?"` relabeled to an explicit `"Missing"`
category rather than imputed or dropped (see data dictionary for the per-column
rationale, including why imputing `race` specifically would be inappropriate).

## Sensitive attributes

| Attribute | Status | Rationale |
|---|---|---|
| `race` | Audit-only, excluded from model features | No identified causal/clinical mechanism linking race itself to readmission risk |
| `gender` | Audit-only, excluded from model features | Candidate mechanism (sex differences in Type 2 diabetes *onset*) does not transfer to readmission risk in an already-diabetic, already-hospitalized cohort |
| `age` | Kept as a model feature, also audited | Established clinical link to comorbidity burden, frailty, polypharmacy (used in real clinical risk scores) |
| `payer_code` | Kept as a model feature (**provisional**), also audited | Plausible genuine signal (insurance/access to follow-up care) but flagged as a likely socioeconomic/race proxy. If the Session 6 fairness audit shows disparate impact consistent with a proxy effect, the model will be retrained without it and both versions documented. |

All four attributes receive the full fairness audit (group recall/FPR/FNR/calibration +
bootstrap confidence intervals, Session 6) regardless of feature-inclusion status —
excluding an attribute from the features does not remove proxy bias carried by
correlated columns ("fairness through unawareness"), so the audit runs either way.

## Known data-quality issues

- Two distinct missing-value encodings in the raw file: the string `"?"` (e.g. `weight`,
  `race`, `medical_specialty`, `payer_code`, `diag_1/2/3`) and literal `None`/`NULL` text
  (`max_glu_serum`, `A1Cresult`, and `IDS_mapping.csv`'s `discharge_disposition_id`
  column). `df.isna()` only catches the second kind — checked explicitly per column
  rather than assumed.
- `gender` has 3 rows coded `Unknown/Invalid` — too small a group to support any fairness
  conclusion; retained rather than dropped, but any group-level fairness result for this
  category must say so explicitly.
- `diag_1/2/3` carry hundreds of distinct ICD-9 codes; no grouping has been applied as of
  this data card — grouping into clinical categories is deferred to Session 3/4 feature
  engineering and must be done on a documented, principled basis (not ad hoc binning).
- `max_glu_serum` and `A1Cresult` are 94.8% / 83.3% missing (test not ordered, not a data
  error). Handling decision (explicit "not tested" category vs. drop vs. something else)
  is **not yet made** — open item for Session 3 preprocessing.
- Two medication columns (`examide`, `citoglipton`) are constant across all 101,766 rows
  — zero variance, no modeling signal as recorded in this dataset.

## Patient-level structure (leakage risk)

71,518 unique patients, 101,766 encounters (99,343 post-exclusion). 23.45% of patients
have more than one encounter. A naive random train/test split would let encounters from
the same patient land in both sets, leaking patient-specific information across the
split and inflating apparent performance. **Patient-grouped splitting
(`GroupShuffleSplit`/`GroupKFold` on `patient_nbr`) is required** — planned for Session 3,
which will also report the naive-vs-grouped score gap directly rather than assert it.

## Limitations

- **Temporal**: 1999–2008 data; coding practices (ICD-9), treatment protocols, and
  hospital discharge practices have changed. Findings do not describe current-day care.
- **Geographic/systemic**: US hospitals only; not generalizable to other health systems.
- **No dates in the data**: encounter order within a patient's multiple visits, and any
  real-world time trend, cannot be reconstructed. No time-based (as opposed to
  patient-grouped) validation is possible, and this is a data limitation, not a
  methodology choice.
- **Encounter-level, not patient-level, unit of analysis**: a model trained on encounters
  implicitly weights frequently-hospitalized patients more heavily in training, which is
  a defensible choice for this use case (predicting risk *for this encounter*) but is
  worth stating explicitly.
- **Proxy risk not fully resolved**: `payer_code`'s status is provisional pending the
  Session 6 fairness audit; `race`/`gender` exclusion from features does not guarantee
  the trained model is free of proxy bias through correlated features.

## Risks of misuse

- Presenting any output of this project as a validated clinical risk score, or using it
  to inform real patient care, insurance, or staffing decisions.
- Treating "accurate on this historical dataset" as evidence the model would be accurate,
  fair, or safe on a current patient population.
- Using group-level fairness metrics from a group with a very small sample size (e.g.
  `gender == "Unknown/Invalid"`, 3 rows) to support a fairness claim.

## Permitted use

Research, learning, and portfolio demonstration, with attribution to Clore, Cios,
DeShazo & Strack (2014) as above, consistent with the CC BY 4.0 license. Any reuse must
carry forward the exclusions, scope decisions, and limitations documented here and in
`docs/data_dictionary.md` — not just the cleaned data itself.
