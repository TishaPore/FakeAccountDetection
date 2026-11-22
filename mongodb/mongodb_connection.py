
import os
from pathlib import Path

import certifi
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

# Load local .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_config(key, default=None):
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(key, default)


MONGODB_URI = get_config("MONGODB_URI")
DATABASE_NAME = get_config("MONGODB_DATABASE", "FakeAccountDB")

_client = None


def connect_mongodb():
    global _client

    if not MONGODB_URI:
        raise ValueError("MONGODB_URI is missing from Secrets or .env")

    if not DATABASE_NAME:
        raise ValueError("MONGODB_DATABASE is missing")

    try:
        _client = MongoClient(
            MONGODB_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=15000
        )

        _client.admin.command("ping")

        print("MongoDB connected successfully!")

        return _client[DATABASE_NAME]

    except Exception as error:
        if _client is not None:
            _client.close()
            _client = None

        raise RuntimeError(
            f"MongoDB connection failed: {error}"
        ) from error
