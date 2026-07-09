"""
Dashboard routes: main HR dashboard home page and its JSON data API.
"""
from flask import Blueprint, render_template, jsonify
from utils.decorators import login_required
from models.resume_model import (
    dashboard_stats,
    department_distribution,
    skill_distribution,
    monthly_upload_trends,
    experience_distribution,
)

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_home():
    stats = dashboard_stats()
    return render_template("dashboard.html", stats=stats)


@dashboard_bp.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    stats = dashboard_stats()
    stats["recent_uploads"] = [
        {
            "id": str(r["_id"]),
            "name": r["name"],
            "department": r.get("department", ""),
            "upload_date": r["upload_date"].strftime("%Y-%m-%d %H:%M"),
            "status": r.get("status", "New"),
        }
        for r in stats["recent_uploads"]
    ]

    return jsonify(
        {
            "stats": stats,
            "charts": {
                "department": department_distribution(),
                "skills": skill_distribution(),
                "monthly": monthly_upload_trends(),
                "experience": experience_distribution(),
            },
        }
    )
