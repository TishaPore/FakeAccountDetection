from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os
from datetime import datetime

# Load environment variables
load_dotenv(Path(__file__).resolve().parent / ".env")

# Connect MongoDB
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DATABASE")]

accounts = db.accounts.find()

print("\n===== FAKE ACCOUNT DETECTION =====")

for account in accounts:
    score = 0

    if account["followers"] < 100:
        score += 30

    if account["following"] > 1000:
        score += 25

    if account["posts_count"] < 5:
        score += 20

    if account["account_age_days"] < 30:
        score += 25

    if score >= 70:
        risk = "HIGH"
        status = "SUSPICIOUS"
    elif score >= 40:
        risk = "MEDIUM"
        status = "REVIEW"
    else:
        risk = "LOW"
        status = "NORMAL"

    result = {
        "user_id": account["user_id"],
        "username": account["username"],
        "risk_score": score,
        "risk_level": risk,
        "detection_status": status,
        "analyzed_at": datetime.now()
    }

    db.analysis_results.update_one(
        {"user_id": account["user_id"]},
        {"$set": result},
        upsert=True
    )

    print(result)

print("\nDetection results saved to MongoDB!")
client.close()