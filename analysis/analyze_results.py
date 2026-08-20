import pandas as pd
from pathlib import Path

results_dir = Path("results/raw")
processed_dir = Path("results/processed")

processed_dir.mkdir(parents=True, exist_ok=True)

files = list(results_dir.glob("*.csv"))

if not files:
    print("No CSV result files found.")
else:
    for file in files:
        df = pd.read_csv(file)

        print(f"\n=== {file.name} ===")
        print(df.describe(include="all"))

        # Save a clean processed version
        output_file = processed_dir / f"{file.stem}_summary.csv"

        summary_columns = [
            "workload",
            "average_ms",
            "median_ms",
            "p95_ms",
            "p99_ms",
            "min_ms",
            "max_ms",
            "avg_records",
            "successful_iterations",
            "failed_iterations",
        ]

        summary = df[summary_columns]

        summary.to_csv(output_file, index=False)

        print(f"\nSaved processed results to: {output_file}")