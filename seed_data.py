"""
Seed script: creates a demo admin user and sample resume records so the
dashboard has data to display immediately after setup.

Usage:
    python seed_data.py
<<<<<<< HEAD

NOTE: `create_app()` is only called inside the `if __name__ == "__main__"`
block below, deliberately. Keeping this file free of a top-level `app`
variable prevents deployment platforms (e.g. Vercel's Python builder) from
mistaking this one-off seeding script for the real WSGI entrypoint — that
entrypoint is `app.py`, which defines `app` at module level on purpose.
=======
>>>>>>> 6910ba463dd33db6a2340fd9a7a4732b3f75eb26
"""
from app import create_app
from models.user_model import create_user
from models.resume_model import create_resume
from datetime import datetime, timedelta
import random

<<<<<<< HEAD
=======
app = create_app()

>>>>>>> 6910ba463dd33db6a2340fd9a7a4732b3f75eb26
DEPARTMENTS = ["Engineering", "Design", "Product", "Marketing", "Sales", "HR"]
SKILLS_POOL = ["Python", "JavaScript", "React", "SQL", "AWS", "Figma", "Docker",
               "Project Management", "SEO", "Salesforce", "Java", "Node.js"]

SAMPLE_NAMES = [
    "Aditi Sharma", "Rahul Verma", "Emily Chen", "Michael Okoro", "Sara Ahmed",
    "David Kim", "Priya Nair", "James Wilson", "Fatima Khan", "Lucas Silva",
]

<<<<<<< HEAD

def run_seed():
    app = create_app()
    with app.app_context():
        try:
            create_user("Admin User", "admin@resumevault.com", "Admin@12345", role="admin")
            print("Created admin user: admin@resumevault.com / Admin@12345")
        except ValueError as e:
            print(f"Admin user already exists: {e}")

        for i, name in enumerate(SAMPLE_NAMES):
            email = f"{name.lower().replace(' ', '.')}@example.com"
            try:
                create_resume(
                    {
                        "name": name,
                        "email": email,
                        "phone": f"+91 90000 000{i:02d}",
                        "address": "Mumbai, India",
                        "university": "State University",
                        "graduation_year": random.choice([2018, 2019, 2020, 2021, 2022]),
                        "skills": random.sample(SKILLS_POOL, k=4),
                        "experience_years": round(random.uniform(0.5, 12), 1),
                        "certifications": random.sample(["AWS Certified", "PMP", "Scrum Master"], k=1),
                        "department": random.choice(DEPARTMENTS),
                        "resume_url": "/uploads/resumes/sample.pdf",
                        "storage_path": "resumes/sample.pdf",
                        "file_type": "pdf",
                        "file_size": random.randint(100_000, 900_000),
                    }
                )
            except Exception as e:
                print(f"Skipped {name}: {e}")

        print("Seed data created successfully.")


if __name__ == "__main__":
    run_seed()
=======
with app.app_context():
    try:
        create_user("Admin User", "admin@resumevault.com", "Admin@12345", role="admin")
        print("Created admin user: admin@resumevault.com / Admin@12345")
    except ValueError as e:
        print(f"Admin user already exists: {e}")

    for i, name in enumerate(SAMPLE_NAMES):
        email = f"{name.lower().replace(' ', '.')}@example.com"
        try:
            create_resume(
                {
                    "name": name,
                    "email": email,
                    "phone": f"+91 90000 000{i:02d}",
                    "address": "Mumbai, India",
                    "university": "State University",
                    "graduation_year": random.choice([2018, 2019, 2020, 2021, 2022]),
                    "skills": random.sample(SKILLS_POOL, k=4),
                    "experience_years": round(random.uniform(0.5, 12), 1),
                    "certifications": random.sample(["AWS Certified", "PMP", "Scrum Master"], k=1),
                    "department": random.choice(DEPARTMENTS),
                    "resume_url": "/uploads/resumes/sample.pdf",
                    "storage_path": "resumes/sample.pdf",
                    "file_type": "pdf",
                    "file_size": random.randint(100_000, 900_000),
                }
            )
        except Exception as e:
            print(f"Skipped {name}: {e}")

    print("Seed data created successfully.")
>>>>>>> 6910ba463dd33db6a2340fd9a7a4732b3f75eb26
