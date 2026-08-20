import pandas as pd
from pathlib import Path

results_dir = Path("results/raw")

files = list(results_dir.glob("*.csv"))

if not files:
    print("No CSV result files found.")
else:
    for file in files:
        df = pd.read_csv(file)

        print(f"\n=== {file.name} ===")
        print(df.describe(include="all"))