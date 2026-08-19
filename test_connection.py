import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USERNAME")
password = os.getenv("COGNODB_PASSWORD")

print("Testing CognoDB connection...")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

try:
    driver.verify_connectivity()
    print("✅ CognoDB connection successful!")
except Exception as e:
    print("❌ Connection failed:")
    print(e)
finally:
    driver.close()