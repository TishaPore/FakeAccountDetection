
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from qdrant_client import QdrantClient

load_dotenv()

# MongoDB connection
try:
    mongo = MongoClient(
        os.getenv("MONGODB_URI"),
        serverSelectionTimeoutMS=10000
    )
    mongo.admin.command("ping")
    print("MongoDB: CONNECTED")
except Exception as e:
    print("MongoDB: FAILED -", e)

# Qdrant connection
try:
    qdrant = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    print("Qdrant: CONNECTED")
    print("Collections:", qdrant.get_collections())
except Exception as e:
    print("Qdrant: FAILED -", e)
