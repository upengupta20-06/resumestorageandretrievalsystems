from dotenv import load_dotenv

load_dotenv()
"""
Resume Storage and Retrieval System
Main Flask application entry point.
"""
import os
from flask import Flask, render_template, redirect, url_for, session
<<<<<<< HEAD
from flask_wtf import CSRFProtect
=======
>>>>>>> 6910ba463dd33db6a2340fd9a7a4732b3f75eb26
from config import Config
from models.db import init_db

# Route blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.resume_routes import resume_bp
from routes.search_routes import search_bp
from routes.analytics_routes import analytics_bp
from routes.admin_routes import admin_bp
from routes.settings_routes import settings_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

<<<<<<< HEAD
    # CSRF protection for all POST/PUT/PATCH/DELETE form submissions.
    # File-upload API endpoints that are called from non-browser clients
    # (if any are added later) can be exempted individually with
    # @csrf.exempt on that view function.
    csrf = CSRFProtect(app)
    app.csrf = csrf

=======
>>>>>>> 6910ba463dd33db6a2340fd9a7a4732b3f75eb26
    # Initialize MongoDB connection (attached to app.db)
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(settings_bp)

    # ---------------------------------------------------------------
    # Root redirect
    # ---------------------------------------------------------------
    @app.route("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("dashboard.dashboard_home"))
        return redirect(url_for("auth.login"))

    # ---------------------------------------------------------------
    # Error handlers
    # ---------------------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return app


<<<<<<< HEAD
# ---------------------------------------------------------------------
# Module-level WSGI app instance.
# Required by serverless/WSGI hosts (Vercel, Gunicorn, etc.) which import
# `app` directly from this module rather than calling create_app() themselves.
# ---------------------------------------------------------------------
app = create_app()


if __name__ == "__main__":
=======
if __name__ == "__main__":
    app = create_app()
>>>>>>> 6910ba463dd33db6a2340fd9a7a4732b3f75eb26
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
