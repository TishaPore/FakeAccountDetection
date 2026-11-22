
import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION",
    "fake_account_posts"
)

client = None


def connect_qdrant():
    global client

    if not QDRANT_URL or not QDRANT_API_KEY:
        raise ValueError("Qdrant credentials missing from .env")

    client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        timeout=20
    )

    # Verify actual connection
    client.get_collections()

    return client


def get_qdrant_client():
    global client

    if client is None:
        return connect_qdrant()

    return client


if __name__ == "__main__":
    try:
        qdrant = connect_qdrant()
        print("Qdrant connected successfully!")
        print("Collections:", qdrant.get_collections().collections)

    except Exception as error:
        print("Qdrant connection failed:", error)
