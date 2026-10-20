"""Download the UCI Diabetes 130-US Hospitals dataset into data/raw/."""

import hashlib
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = (
    "https://archive.ics.uci.edu/static/public/296/"
    "diabetes+130-us+hospitals+for+years+1999-2008.zip"
)
RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
ZIP_PATH = RAW_DIR / "diabetes_130_us_hospitals.zip"
CHECKSUM_PATH = RAW_DIR / "SHA256SUMS.txt"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, dest: Path) -> None:
    print(f"Downloading {url}")
    urllib.request.urlretrieve(url, dest)


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if not ZIP_PATH.exists():
        download(URL, ZIP_PATH)
    else:
        print(f"{ZIP_PATH} already exists, skipping download")

    checksum = sha256_of(ZIP_PATH)
    print(f"SHA-256: {checksum}")
    CHECKSUM_PATH.write_text(f"{checksum}  {ZIP_PATH.name}\n")

    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        print(f"Extracting: {names}")
        zf.extractall(RAW_DIR)

    for name in ("diabetic_data.csv", "IDS_mapping.csv"):
        path = RAW_DIR / name
        if not path.exists():
            print(f"WARNING: expected file not found after extraction: {path}", file=sys.stderr)
        else:
            print(f"OK: {path} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
