
import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

# Load the main project .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "FakeAccountDB")

client = None
db = None


def connect_mongodb():
    global client, db

    try:
        if not MONGODB_URI:
            raise ValueError("MONGODB_URI is missing from .env")

        print("Connecting to MongoDB Atlas...")

        client = MongoClient(
            MONGODB_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=15000
        )

        client.admin.command("ping")

        db = client[DATABASE_NAME]

        print("MongoDB Atlas connected successfully!")
        print("Database:", DATABASE_NAME)
        print("Collections:", db.list_collection_names())

        return db

    except Exception as error:
        print("MongoDB connection failed!")
        print("Error:", error)
        return None


if __name__ == "__main__":
    connect_mongodb()
