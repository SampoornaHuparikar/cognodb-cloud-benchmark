import os
from dotenv import load_dotenv

load_dotenv()

COGNODB_URI = os.getenv("COGNODB_URI")
COGNODB_USERNAME = os.getenv("COGNODB_USER", "cognodb")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD")

DATASET_NAME = "pokec_sample"
TARGET_RELATIONSHIPS = 100_000

WARMUP_ITERATIONS = 20
READ_ITERATIONS = 100

CONCURRENCY_LEVELS = [1, 10, 40]