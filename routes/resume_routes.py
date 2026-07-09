"""
Resume routes: upload, database listing, profile view, edit, delete,
download, notes, shortlist toggling, and export.
"""
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, jsonify, session, send_file, abort
)
from utils.decorators import login_required
from utils.validators import (
    is_valid_email, is_valid_phone, allowed_file,
    is_valid_file_size, validate_required_fields, parse_skills,
)
from utils.storage import upload_file, delete_file
from utils.exporters import export_to_excel, export_to_pdf
from models.resume_model import (
    create_resume, find_duplicate, get_resume, update_resume,
    replace_resume_file, delete_resume, add_note, set_status, list_resumes,
)
from models.log_model import log_activity

resume_bp = Blueprint("resume", __name__)

REQUIRED_FIELDS = ["name", "email", "phone", "department"]


@resume_bp.route("/upload-resume", methods=["GET", "POST"])
@login_required
def upload_resume():
    if request.method == "GET":
        return render_template("upload_resume.html")

    form = request.form
    missing = validate_required_fields(form, REQUIRED_FIELDS)
    if missing:
        flash(f"Missing required fields: {', '.join(missing)}", "danger")
        return render_template("upload_resume.html", form=form)

    email = form["email"].strip()
    phone = form["phone"].strip()

    if not is_valid_email(email):
        flash("Please enter a valid email address.", "danger")
        return render_template("upload_resume.html", form=form)
    if not is_valid_phone(phone):
        flash("Please enter a valid phone number.", "danger")
        return render_template("upload_resume.html", form=form)

    if find_duplicate(email):
        flash("A resume with this email already exists. Please edit the existing record instead.", "warning")
        return render_template("upload_resume.html", form=form)

    file = request.files.get("resume_file")
    if not file or file.filename == "":
        flash("Please attach a resume file (PDF, DOC, or DOCX).", "danger")
        return render_template("upload_resume.html", form=form)
    if not allowed_file(file.filename):
        flash("Unsupported file type. Only PDF, DOC, and DOCX are allowed.", "danger")
        return render_template("upload_resume.html", form=form)
    if not is_valid_file_size(file):
        flash("File is too large. Maximum size is 10 MB.", "danger")
        return render_template("upload_resume.html", form=form)

    upload_result = upload_file(file, subfolder="resumes")

    resume_id = create_resume(
        {
            "name": form["name"].strip(),
            "email": email,
            "phone": phone,
            "address": form.get("address", "").strip(),
            "university": form.get("university", "").strip(),
            "graduation_year": form.get("graduation_year") or None,
            "skills": parse_skills(form.get("skills", "")),
            "experience_years": float(form.get("experience_years") or 0),
            "certifications": parse_skills(form.get("certifications", "")),
            "department": form["department"].strip(),
            "resume_url": upload_result["url"],
            "storage_path": upload_result["storage_path"],
            "file_type": upload_result["file_type"],
            "file_size": upload_result["file_size"],
        }
    )

    log_activity(session.get("email"), "Upload", f"Uploaded resume for {form['name']}")
    flash("Resume uploaded successfully!", "success")
    return redirect(url_for("resume.resume_profile", resume_id=resume_id))


