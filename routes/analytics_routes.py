"""
Analytics routes: analytics dashboard page and chart data API.
"""
from flask import Blueprint, render_template, jsonify
from utils.decorators import login_required
from models.resume_model import (
    dashboard_stats, department_distribution, skill_distribution,
    monthly_upload_trends, experience_distribution,
)
from models.db import get_db

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics")
@login_required
def analytics_home():
    stats = dashboard_stats()
    return render_template("analytics.html", stats=stats)


@analytics_bp.route("/api/analytics-data")
@login_required
def api_analytics_data():
    db = get_db()
    stats = dashboard_stats()

    # Simple hiring funnel based on status counts
    funnel = {
        "New": db.resumes.count_documents({"status": "New"}),
        "Reviewed": db.resumes.count_documents({"status": "Reviewed"}),
        "Shortlisted": db.resumes.count_documents({"status": "Shortlisted"}),
        "Rejected": db.resumes.count_documents({"status": "Rejected"}),
    }

    # Rough cloud storage usage estimate (sum of file sizes in MB)
    pipeline = [{"$group": {"_id": None, "total_bytes": {"$sum": "$file_size"}}}]
    agg = list(db.resumes.aggregate(pipeline))
    total_mb = round((agg[0]["total_bytes"] / (1024 * 1024)), 2) if agg else 0

    return jsonify(
        {
            "totals": {
                "total_resumes": stats["total"],
                "storage_used_mb": total_mb,
            },
            "department": department_distribution(),
            "skills": skill_distribution(),
            "monthly": monthly_upload_trends(),
            "experience": experience_distribution(),
            "funnel": funnel,
        }
    )
