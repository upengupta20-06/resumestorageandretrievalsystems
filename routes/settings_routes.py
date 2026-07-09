"""
Settings routes: profile update, password change, cloud storage config,
and notification preferences (self-service, for the logged-in user).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bson import ObjectId
from utils.decorators import login_required
from utils.validators import is_valid_email
from models.db import get_db
from models.user_model import get_user_by_id, change_password
from models.log_model import log_activity
from werkzeug.security import check_password_hash

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings")
@login_required
def settings_home():
    user = get_user_by_id(session["user_id"])
    return render_template("settings.html", user=user)


@settings_bp.route("/settings/profile", methods=["POST"])
@login_required
def update_profile():
    db = get_db()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()

    if not name or not is_valid_email(email):
        flash("Please provide a valid name and email.", "danger")
        return redirect(url_for("settings.settings_home"))

    db.users.update_one(
        {"_id": ObjectId(session["user_id"])},
        {"$set": {"name": name, "email": email.lower()}},
    )
    session["name"] = name
    session["email"] = email.lower()
    log_activity(email, "Edit", "Updated profile")
    flash("Profile updated.", "success")
    return redirect(url_for("settings.settings_home"))


@settings_bp.route("/settings/password", methods=["POST"])
@login_required
def update_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    user = get_user_by_id(session["user_id"])
    if not check_password_hash(user["password_hash"], current_password):
        flash("Current password is incorrect.", "danger")
        return redirect(url_for("settings.settings_home"))
    if len(new_password) < 8:
        flash("New password must be at least 8 characters.", "danger")
        return redirect(url_for("settings.settings_home"))
    if new_password != confirm_password:
        flash("New password and confirmation do not match.", "danger")
        return redirect(url_for("settings.settings_home"))

    change_password(session["user_id"], new_password)
    log_activity(session.get("email"), "Edit", "Changed password")
    flash("Password changed successfully.", "success")
    return redirect(url_for("settings.settings_home"))


@settings_bp.route("/settings/notifications", methods=["POST"])
@login_required
def update_notifications():
    db = get_db()
    prefs = {
        "email_on_upload": request.form.get("email_on_upload") == "on",
        "email_on_shortlist": request.form.get("email_on_shortlist") == "on",
        "weekly_summary": request.form.get("weekly_summary") == "on",
    }
    db.users.update_one(
        {"_id": ObjectId(session["user_id"])}, {"$set": {"notification_preferences": prefs}}
    )
    flash("Notification preferences saved.", "success")
    return redirect(url_for("settings.settings_home"))
