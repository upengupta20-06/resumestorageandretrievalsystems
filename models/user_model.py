"""
User model — thin wrapper around the `users` MongoDB collection.
Passwords are always stored hashed (bcrypt via Werkzeug's generate_password_hash).
"""
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import get_db


ROLES = ("admin", "recruiter", "viewer")


def create_user(name, email, password, role="recruiter"):
    db = get_db()
    if db.users.find_one({"email": email.lower()}):
        raise ValueError("A user with this email already exists.")

    user = {
        "name": name,
        "email": email.lower(),
        "password_hash": generate_password_hash(password),
        "role": role if role in ROLES else "recruiter",
        "created_at": datetime.utcnow(),
        "last_login": None,
        "active": True,
    }
    result = db.users.insert_one(user)
    return str(result.inserted_id)


def verify_user(email, password):
    """Return the user dict if credentials are valid, else None."""
    db = get_db()
    user = db.users.find_one({"email": email.lower(), "active": True})
    if not user:
        return None
    if not check_password_hash(user["password_hash"], password):
        return None
    return user


def get_user_by_id(user_id):
    db = get_db()
    try:
        return db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None


def update_last_login(user_id):
    db = get_db()
    db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"last_login": datetime.utcnow()}}
    )


def change_password(user_id, new_password):
    db = get_db()
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": generate_password_hash(new_password)}},
    )


def list_users():
    db = get_db()
    return list(db.users.find({}, {"password_hash": 0}))


def delete_user(user_id):
    db = get_db()
    db.users.delete_one({"_id": ObjectId(user_id)})


def set_user_role(user_id, role):
    if role not in ROLES:
        raise ValueError("Invalid role")
    db = get_db()
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": role}})