@resume_bp.route("/resume-database")
@login_required
def resume_database():
    page = int(request.args.get("page", 1))
    department = request.args.get("department", "")
    status = request.args.get("status", "")

    query = {}
    if department:
        query["department"] = department
    if status:
        query["status"] = status

    resumes, total = list_resumes(query, page=page, per_page=10)
    total_pages = max(1, (total + 9) // 10)

    return render_template(
        "resume_database.html",
        resumes=resumes,
        page=page,
        total_pages=total_pages,
        department=department,
        status=status,
    )


@resume_bp.route("/resume/<resume_id>")
@login_required
def resume_profile(resume_id):
    resume = get_resume(resume_id)
    if not resume:
        abort(404)
    return render_template("resume_profile.html", resume=resume)


@resume_bp.route("/resume/<resume_id>/edit", methods=["GET", "POST"])
@login_required
def edit_resume(resume_id):
    resume = get_resume(resume_id)
    if not resume:
        abort(404)

    if request.method == "GET":
        return render_template("edit_resume.html", resume=resume)

    form = request.form
    missing = validate_required_fields(form, REQUIRED_FIELDS)
    if missing:
        flash(f"Missing required fields: {', '.join(missing)}", "danger")
        return render_template("edit_resume.html", resume=resume)

    if not is_valid_email(form["email"]):
        flash("Please enter a valid email address.", "danger")
        return render_template("edit_resume.html", resume=resume)
    if not is_valid_phone(form["phone"]):
        flash("Please enter a valid phone number.", "danger")
        return render_template("edit_resume.html", resume=resume)

    updates = {
        "name": form["name"].strip(),
        "email": form["email"].strip().lower(),
        "phone": form["phone"].strip(),
        "address": form.get("address", "").strip(),
        "education.university": form.get("university", "").strip(),
        "education.graduation_year": form.get("graduation_year") or None,
        "skills": parse_skills(form.get("skills", "")),
        "experience_years": float(form.get("experience_years") or 0),
        "certifications": parse_skills(form.get("certifications", "")),
        "department": form["department"].strip(),
    }
    update_resume(resume_id, updates)

    new_file = request.files.get("resume_file")
    if new_file and new_file.filename:
        if not allowed_file(new_file.filename):
            flash("Unsupported file type for replacement resume.", "danger")
            return redirect(url_for("resume.edit_resume", resume_id=resume_id))
        if not is_valid_file_size(new_file):
            flash("Replacement file is too large.", "danger")
            return redirect(url_for("resume.edit_resume", resume_id=resume_id))
        result = upload_file(new_file, subfolder="resumes")
        replace_resume_file(
            resume_id, result["url"], result["storage_path"], result["file_type"], result["file_size"]
        )

    log_activity(session.get("email"), "Edit", f"Edited resume {resume_id}")
    flash("Resume updated successfully.", "success")
    return redirect(url_for("resume.resume_profile", resume_id=resume_id))


@resume_bp.route("/resume/<resume_id>/delete", methods=["POST"])
@login_required
def delete_resume_route(resume_id):
    resume = get_resume(resume_id)
    if not resume:
        abort(404)

    if resume.get("storage_path"):
        try:
            delete_file(resume["storage_path"])
        except Exception:
            pass  # File may already be gone; don't block record deletion

    delete_resume(resume_id)
    log_activity(session.get("email"), "Delete", f"Deleted resume for {resume.get('name')}")
    flash("Resume deleted.", "info")
    return redirect(url_for("resume.resume_database"))


@resume_bp.route("/resume/<resume_id>/download")
@login_required
def download_resume(resume_id):
    resume = get_resume(resume_id)
    if not resume:
        abort(404)
    log_activity(session.get("email"), "Download", f"Downloaded resume for {resume.get('name')}")
    return redirect(resume["resume_url"])


@resume_bp.route("/resume/<resume_id>/note", methods=["POST"])
@login_required
def add_resume_note(resume_id):
    text = request.form.get("note", "").strip()
    if text:
        add_note(resume_id, session.get("name", "Unknown"), text)
        flash("Note added.", "success")
    return redirect(url_for("resume.resume_profile", resume_id=resume_id))


@resume_bp.route("/resume/<resume_id>/status", methods=["POST"])
@login_required
def update_status(resume_id):
    status = request.form.get("status")
    try:
        set_status(resume_id, status)
        flash(f"Status updated to {status}.", "success")
    except ValueError:
        flash("Invalid status.", "danger")
    return redirect(url_for("resume.resume_profile", resume_id=resume_id))


@resume_bp.route("/shortlisted")
@login_required
def shortlisted_candidates():
    page = int(request.args.get("page", 1))
    resumes, total = list_resumes({"status": "Shortlisted"}, page=page, per_page=10)
    total_pages = max(1, (total + 9) // 10)
    return render_template("shortlisted.html", resumes=resumes, page=page, total_pages=total_pages)


@resume_bp.route("/export/<fmt>")
@login_required
def export_candidates(fmt):
    resumes, _ = list_resumes({}, per_page=10000)
    if fmt == "excel":
        buffer = export_to_excel(resumes)
        log_activity(session.get("email"), "Download", "Exported candidate list to Excel")
        return send_file(
            buffer, as_attachment=True, download_name="candidates.xlsx",
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    elif fmt == "pdf":
        buffer = export_to_pdf(resumes)
        log_activity(session.get("email"), "Download", "Exported candidate list to PDF")
        return send_file(buffer, as_attachment=True, download_name="candidates.pdf", mimetype="application/pdf")
    abort(404)
