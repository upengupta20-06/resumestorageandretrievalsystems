"""
Authentication routes: login, logout, forgot password.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user_model import verify_user, update_last_login
from models.log_model import log_activity
from utils.validators import is_valid_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.dashboard_home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember_me") == "on"

        errors = []
        if not is_valid_email(email):
            errors.append("Please enter a valid email address.")
        if not password:
            errors.append("Password is required.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("login.html", email=email)

        user = verify_user(email, password)
        if not user:
            flash("Invalid email or password.", "danger")
            log_activity(email, "Login", "Failed login attempt")
            return render_template("login.html", email=email)

        session["user_id"] = str(user["_id"])
        session["name"] = user["name"]
        session["email"] = user["email"]
        session["role"] = user["role"]
        session.permanent = remember

        update_last_login(str(user["_id"]))
        log_activity(user["email"], "Login", "Successful login")

        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("dashboard.dashboard_home"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    if session.get("email"):
        log_activity(session["email"], "Logout", "User logged out")
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not is_valid_email(email):
            flash("Please enter a valid email address.", "danger")
            return render_template("forgot_password.html", email=email)

        # In production this would send a reset link via email.
        flash("If an account exists for that email, a reset link has been sent.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")
