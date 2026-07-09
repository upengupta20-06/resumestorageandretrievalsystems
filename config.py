"""
Application configuration.
All secrets are pulled from environment variables — never hard-code credentials.
Copy .env.example to .env and fill in real values before running.
"""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # ---- Core Flask ----
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # ---- Session ----
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    # Set to True when served over HTTPS in production
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"

    # ---- MongoDB Atlas ----
    MONGO_URI = os.environ.get(
        "MONGO_URI",
        "mongodb+srv://<username>:<password>@<cluster-url>/resume_system?retryWrites=true&w=majority",
    )
    MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "resume_system")

    # ---- File Upload ----
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload size
    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
    LOCAL_UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

    # ---- Cloud Storage Provider ----
    # "firebase", "s3", or "local" (local is used as a safe default/fallback
    # for development when no cloud credentials are configured)
    STORAGE_PROVIDER = os.environ.get("STORAGE_PROVIDER", "local")

    # Firebase
    FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "")

    # AWS S3
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET = os.environ.get("AWS_S3_BUCKET", "")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    # ---- CSRF ----
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
