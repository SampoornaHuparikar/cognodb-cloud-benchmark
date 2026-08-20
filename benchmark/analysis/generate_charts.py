import os
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================
# PATHS
# ==========================================

INPUT_FILE = "results/raw/cognodb_pokec_results.csv"
OUTPUT_DIR = "results/charts"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==========================================
# LOAD RESULTS
# ==========================================

df = pd.read_csv(INPUT_FILE)

print("Loaded benchmark results:")
print(df)
print()


# ==========================================
# CHART 1 — AVERAGE LATENCY
# ==========================================

plt.figure(figsize=(10, 6))

plt.bar(
    df["workload"],
    df["average_ms"]
)

plt.title("CognoDB POKEC Benchmark - Average Latency")
plt.xlabel("Workload")
plt.ylabel("Average Latency (ms)")

plt.xticks(
    rotation=20,
    ha="right"
)

plt.tight_layout()

average_file = os.path.join(
    OUTPUT_DIR,
    "average_latency.png"
)

plt.savefig(average_file, dpi=200)

plt.close()

print(
    f"Created: {average_file}"
)


# ==========================================
# CHART 2 — MEDIAN vs P95
# ==========================================

plt.figure(figsize=(10, 6))

x = range(len(df))

plt.bar(
    [i - 0.2 for i in x],
    df["median_ms"],
    width=0.4,
    label="Median"
)

plt.bar(
    [i + 0.2 for i in x],
    df["p95_ms"],
    width=0.4,
    label="P95"
)

plt.xticks(
    list(x),
    df["workload"],
    rotation=20,
    ha="right"
)

plt.title("CognoDB POKEC Benchmark - Median vs P95")
plt.xlabel("Workload")
plt.ylabel("Latency (ms)")
plt.legend()

plt.tight_layout()

percentile_file = os.path.join(
    OUTPUT_DIR,
    "median_vs_p95.png"
)

plt.savefig(
    percentile_file,
    dpi=200
)

plt.close()

print(
    f"Created: {percentile_file}"
)


# ==========================================
# CHART 3 — LATENCY DISTRIBUTION
# ==========================================

plt.figure(figsize=(10, 6))

plt.bar(
    df["workload"],
    df["min_ms"],
    label="Minimum"
)

plt.bar(
    df["workload"],
    df["max_ms"],
    bottom=df["min_ms"],
    label="Maximum range"
)

plt.title("CognoDB POKEC Benchmark - Latency Range")
plt.xlabel("Workload")
plt.ylabel("Latency (ms)")

plt.xticks(
    rotation=20,
    ha="right"
)

plt.legend()

plt.tight_layout()

range_file = os.path.join(
    OUTPUT_DIR,
    "latency_range.png"
)

plt.savefig(
    range_file,
    dpi=200
)

plt.close()

print(
    f"Created: {range_file}"
)


# ==========================================
# DONE
# ==========================================

print()
print("==========================================")
print("Chart generation complete!")
print("==========================================")