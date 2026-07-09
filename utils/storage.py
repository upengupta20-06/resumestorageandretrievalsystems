"""
Cloud storage abstraction layer.

Provides a single interface (upload_file / delete_file) regardless of which
backend is configured via STORAGE_PROVIDER: "firebase", "s3", or "local".

Only the resulting URL is ever stored in MongoDB — the raw file bytes live in
cloud storage (or the local uploads/ folder as a dev fallback).
"""
import os
import uuid
from datetime import datetime
from flask import current_app


def _unique_filename(original_filename):
    ext = original_filename.rsplit(".", 1)[-1].lower()
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{stamp}_{uuid.uuid4().hex[:8]}.{ext}"


def upload_file(file_storage, subfolder="resumes"):
    """
    Upload a werkzeug FileStorage object to the configured provider.
    Returns dict: { url, storage_path, file_type, file_size }
    """
    provider = current_app.config["STORAGE_PROVIDER"]
    filename = _unique_filename(file_storage.filename)
    file_storage.stream.seek(0, os.SEEK_END)
    file_size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    file_type = filename.rsplit(".", 1)[-1].lower()

    if provider == "firebase":
        url, path = _upload_firebase(file_storage, subfolder, filename)
    elif provider == "s3":
        url, path = _upload_s3(file_storage, subfolder, filename)
    else:
        url, path = _upload_local(file_storage, subfolder, filename)

    return {"url": url, "storage_path": path, "file_type": file_type, "file_size": file_size}


def delete_file(storage_path):
    provider = current_app.config["STORAGE_PROVIDER"]
    if provider == "firebase":
        _delete_firebase(storage_path)
    elif provider == "s3":
        _delete_s3(storage_path)
    else:
        _delete_local(storage_path)


# ---------------------------------------------------------------------
# Local filesystem (development fallback)
# ---------------------------------------------------------------------
def _upload_local(file_storage, subfolder, filename):
    folder = os.path.join(current_app.config["LOCAL_UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    file_storage.save(path)
    rel_path = os.path.join(subfolder, filename)
    url = f"/uploads/{rel_path.replace(os.sep, '/')}"
    return url, rel_path


def _delete_local(storage_path):
    full_path = os.path.join(current_app.config["LOCAL_UPLOAD_FOLDER"], storage_path)
    if os.path.exists(full_path):
        os.remove(full_path)


# ---------------------------------------------------------------------
# Firebase Storage
# ---------------------------------------------------------------------
def _get_firebase_bucket():
    import firebase_admin
    from firebase_admin import credentials, storage

    if not firebase_admin._apps:
        cred = credentials.Certificate(current_app.config["FIREBASE_CREDENTIALS_JSON"])
        firebase_admin.initialize_app(
            cred, {"storageBucket": current_app.config["FIREBASE_STORAGE_BUCKET"]}
        )
    return storage.bucket()


def _upload_firebase(file_storage, subfolder, filename):
    bucket = _get_firebase_bucket()
    blob_path = f"{subfolder}/{filename}"
    blob = bucket.blob(blob_path)
    blob.upload_from_file(file_storage.stream, content_type=file_storage.content_type)
    blob.make_public()
    return blob.public_url, blob_path


def _delete_firebase(storage_path):
    bucket = _get_firebase_bucket()
    blob = bucket.blob(storage_path)
    if blob.exists():
        blob.delete()


# ---------------------------------------------------------------------
# AWS S3
# ---------------------------------------------------------------------
def _get_s3_client():
    import boto3

    return boto3.client(
        "s3",
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_REGION"],
    )


def _upload_s3(file_storage, subfolder, filename):
    client = _get_s3_client()
    bucket = current_app.config["AWS_S3_BUCKET"]
    key = f"{subfolder}/{filename}"
    client.upload_fileobj(
        file_storage.stream, bucket, key, ExtraArgs={"ContentType": file_storage.content_type}
    )
    url = f"https://{bucket}.s3.{current_app.config['AWS_REGION']}.amazonaws.com/{key}"
    return url, key


def _delete_s3(storage_path):
    client = _get_s3_client()
    bucket = current_app.config["AWS_S3_BUCKET"]
    client.delete_object(Bucket=bucket, Key=storage_path)
