"""
Activity log model — wraps the `logs` MongoDB collection.
Tracks login, logout, upload, edit, delete, download, search actions.
"""
from datetime import datetime
from models.db import get_db

ACTIONS = ("Login", "Logout", "Upload", "Edit", "Delete", "Download", "Search")


def log_activity(username, action, details=""):
    db = get_db()
    db.logs.insert_one(
        {
            "username": username,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow(),
        }
    )


def list_logs(page=1, per_page=25, action=None, username=None):
    db = get_db()
    query = {}
    if action:
        query["action"] = action
    if username:
        query["username"] = {"$regex": username, "$options": "i"}

    skip = (page - 1) * per_page
    cursor = db.logs.find(query).sort("timestamp", -1).skip(skip).limit(per_page)
    total = db.logs.count_documents(query)
    return list(cursor), total
