# Data Dictionary — CareLens AI

Source: UCI *Diabetes 130-US Hospitals for Years 1999-2008* dataset (Clore, Cios,
DeShazo & Strack, 2014, CC BY 4.0). Column descriptions are drawn from the
dataset's UCI documentation and the accompanying Strack et al. (2014) paper.
`dtype`, `n_unique`, and `sample` are computed directly from `data/raw/diabetic_data.csv`
(101,766 rows x 50 columns) — see `notebooks/01_initial_inspection.py` and
`notebooks/02_eda_data_quality.py`.

Columns are grouped by role rather than listed in raw file order.

## Identifiers

| Column | dtype | n_unique | Description | Notes |
|---|---|---|---|---|
| `encounter_id` | int64 | 101,766 | Unique ID per hospital encounter (row) | One per row; not a feature |
| `patient_nbr` | int64 | 71,518 | Unique ID per patient; a patient can have multiple encounters | Drives patient-grouped split (Session 3) — mean 1.42 encounters/patient, 23.45% of patients have >1 encounter |

## Demographics (sensitive attributes)

| Column | dtype | n_unique | Description | Notes |
|---|---|---|---|---|
| `race` | object | 6 | Patient race, self-reported at registration | 2,273 (2.2%) `"?"` relabeled `"Missing"`. **Audit-only** — excluded from model features (Session 2 decision, Section 3 of `CLAUDE.md`) |
| `gender` | object | 3 | Patient gender | `Female` 54,708; `Male` 47,055; `Unknown/Invalid` 3 (negligible, too small for any audit conclusion). **Audit-only** — excluded from model features |
| `age` | object | 10 | Age in 10-year bins, e.g. `[70-80)` | Ordinal-like string bins, not a raw integer. **Kept as a model feature** — established clinical link to comorbidity/frailty; also audited for fairness |
| `weight` | object | 10 | Patient weight in 25kg-wide bins when recorded, e.g. `[75-100)` (9 real bins + `"?"`) | **Dropped entirely** (96.9% `"?"`, structural/hospital-level missingness, not patient-level — Session 2 decision) |

## Admission / visit details

`admission_type_id`, `discharge_disposition_id`, and `admission_source_id` are integer
codes whose meanings are *not* self-explanatory from `diabetic_data.csv` alone — they're
defined in `data/raw/IDS_mapping.csv`, a separate lookup file with 3 stacked tables.

| Column | dtype | n_unique | Description | Notes |
|---|---|---|---|---|
| `admission_type_id` | int64 | 8 | Coded type of admission (e.g. 1=Emergency, 2=Urgent, 3=Elective, 4=Newborn, 7=Trauma Center; others are "Not Available"/"Not Mapped"/unlabeled) | Meanings from `IDS_mapping.csv` |
| `discharge_disposition_id` | int64 | 26 | Coded discharge destination (e.g. 1=Discharged to home, 3=Discharged to SNF, 6=Home with home health service) | Meanings from `IDS_mapping.csv`. IDs **11, 19, 20, 21** = Expired; IDs **13, 14** = Hospice — both **excluded from `model_df`** (Session 2 decision, label-contamination rationale in Section 3/11 of `CLAUDE.md`) |
| `admission_source_id` | int64 | 17 | Coded source the patient was admitted from (e.g. 1=Physician Referral, 7=Emergency Room, 4=Transfer from a hospital) | Meanings from `IDS_mapping.csv` |
| `time_in_hospital` | int64 | 14 | Length of stay in days (integer, 1–14) | Numeric, no missing values |
| `payer_code` | object | 18 | Coded insurance/payment source (e.g. `MC`=Medicare, `HM`=HMO, `BC`=Blue Cross, `MD`=Medicaid) | 40,256 (39.6%) `"?"` relabeled `"Missing"`. **Kept as a model feature (provisional)** — flagged as a socioeconomic/race proxy; revisit after Session 6 fairness audit |
| `medical_specialty` | object | 73 | Specialty of the admitting physician (e.g. `InternalMedicine`, `Emergency/Trauma`, `Cardiology`) | 49,949 (49.1%) `"?"` relabeled `"Missing"`. High cardinality with a long rare-value tail — will need grouping into an `Other` bucket before encoding (Session 3/4) |

## Utilization counts

All numeric, no missing values. `number_inpatient` (prior inpatient admissions) is the
single strongest prior-utilization signal for readmission risk reported in the
Strack et al. (2014) paper and the wider readmission-risk literature.

