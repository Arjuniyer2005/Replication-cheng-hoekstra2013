"""Download the public Castle Doctrine dataset for the replication project."""

from pathlib import Path
from urllib.request import urlopen

DATA_URL = "https://raw.githubusercontent.com/scunning1975/mixtape/master/castle.dta"
DATA_PATH = Path(__file__).resolve().parent / "data" / "castle.dta"


def main():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    if DATA_PATH.is_file() and DATA_PATH.stat().st_size > 0:
        print(f"Dataset already exists: {DATA_PATH}")
        return

    try:
        with urlopen(DATA_URL, timeout=30) as response:
            content = response.read()
        if not content:
            raise ValueError("Downloaded dataset is empty")
        DATA_PATH.write_bytes(content)
    except Exception:
        DATA_PATH.unlink(missing_ok=True)
        raise

    print(f"Downloaded dataset to {DATA_PATH} ({len(content):,} bytes)")


if __name__ == "__main__":
    main()
