# CognoDB Cloud Benchmark

A reproducible benchmark for evaluating graph query performance on CognoDB Cloud using the Stanford POKEC social-network dataset.

## Dataset

- Dataset: Stanford POKEC
- Nodes: ~243K
- Relationships: ~672K

## Workloads

The benchmark measures:

1. Point lookup
2. One-hop traversal
3. Two-hop traversal
4. Aggregation

Each workload uses:

- 3 warm-up runs
- 20 measured runs
- Average, median, P95 and P99 latency

## Latest Results

| Workload | Average | Median | P95 | P99 |
|---|---:|---:|---:|---:|
| Point lookup | 368.26 ms | 350.84 ms | 540.93 ms | 590.30 ms |
| One-hop traversal | 446.52 ms | 452.55 ms | 619.72 ms | 714.13 ms |
| Two-hop traversal | 393.58 ms | 275.22 ms | 916.26 ms | 1661.20 ms |
| Aggregation | 5175.77 ms | 5179.96 ms | 6038.64 ms | 6559.59 ms |

All workloads completed with **20/20 successful iterations and 0 failures**.


## Project Structure

```text
benchmark/
├── datasets/
├── workloads/
└── analysis/

results/
├── raw/
└── charts/
```

## Methodology

The benchmark was designed to measure query latency for representative graph workloads on CognoDB Cloud using the Stanford POKEC dataset.

For each workload:

- 3 warm-up runs were executed.
- 20 measured iterations were executed.
- Failed iterations were recorded separately.
- Latency was measured in milliseconds.
- Average, median, P95 and P99 latency were calculated.
Once you've done that, just tell me **"done"** and I'll give you the next single step.



=======
>>>>>>> e5b14b3 (Improve README documentation)
