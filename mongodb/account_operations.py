
from mongodb.mongodb_connection import connect_mongodb

def get_db():
    db = connect_mongodb()
    if db is None:
        raise ConnectionError("MongoDB connection failed")
    return db


# Get all registered accounts
def get_accounts():
    db = get_db()
    return [
        {k: v for k, v in account.items() if k != "_id"}
        for account in db.accounts.find()
    ]


# Add a new account
def add_account(account):
    db = get_db()

    existing = db.accounts.find_one({
        "username": {
            "$regex": f"^{account['username']}$",
            "$options": "i"
        }
    })

    if existing:
        return False

    db.accounts.insert_one(account)
    return True


# Delete an account
def delete_account(user_id):
    db = get_db()

    db.accounts.delete_one({"user_id": user_id})

    # Also delete its analysis history
    db.analysis_results.delete_many({"user_id": user_id})


# Save an analysis result
def save_analysis(result):
    db = get_db()
    db.analysis_results.insert_one(result)


# Get detection history
def get_analysis():
    db = get_db()

    return [
        {k: v for k, v in result.items() if k != "_id"}
        for result in db.analysis_results.find().sort("_id", -1)
    ]


# Clear detection history
def clear_analysis():
    db = get_db()
    db.analysis_results.delete_many({})
