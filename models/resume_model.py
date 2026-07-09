"""
Resume model — wraps the `resumes` MongoDB collection.

Each resume document shape:
{
  _id, name, email, phone, address,
  education: { university, graduation_year },
  skills: [str],
  experience_years: number,
  certifications: [str],
  department, resume_url, storage_path,
  file_type, file_size,
  status,                # "New" | "Reviewed" | "Shortlisted" | "Rejected"
  notes: [{author, text, created_at}],
  version_history: [{resume_url, uploaded_at}],
  upload_date, updated_at
}
"""
from datetime import datetime
from bson import ObjectId
from models.db import get_db

STATUSES = ("New", "Reviewed", "Shortlisted", "Rejected")


def create_resume(data):
    db = get_db()
    now = datetime.utcnow()
    doc = {
        "name": data["name"],
        "email": data["email"].lower(),
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "education": {
            "university": data.get("university", ""),
            "graduation_year": data.get("graduation_year"),
        },
        "skills": data.get("skills", []),
        "experience_years": data.get("experience_years", 0),
        "certifications": data.get("certifications", []),
        "department": data.get("department", "General"),
        "resume_url": data["resume_url"],
        "storage_path": data.get("storage_path", ""),
        "file_type": data.get("file_type", ""),
        "file_size": data.get("file_size", 0),
        "status": "New",
        "notes": [],
        "version_history": [{"resume_url": data["resume_url"], "uploaded_at": now}],
        "upload_date": now,
        "updated_at": now,
    }
    result = db.resumes.insert_one(doc)
    return str(result.inserted_id)


def find_duplicate(email):
    db = get_db()
    return db.resumes.find_one({"email": email.lower()})


def get_resume(resume_id):
    db = get_db()
    try:
        return db.resumes.find_one({"_id": ObjectId(resume_id)})
    except Exception:
        return None


def update_resume(resume_id, updates):
    db = get_db()
    updates["updated_at"] = datetime.utcnow()
    db.resumes.update_one({"_id": ObjectId(resume_id)}, {"$set": updates})


def replace_resume_file(resume_id, resume_url, storage_path, file_type, file_size):
    db = get_db()
    now = datetime.utcnow()
    db.resumes.update_one(
        {"_id": ObjectId(resume_id)},
        {
            "$set": {
                "resume_url": resume_url,
                "storage_path": storage_path,
                "file_type": file_type,
                "file_size": file_size,
                "updated_at": now,
            },
            "$push": {"version_history": {"resume_url": resume_url, "uploaded_at": now}},
        },
    )


def delete_resume(resume_id):
    db = get_db()
    db.resumes.delete_one({"_id": ObjectId(resume_id)})


def add_note(resume_id, author, text):
    db = get_db()
    db.resumes.update_one(
        {"_id": ObjectId(resume_id)},
        {"$push": {"notes": {"author": author, "text": text, "created_at": datetime.utcnow()}}},
    )


def set_status(resume_id, status):
    if status not in STATUSES:
        raise ValueError("Invalid status")
    db = get_db()
    db.resumes.update_one(
        {"_id": ObjectId(resume_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}},
    )


def list_resumes(filters=None, sort_by="upload_date", sort_dir=-1, page=1, per_page=10):
    db = get_db()
    query = filters or {}
    skip = (page - 1) * per_page
    cursor = (
        db.resumes.find(query)
        .sort(sort_by, sort_dir)
        .skip(skip)
        .limit(per_page)
    )
    total = db.resumes.count_documents(query)
    return list(cursor), total


def search_resumes(criteria, sort_by="upload_date", sort_dir=-1, page=1, per_page=10):
    """
    criteria: dict that may contain name, skills, department, education,
    min_experience, graduation_year, certifications, keyword
    """
    db = get_db()
    query = {}

    if criteria.get("name"):
        query["name"] = {"$regex": criteria["name"], "$options": "i"}
    if criteria.get("department"):
        query["department"] = criteria["department"]
    if criteria.get("education"):
        query["education.university"] = {"$regex": criteria["education"], "$options": "i"}
    if criteria.get("graduation_year"):
        query["education.graduation_year"] = int(criteria["graduation_year"])
    if criteria.get("skills"):
        skills_list = criteria["skills"] if isinstance(criteria["skills"], list) else [criteria["skills"]]
        query["skills"] = {"$in": [s.strip() for s in skills_list if s.strip()]}
    if criteria.get("certifications"):
        query["certifications"] = {"$regex": criteria["certifications"], "$options": "i"}
    if criteria.get("min_experience") is not None:
        query["experience_years"] = {"$gte": float(criteria["min_experience"])}
    if criteria.get("keyword"):
        kw = criteria["keyword"]
        query["$or"] = [
            {"name": {"$regex": kw, "$options": "i"}},
            {"email": {"$regex": kw, "$options": "i"}},
            {"skills": {"$regex": kw, "$options": "i"}},
            {"department": {"$regex": kw, "$options": "i"}},
            {"certifications": {"$regex": kw, "$options": "i"}},
        ]

    return list_resumes(query, sort_by, sort_dir, page, per_page)


def dashboard_stats():
    db = get_db()
    total = db.resumes.count_documents({})

    start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = db.resumes.count_documents({"upload_date": {"$gte": start_of_month}})
    shortlisted = db.resumes.count_documents({"status": "Shortlisted"})
    departments = db.resumes.distinct("department")

    recent = list(db.resumes.find().sort("upload_date", -1).limit(5))
    return {
        "total": total,
        "new_this_month": new_this_month,
        "shortlisted": shortlisted,
        "department_count": len(departments),
        "recent_uploads": recent,
    }


def department_distribution():
    db = get_db()
    pipeline = [{"$group": {"_id": "$department", "count": {"$sum": 1}}}]
    return list(db.resumes.aggregate(pipeline))


def skill_distribution(limit=10):
    db = get_db()
    pipeline = [
        {"$unwind": "$skills"},
        {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
    ]
    return list(db.resumes.aggregate(pipeline))


def monthly_upload_trends(months=6):
    db = get_db()
    pipeline = [
        {
            "$group": {
                "_id": {"y": {"$year": "$upload_date"}, "m": {"$month": "$upload_date"}},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.y": 1, "_id.m": 1}},
        {"$limit": months},
    ]
    return list(db.resumes.aggregate(pipeline))


def experience_distribution():
    db = get_db()
    pipeline = [
        {
            "$bucket": {
                "groupBy": "$experience_years",
                "boundaries": [0, 2, 5, 10, 100],
                "default": "10+",
                "output": {"count": {"$sum": 1}},
            }
        }
    ]
    return list(db.resumes.aggregate(pipeline))
