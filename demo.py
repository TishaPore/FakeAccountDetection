
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path
import os

# Connect to MongoDB
load_dotenv(Path(__file__).resolve().parent / ".env")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DATABASE")]

def show_accounts():
    print("\n===== REGISTERED ACCOUNTS =====")
    for account in db.accounts.find():
        print(
            f"ID: {account['user_id']} | "
            f"Username: {account['username']} | "
            f"Followers: {account['followers']}"
        )

def analyze_account():
    user_id = input("\nEnter Account ID (U001-U005): ").strip()

    account = db.accounts.find_one({"user_id": user_id})

    if not account:
        print("Account not found!")
        return

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
        risk, status = "HIGH", "SUSPICIOUS"
    elif score >= 40:
        risk, status = "MEDIUM", "REVIEW"
    else:
        risk, status = "LOW", "NORMAL"

    print("\n===== DETECTION REPORT =====")
    print("Username:", account["username"])
    print("Followers:", account["followers"])
    print("Following:", account["following"])
    print("Posts:", account["posts_count"])
    print("Account Age:", account["account_age_days"], "days")
    print("Risk Score:", score, "/ 100")
    print("Risk Level:", risk)
    print("Detection Status:", status)

    db.analysis_results.update_one(
        {"user_id": user_id},
        {"$set": {
            "user_id": user_id,
            "username": account["username"],
            "risk_score": score,
            "risk_level": risk,
            "detection_status": status
        }},
        upsert=True
    )

    print("\nResult saved successfully!")

def show_results():
    print("\n===== PREVIOUS DETECTION RESULTS =====")
    for result in db.analysis_results.find():
        print(
            result["user_id"],
            "|", result["username"],
            "| Score:", result["risk_score"],
            "|", result["detection_status"]
        )

while True:
    print("\n================================")
    print("     FAKE ACCOUNT DETECTOR")
    print("================================")
    print("1. View All Accounts")
    print("2. Analyze an Account")
    print("3. View Detection Results")
    print("4. Exit")

    choice = input("\nChoose an option: ")

    if choice == "1":
        show_accounts()
    elif choice == "2":
        analyze_account()
    elif choice == "3":
        show_results()
    elif choice == "4":
        print("Thank you for using Fake Account Detector!")
        break
    else:
        print("Invalid choice. Try again.")

client.close()
