"""
MongoDB Atlas connection setup.
Exposes `get_db()` to fetch the active pymongo Database handle from anywhere
in the app, and `init_db(app)` to attach it during app creation.
"""
from pymongo import MongoClient, ASCENDING
from flask import g, current_app

_client = None


def init_db(app):
    """Create a MongoClient once and store it on the app object."""
    global _client
    _client = MongoClient(app.config["MONGO_URI"])
    app.mongo_client = _client
    app.db = _client[app.config["MONGO_DB_NAME"]]

    with app.app_context():
        _ensure_indexes(app.db)


def _ensure_indexes(db):
    """Create indexes required for uniqueness and fast search/sort."""
    db.users.create_index("email", unique=True)
    db.resumes.create_index([("email", ASCENDING)])
    db.resumes.create_index([("name", ASCENDING)])
    db.resumes.create_index([("department", ASCENDING)])
    db.resumes.create_index([("skills", ASCENDING)])
    db.resumes.create_index([("upload_date", ASCENDING)])
    db.logs.create_index([("timestamp", ASCENDING)])


def get_db():
    """Return the active database handle for the current app context."""
    return current_app.db
