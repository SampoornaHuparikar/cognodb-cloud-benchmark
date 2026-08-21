import os
import gzip
import time
import certifi

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, TransientError

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

DATA_FILE = "data/soc-pokec-relationships.txt.gz"

BATCH_SIZE = 500
MAX_RETRIES = 5


def create_driver():
    return GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
        max_connection_lifetime=300,
        connection_timeout=30,
        max_transaction_retry_time=30,
    )


def import_batch(driver, batch):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with driver.session() as session:
                session.run(
                    """
                    UNWIND $rows AS row
                    MERGE (a:Person {id: row.source})
                    MERGE (b:Person {id: row.target})
                    MERGE (a)-[:KNOWS]->(b)
                    """,
                    rows=batch,
                ).consume()

            return True

        except (ServiceUnavailable, TransientError, OSError) as error:
            print(
                f"Batch failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {error}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(3)

    return False


def import_pokec():

    print("Connecting to Neo4j...")

    if not URI:
        raise RuntimeError("NEO4J_URI is missing from .env")

    if not USERNAME:
        raise RuntimeError("NEO4J_USERNAME is missing from .env")

    if not PASSWORD:
        raise RuntimeError("NEO4J_PASSWORD is missing from .env")

    driver = create_driver()

    try:
        driver.verify_connectivity()

        print("Connected to Neo4j successfully.")
        print("Starting POKEC import...")

        batch = []
        total = 0

        with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:

            for line in file:

                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                parts = line.split()

                if len(parts) < 2:
                    continue

                source = int(parts[0])
                target = int(parts[1])

                batch.append({
                    "source": source,
                    "target": target
                })

                if len(batch) >= BATCH_SIZE:

                    success = import_batch(driver, batch)

                    if not success:
                        raise RuntimeError(
                            "Batch failed after maximum retries."
                        )

                    total += len(batch)

                    print(
                        f"Imported {total:,} relationships..."
                    )

                    batch.clear()

            if batch:

                success = import_batch(driver, batch)

                if not success:
                    raise RuntimeError(
                        "Final batch failed after maximum retries."
                    )

                total += len(batch)

        print()
        print("POKEC import completed successfully!")
        print(f"Relationships processed: {total:,}")

    finally:
        driver.close()


if __name__ == "__main__":
    import_pokec()