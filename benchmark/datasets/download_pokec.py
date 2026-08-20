from pathlib import Path
import urllib.request


DATA_URL = "https://snap.stanford.edu/data/soc-pokec-relationships.txt.gz"

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "data"
OUTPUT_FILE = OUTPUT_DIR / "soc-pokec-relationships.txt.gz"


def download_dataset():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_FILE.exists():
        print(f"Dataset already exists: {OUTPUT_FILE}")
        return

    print("Downloading Pokec relationship dataset...")
    urllib.request.urlretrieve(DATA_URL, OUTPUT_FILE)
    print(f"Downloaded to: {OUTPUT_FILE}")


if __name__ == "__main__":
    download_dataset()