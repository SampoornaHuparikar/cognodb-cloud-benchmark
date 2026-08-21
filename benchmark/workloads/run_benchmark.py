import os
import csv
import math
import time
import statistics
from datetime import datetime

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

ITERATIONS = 20
WARMUP_ITERATIONS = 3
TEST_PERSON_ID = 1

RESULTS_DIR = "results/raw"
os.makedirs(RESULTS_DIR, exist_ok=True)


# ==================================================
# BENCHMARK QUERIES
# ==================================================

QUERIES = {

    # 1. Point lookup
    "point_lookup": """
        MATCH (n:Person {id: $person_id})
        RETURN n.id
    """,

    # 2. One-hop traversal
    "one_hop_traversal": """
        MATCH (n:Person {id: $person_id})-[:KNOWS]->(friend)
        RETURN friend.id
    """,

    # 3. Two-hop traversal
    "two_hop_traversal": """
        MATCH (n:Person {id: $person_id})
              -[:KNOWS]->(:Person)
              -[:KNOWS]->(friend)
        RETURN DISTINCT friend.id
    """,

    # 4. Aggregation
    "aggregation": """
        MATCH (n:Person)-[:KNOWS]->(friend)
        RETURN n.id AS person_id,
               count(friend) AS connections
        ORDER BY connections DESC
        LIMIT 10
    """
}


# ==================================================
# RUN ONE QUERY
# ==================================================

def run_query(session, query, person_id):

    start = time.perf_counter()

    result = session.run(
        query,
        person_id=person_id
    )

    records = list(result)

    end = time.perf_counter()

    latency_ms = (end - start) * 1000

    return latency_ms, len(records)


# ==================================================
# CALCULATE PERCENTILES
# ==================================================

def percentile(sorted_values, percentile):

    index = max(
        0,
        math.ceil(percentile * len(sorted_values)) - 1
    )

    return sorted_values[index]


# ==================================================
# BENCHMARK
# ==================================================

def benchmark():

    print("Connecting to CognoDB...")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
        connection_timeout=30,
        max_connection_lifetime=300,
        max_transaction_retry_time=30
    )

    driver.verify_connectivity()

    print("✅ Connected to CognoDB")
    print()

    results = {}

    with driver.session() as session:

        for name, query in QUERIES.items():

            print("=" * 50)
            print(f"Running: {name}")
            print("=" * 50)

            # ------------------------------------------
            # Warm-up runs
            # ------------------------------------------

            print(
                f"Warm-up runs: {WARMUP_ITERATIONS}"
            )

            for _ in range(WARMUP_ITERATIONS):

                try:

                    run_query(
                        session,
                        query,
                        TEST_PERSON_ID
                    )

                except Exception as error:

                    print(
                        f"⚠️ Warm-up failed: {error}"
                    )

            # ------------------------------------------
            # Measured runs
            # ------------------------------------------

            latencies = []
            record_counts = []

            print(
                f"Measured runs: {ITERATIONS}"
            )

            for iteration in range(ITERATIONS):

                try:

                    latency, records = run_query(
                        session,
                        query,
                        TEST_PERSON_ID
                    )

                    latencies.append(latency)
                    record_counts.append(records)

                except Exception as error:

                    print(
                        f"⚠️ Run {iteration + 1} failed: "
                        f"{error}"
                    )

            # ------------------------------------------
            # No successful runs
            # ------------------------------------------

            if not latencies:

                print(
                    "❌ No successful measurements."
                )

                continue

            # ------------------------------------------
            # Statistics
            # ------------------------------------------

            sorted_latencies = sorted(latencies)

            result_data = {

                "min_ms":
                    min(latencies),

                "avg_ms":
                    statistics.mean(latencies),

                "median_ms":
                    statistics.median(latencies),

                "p95_ms":
                    percentile(
                        sorted_latencies,
                        0.95
                    ),

                "p99_ms":
                    percentile(
                        sorted_latencies,
                        0.99
                    ),

                "max_ms":
                    max(latencies),

                "records":
                    statistics.mean(record_counts),

                "successful_iterations":
                    len(latencies),

                "failed_iterations":
                    ITERATIONS - len(latencies)
            }

            results[name] = result_data

            # ------------------------------------------
            # Display
            # ------------------------------------------

            print()
            print(
                f"Average:  "
                f"{result_data['avg_ms']:.2f} ms"
            )

            print(
                f"Median:   "
                f"{result_data['median_ms']:.2f} ms"
            )

            print(
                f"P95:      "
                f"{result_data['p95_ms']:.2f} ms"
            )

            print(
                f"P99:      "
                f"{result_data['p99_ms']:.2f} ms"
            )

            print(
                f"Min:      "
                f"{result_data['min_ms']:.2f} ms"
            )

            print(
                f"Max:      "
                f"{result_data['max_ms']:.2f} ms"
            )

            print(
                f"Records:  "
                f"{result_data['records']:.2f}"
            )

            print(
                f"Successful: "
                f"{result_data['successful_iterations']}"
            )

            print(
                f"Failed:     "
                f"{result_data['failed_iterations']}"
            )

            print()


    # ==================================================
    # CLOSE CONNECTION
    # ==================================================

    driver.close()


    # ==================================================
    # SAVE CSV
    # ==================================================

    results_file = os.path.join(
        RESULTS_DIR,
        "cognodb_pokec_results.csv"
    )

    timestamp = datetime.now().isoformat()

    with open(
        results_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "workload",
            "average_ms",
            "median_ms",
            "p95_ms",
            "p99_ms",
            "min_ms",
            "max_ms",
            "avg_records",
            "successful_iterations",
            "failed_iterations"
        ])

        for name, result in results.items():

            writer.writerow([
                timestamp,
                name,
                f"{result['avg_ms']:.2f}",
                f"{result['median_ms']:.2f}",
                f"{result['p95_ms']:.2f}",
                f"{result['p99_ms']:.2f}",
                f"{result['min_ms']:.2f}",
                f"{result['max_ms']:.2f}",
                f"{result['records']:.2f}",
                result["successful_iterations"],
                result["failed_iterations"]
            ])


    # ==================================================
    # FINAL SUMMARY
    # ==================================================

    print()
    print("=" * 60)
    print("              BENCHMARK RESULTS")
    print("=" * 60)

    for name, result in results.items():

        print()
        print(name)

        print(
            f"  Average:   "
            f"{result['avg_ms']:.2f} ms"
        )

        print(
            f"  Median:    "
            f"{result['median_ms']:.2f} ms"
        )

        print(
            f"  P95:       "
            f"{result['p95_ms']:.2f} ms"
        )

        print(
            f"  P99:       "
            f"{result['p99_ms']:.2f} ms"
        )

        print(
            f"  Min:       "
            f"{result['min_ms']:.2f} ms"
        )

        print(
            f"  Max:       "
            f"{result['max_ms']:.2f} ms"
        )

        print(
            f"  Records:   "
            f"{result['records']:.2f}"
        )

        print(
            f"  Successful: "
            f"{result['successful_iterations']}"
        )

        print(
            f"  Failed:     "
            f"{result['failed_iterations']}"
        )

    print()
    print(
        f"✅ Results saved to: {results_file}"
    )


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    benchmark()
