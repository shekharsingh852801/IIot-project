from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.sample_data import make_sample_data


OUTPUT_PATH = ROOT / "data" / "online_learning_engagement.csv"


def main() -> None:
    data = make_sample_data()
    data.to_csv(OUTPUT_PATH, index=False)
    print(f"Generated {len(data):,} synthetic learner-module rows: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
