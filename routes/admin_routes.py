"""
Admin routes: user management, roles/permissions, activity logs,
and simple JSON database backup/restore.
"""
import json
import io
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, send_file, abort
)
from bson import ObjectId
from utils.decorators import login_required, role_required
from models.user_model import (
    create_user, list_users, delete_user, set_user_role,
    change_password, ROLES,
)
from models.log_model import log_activity, list_logs
from models.db import get_db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users")
@login_required
@role_required("admin")
def manage_users():
    users = list_users()
    return render_template("users.html", users=users, roles=ROLES)


@admin_bp.route("/users/add", methods=["POST"])
@login_required
@role_required("admin")
def add_user():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "recruiter")

    if not name or not email or not password:
        flash("All fields are required to add a user.", "danger")
        return redirect(url_for("admin.manage_users"))

    try:
        create_user(name, email, password, role)
        log_activity(session.get("email"), "Edit", f"Created user {email}")
        flash("User created successfully.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<user_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def remove_user(user_id):
    if user_id == session.get("user_id"):
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.manage_users"))
    delete_user(user_id)
    log_activity(session.get("email"), "Delete", f"Deleted user {user_id}")
    flash("User removed.", "info")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<user_id>/role", methods=["POST"])
@login_required
@role_required("admin")
def change_role(user_id):
    role = request.form.get("role")
    try:
        set_user_role(user_id, role)
        log_activity(session.get("email"), "Edit", f"Changed role for {user_id} to {role}")
        flash("Role updated.", "success")
    except ValueError:
        flash("Invalid role.", "danger")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<user_id>/reset-password", methods=["POST"])
@login_required
@role_required("admin")
def reset_password(user_id):
    new_password = request.form.get("new_password", "")
    if len(new_password) < 8:
        flash("Password must be at least 8 characters.", "danger")
        return redirect(url_for("admin.manage_users"))
    change_password(user_id, new_password)
    log_activity(session.get("email"), "Edit", f"Reset password for user {user_id}")
    flash("Password reset successfully.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/activity-logs")
@login_required
@role_required("admin")
def activity_logs():
    page = int(request.args.get("page", 1))
    action = request.args.get("action", "")
    username = request.args.get("username", "")
    logs, total = list_logs(page=page, action=action, username=username)
    total_pages = max(1, (total + 24) // 25)
    return render_template(
        "activity_logs.html", logs=logs, page=page, total_pages=total_pages,
        action=action, username=username,
    )


@admin_bp.route("/backup")
@login_required
@role_required("admin")
def backup_database():
    db = get_db()

    def clean(doc):
        doc = dict(doc)
        doc["_id"] = str(doc["_id"])
        for k, v in doc.items():
            if isinstance(v, datetime):
                doc[k] = v.isoformat()
        return doc

    data = {
        "users": [clean(u) for u in db.users.find({}, {"password_hash": 0})],
        "resumes": [clean(r) for r in db.resumes.find()],
        "logs": [clean(l) for l in db.logs.find()],
        "exported_at": datetime.utcnow().isoformat(),
    }
    buffer = io.BytesIO(json.dumps(data, default=str, indent=2).encode("utf-8"))
    log_activity(session.get("email"), "Download", "Exported database backup")
    return send_file(buffer, as_attachment=True, download_name="backup.json", mimetype="application/json")


@admin_bp.route("/restore", methods=["POST"])
@login_required
@role_required("admin")
def restore_database():
    file = request.files.get("backup_file")
    if not file or not file.filename.endswith(".json"):
        flash("Please upload a valid .json backup file.", "danger")
        return redirect(url_for("admin.manage_users"))

    try:
        data = json.load(file.stream)
        db = get_db()
        if "resumes" in data:
            for doc in data["resumes"]:
                doc.pop("_id", None)
            if data["resumes"]:
                db.resumes.insert_many(data["resumes"])
        log_activity(session.get("email"), "Edit", "Restored database from backup")
        flash("Backup restored successfully.", "success")
    except Exception as e:
        flash(f"Restore failed: {e}", "danger")

    return redirect(url_for("admin.manage_users"))
