"""
Validation utilities: email/phone format checks, file type/size checks,
and required-field checks used across the resume upload and edit forms.
"""
import re
from flask import current_app

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9\-\s()]{7,15}$")


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email.strip()))


def is_valid_phone(phone):
    return bool(phone) and bool(PHONE_RE.match(phone.strip()))


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def is_valid_file_size(file_storage, max_bytes=None):
    max_bytes = max_bytes or current_app.config["MAX_CONTENT_LENGTH"]
    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    return size <= max_bytes


def validate_required_fields(data, required_fields):
    """Returns a list of missing field names (empty list = all present)."""
    missing = []
    for field in required_fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field)
    return missing


def parse_skills(raw):
    """Parse a comma-separated skills string into a clean list."""
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]
