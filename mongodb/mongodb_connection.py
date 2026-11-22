
import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

# Load local .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Load Streamlit Cloud Secrets when available
try:
    import streamlit as st

    if "MONGODB_URI" in st.secrets:
        os.environ["MONGODB_URI"] = str(st.secrets["MONGODB_URI"])

    if "MONGODB_DATABASE" in st.secrets:
        os.environ["MONGODB_DATABASE"] = str(
            st.secrets["MONGODB_DATABASE"]
        )

except Exception:
    # Local execution can continue using .env
    pass

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "FakeAccountDB")

client = None
db = None


def connect_mongodb():
    global client, db

    try:
        if not MONGODB_URI:
            raise ValueError(
                "MONGODB_URI is missing. Configure .env or Streamlit Secrets."
            )

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
