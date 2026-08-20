import os
import gzip
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, TransientError

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

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
                f"⚠️ Batch failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {error}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(3)
                driver.verify_connectivity()

    return False


def import_pokec():

    print("Connecting to CognoDB...")

    driver = create_driver()
    driver.verify_connectivity()

    print("✅ Connected to CognoDB")
    print("Starting POKEC import...")

    batch = []
    total = 0

    try:

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

                batch.append(
                    {
                        "source": source,
                        "target": target,
                    }
                )

                if len(batch) >= BATCH_SIZE:

                    success = import_batch(driver, batch)

                    if not success:
                        print("❌ Batch failed after maximum retries.")
                        print("Stopping import safely.")
                        return

                    total += len(batch)

                    print(f"Imported {total:,} relationships")

                    batch.clear()

        if batch:

            success = import_batch(driver, batch)

            if not success:
                print("❌ Final batch failed.")
                return

            total += len(batch)

        print()
        print("✅ Import complete!")
        print(f"Total relationships processed: {total:,}")

    finally:
        driver.close()


if __name__ == "__main__":
    import_pokec()