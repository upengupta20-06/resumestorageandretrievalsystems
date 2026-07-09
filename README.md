# Resume Storage and Retrieval System

A cloud-based HR dashboard for uploading, storing, searching, and managing
candidate resumes. Built with Flask, MongoDB Atlas, and Bootstrap 5, with
pluggable cloud file storage (Firebase Storage or AWS S3).

## Tech Stack
- **Backend:** Python Flask (modular blueprints)
- **Database:** MongoDB Atlas
- **File Storage:** Firebase Storage or AWS S3 (local filesystem fallback for dev)
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5, Chart.js
- **Auth:** Session-based, hashed passwords (Werkzeug/bcrypt)

## Project Structure
```
project/
├── app.py                 # App factory & entry point
├── config.py               # Environment-driven configuration
├── requirements.txt
├── seed_data.py             # Creates a demo admin user + sample resumes
├── routes/                  # Blueprints: auth, dashboard, resume, search, analytics, admin, settings
├── models/                  # MongoDB collection wrappers: users, resumes, logs
├── utils/                   # storage.py (cloud abstraction), validators, decorators, exporters
├── templates/                # Jinja2 HTML templates
└── static/
    ├── css/style.css
    ├── js/main.js
    └── images/
```

## Deploying to Vercel

This repo includes a `vercel.json` that routes all traffic to the Flask
`app` object exposed at module level in `app.py`. To deploy:

1. Push this repo to GitHub and import it in Vercel.
2. In **Project Settings → Environment Variables**, set at minimum:
   - `SECRET_KEY`
   - `MONGO_URI` (your MongoDB Atlas connection string)
   - `STORAGE_PROVIDER` — **must be `firebase` or `s3` on Vercel** (see below)
   - Plus the matching Firebase or AWS credentials
3. Redeploy.

**Important:** Vercel's serverless filesystem is read-only and ephemeral —
files written to disk during one request are not guaranteed to exist on the
next. `STORAGE_PROVIDER=local` only works for local development on your own
machine; on Vercel you must set `STORAGE_PROVIDER=firebase` or `s3` so
uploaded resumes actually persist in real cloud storage.

`seed_data.py` is a standalone script (not the web entrypoint) — run it
locally with `python seed_data.py` against your Atlas cluster; don't expect
Vercel to execute it automatically.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in:
   - `MONGO_URI` — your MongoDB Atlas connection string
   - `SECRET_KEY` — a long random string
   - `STORAGE_PROVIDER` — `local` (default, for development), `firebase`, or `s3`
   - Firebase or AWS credentials if you set a cloud provider

3. **Load environment variables and run**
   ```bash
   export $(cat .env | xargs)   # or use python-dotenv / your shell's env loader
   python app.py
   ```
   The app runs on `http://localhost:5000` by default.

4. **Seed demo data (optional)**
   ```bash
   python seed_data.py
   ```
   Creates an admin login: `admin@resumevault.com` / `Admin@12345`
   (change this password immediately in a real deployment).

## Switching Storage Providers

Set `STORAGE_PROVIDER=firebase` and provide `FIREBASE_CREDENTIALS_JSON`
(path to your service account JSON) and `FIREBASE_STORAGE_BUCKET`.

Set `STORAGE_PROVIDER=s3` and provide `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`, and `AWS_REGION`.

Only the resulting file URL is ever stored in MongoDB — raw files always
live in the configured storage backend, never in the database.

## Security Notes
- Passwords are hashed with Werkzeug's `generate_password_hash` (never stored in plaintext).
- All dashboard routes are protected with a `login_required` decorator; admin-only routes additionally use `role_required("admin")`.
- File uploads are validated for extension (`pdf`, `doc`, `docx`) and size (10 MB max) before being sent to storage.
- Session cookies are `HttpOnly` and `SameSite=Lax`; set `SESSION_COOKIE_SECURE=True` in production behind HTTPS.
- Never commit `.env` or real cloud credentials to version control.

## Notes on This Build
This scaffold is fully wired end-to-end (routes, MongoDB models, storage
abstraction, templates) and ready to run against a real MongoDB Atlas
cluster. A few things worth knowing before treating it as production-ready:
- CSRF protection: `Flask-WTF` is included in requirements; wire up
  `CSRFProtect(app)` in `app.py` and add `{{ csrf_token() }}` hidden fields
  to forms before deploying publicly.
- Email delivery (password reset, upload notifications) is stubbed 
  the routes exist but don't send real email yet; plug in an email
  provider (e.g., SendGrid, SES) in `routes/auth_routes.py` and the
  notification logic.
- Duplicate resume detection currently matches on email; extend with
  file-hash comparison in `utils/storage.py` if you want content-level
  duplicate detection too.
