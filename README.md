# CareLens AI

Explainable 30-day hospital readmission risk, responsible AI evaluation, data-quality
monitoring and a document-grounded policy assistant — built on the UCI
*Diabetes 130-US Hospitals (1999-2008)* dataset.

**This is a portfolio / learning project, not a validated clinical tool.**

## Status

Work in progress - repo setup + EDA

## Setup

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -e .
pip install -r requirements.txt
```

## Data

Raw data is not committed. Download and verify it with:

```bash
python scripts/download_data.py
```

This fetches the UCI zip, records its SHA-256 checksum, and extracts
`diabetic_data.csv` and `IDS_mapping.csv` into `data/raw/`.

Source: Clore, J., Cios, K., DeShazo, J., & Strack, B. (2014). *Diabetes 130-US
Hospitals for Years 1999-2008* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5230J — License: CC BY 4.0.