| Column | dtype | range | mean | Description | Notes |
|---|---|---|---|---|---|
| `num_lab_procedures` | int64 | 1–132 | 43.1 | Number of lab tests performed during this encounter | |
| `num_procedures` | int64 | 0–6 | 1.34 | Number of non-lab procedures performed during this encounter | |
| `num_medications` | int64 | 1–81 | 16.0 | Number of distinct generic medications administered during this encounter | |
| `number_outpatient` | int64 | 0–42 | 0.37 | Outpatient visits by this patient in the year preceding this encounter | Heavily right-skewed (most patients: 0) |
| `number_emergency` | int64 | 0–76 | 0.20 | Emergency-department visits in the year preceding this encounter | Heavily right-skewed (most patients: 0) |
| `number_inpatient` | int64 | 0–21 | 0.64 | Inpatient admissions in the year preceding this encounter | Strongest known prior-utilization predictor of readmission |
| `number_diagnoses` | int64 | 1–16 | 7.42 | Number of diagnoses entered into the system for this encounter | |

## Diagnosis and lab fields

| Column | dtype | n_unique (incl. `"?"`) | Description | Notes |
|---|---|---|---|---|
| `diag_1` | object | 717 | Primary diagnosis, ICD-9 code | 21 (0.02%) `"?"` relabeled `"Missing"`. Hundreds of distinct codes — grouping into clinical categories (e.g. circulatory, diabetes, respiratory) is deferred to feature engineering (Session 3/4); no grouping applied yet |
| `diag_2` | object | 749 | Secondary diagnosis, ICD-9 code | 358 (0.35%) `"?"` → `"Missing"`. Same grouping note as `diag_1` |
| `diag_3` | object | 790 | Additional secondary diagnosis, ICD-9 code | 1,423 (1.4%) `"?"` → `"Missing"`. Same grouping note as `diag_1` |
| `max_glu_serum` | object | 4 | Max glucose-serum test result during the encounter: `Norm`, `>200`, `>300`, or missing | 96,420 (94.8%) missing via **literal `None`**, not `"?"` — missing because the test wasn't ordered, not a data-entry gap. Relabeling/handling decision **not yet made** — open item for Session 3 preprocessing |
| `A1Cresult` | object | 4 | HbA1c test result during the encounter: `>8`, `Norm`, `>7`, or missing | 84,748 (83.3%) missing via **literal `None`**, same reasoning as `max_glu_serum`. Handling decision **open**, Session 3 |

## Medications (23 columns, shared structure)

Each column records the dosage-change action for one diabetes drug (or drug combination)
during the encounter, with the same 2–4 category values across all 23 columns:
`No` (not prescribed), `Steady` (unchanged), `Up`, `Down`. Exact category sets observed:

| Columns | Categories observed |
|---|---|
| `insulin`, `metformin`, `glipizide`, `glyburide`, `glimepiride`, `pioglitazone`, `rosiglitazone`, `repaglinide`, `nateglinide`, `chlorpropamide`, `acarbose`, `glyburide-metformin` | `No`, `Steady`, `Up`, `Down` (full set) |
| `miglitol`, `tolazamide` | `No`, `Steady`, `Up` (no `Down` observed) |
| `acetohexamide`, `tolbutamide`, `troglitazone`, `glipizide-metformin`, `glimepiride-pioglitazone`, `metformin-rosiglitazone`, `metformin-pioglitazone` | `No`, `Steady` only — near-constant (1–38 non-`"No"` rows out of 101,766) |
| `examide`, `citoglipton` | `No` only — **constant, zero variance**, no modeling signal. Flagged here; dropping is a Session 3/4 action, not applied yet |

`insulin` has by far the most balanced distribution (`No` 46.6%, `Steady` 30.3%, `Down` 12.0%,
`Up` 11.1%) and is the most clinically central of the 23 — dosage changes during an inpatient
stay plausibly reflect acute glycemic instability.

| Column | dtype | n_unique | Description | Notes |
|---|---|---|---|---|
| `change` | object | 2 | Whether *any* diabetes medication's dosage changed during the encounter | `No` 53.8% / `Ch` 46.2%. No missing values |
| `diabetesMed` | object | 2 | Whether any diabetes medication was prescribed at all | `Yes` 77.0% / `No` 23.0%. No missing values |

## Target

| Column | dtype | n_unique | Description | Notes |
|---|---|---|---|---|
| `readmitted` | object | 3 | Raw readmission outcome as recorded by the hospital | `NO` 53.91% (54,864), `>30` 34.93% (35,545), `<30` 11.16% (11,357). No missing values |
| `readmitted_30d` | int64 (derived) | 2 | Binary target: 1 if `readmitted == "<30"`, else 0 | Derived column, not in the raw file. `>30` and `NO` merged into 0 on an action-equivalence rationale (Session 2 decision, Section 3/11 of `CLAUDE.md`). Computed on `model_df` (post-exclusion): positive rate 11.39% vs. 11.16% pre-exclusion |
