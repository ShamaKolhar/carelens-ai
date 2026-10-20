#Schema tests for the raw UCI diabetes dataset

import hashlib
from pathlib import Path

import pandas as pd
import pytest

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
DATA_PATH = RAW_DIR / "diabetic_data.csv"
IDS_PATH = RAW_DIR / "IDS_mapping.csv"
CHECKSUM_PATH = RAW_DIR / "SHA256SUMS.txt"

EXPECTED_SHAPE = (101766, 50)
EXPECTED_READMITTED_VALUES = {"NO", ">30", "<30"}


def _raw_files_present() -> bool:
    return DATA_PATH.exists() and IDS_PATH.exists()


pytestmark = pytest.mark.skipif(
    not _raw_files_present(),
    reason="raw data not downloaded; run scripts/download_data.py first",
)


@pytest.fixture(scope="module")
def df():
    return pd.read_csv(DATA_PATH)


def test_zip_checksum_recorded():
    assert CHECKSUM_PATH.exists()
    recorded = CHECKSUM_PATH.read_text().split()[0]
    assert len(recorded) == 64


EXPECTED_DIABETIC_DATA_SHA256 = (
    "0689e7ec031237dc63031b938805c48377748761a3b26acab621567afa24df97"
)


def test_diabetic_data_checksum_matches_recorded_value():
    digest = hashlib.sha256()
    with open(DATA_PATH, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    assert digest.hexdigest() == EXPECTED_DIABETIC_DATA_SHA256


def test_shape(df):
    assert df.shape == EXPECTED_SHAPE


def test_expected_columns_present(df):
    for col in ("encounter_id", "patient_nbr", "readmitted", "weight", "race"):
        assert col in df.columns


def test_readmitted_target_values(df):
    assert set(df["readmitted"].unique()) == EXPECTED_READMITTED_VALUES


def test_patient_nbr_has_repeat_encounters(df):
    counts = df["patient_nbr"].value_counts()
    assert counts.max() > 1


def test_ids_mapping_has_expired_discharge_dispositions():
    import io

    with open(IDS_PATH) as f:
        lines = f.readlines()

    start = lines.index("discharge_disposition_id,description\n")
    end = lines[start:].index(",\n")
    section = pd.read_csv(io.StringIO("".join(lines[start : start + end])))

    expired_ids = section[section["description"].str.contains("Expired")][
        "discharge_disposition_id"
    ].tolist()
    assert expired_ids == [11, 19, 20, 21]
