import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

try:
    MONGODB_URI = st.secrets["MONGODB_URI"]
    DATABASE_NAME = st.secrets.get(
        "MONGODB_DATABASE", "FakeAccountDB"
    )
except Exception:
    MONGODB_URI = os.getenv("MONGODB_URI")
    DATABASE_NAME = os.getenv(
        "MONGODB_DATABASE", "FakeAccountDB"
    )