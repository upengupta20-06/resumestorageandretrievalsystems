"""
Search routes: advanced resume search page and its JSON API.
"""
from flask import Blueprint, render_template, request, jsonify, session
from utils.decorators import login_required
from models.resume_model import search_resumes
from models.log_model import log_activity
from bson import ObjectId

search_bp = Blueprint("search", __name__)


def _serialize(resume):
    resume["_id"] = str(resume["_id"])
    if resume.get("upload_date"):
        resume["upload_date"] = resume["upload_date"].strftime("%Y-%m-%d")
    return resume


@search_bp.route("/search-resumes")
@login_required
def search_resumes_page():
    return render_template("search_resumes.html")


@search_bp.route("/api/search")
@login_required
def api_search():
    criteria = {
        "name": request.args.get("name", ""),
        "department": request.args.get("department", ""),
        "education": request.args.get("education", ""),
        "graduation_year": request.args.get("graduation_year", ""),
        "skills": request.args.get("skills", "").split(",") if request.args.get("skills") else [],
        "certifications": request.args.get("certifications", ""),
        "min_experience": request.args.get("min_experience") or None,
        "keyword": request.args.get("keyword", ""),
    }
    sort_by = request.args.get("sort_by", "upload_date")
    sort_dir = -1 if request.args.get("sort_dir", "desc") == "desc" else 1
    page = int(request.args.get("page", 1))

    resumes, total = search_resumes(criteria, sort_by=sort_by, sort_dir=sort_dir, page=page, per_page=10)

    if any(criteria.values()):
        log_activity(session.get("email"), "Search", f"Searched with criteria: {criteria}")

    return jsonify(
        {
            "results": [_serialize(r) for r in resumes],
            "total": total,
            "page": page,
            "total_pages": max(1, (total + 9) // 10),
        }
    )
