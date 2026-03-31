# UMDEHUB Dental Learning Platform

A production-ready Django MVP for dental students with notes, quizzes, mock exams, past papers, document-to-question import, moderated contributions, and role-aware login for admins and students.

## Key Production Files

- `requirements.txt`
- `Procfile`
- `runtime.txt`
- `build.sh`
- `render.yaml`
- `dental_platform/settings.py`
- `templates/registration/login.html`
- `templates/dashboard/home.html`

## Local Development

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run migrations:

```powershell
python manage.py makemigrations
python manage.py migrate
```

4. Create a superuser:

```powershell
python manage.py createsuperuser
```

5. Run the app:

```powershell
python manage.py runserver
```

## Render Deployment

### Expected Public URL

If the Render service name `umdehub-edu-rw` is available, the generated URL should be:

- `https://umdehub-edu-rw.onrender.com`

This is the closest valid Render URL format to your requested domain. Render generates `onrender.com` subdomains from the service name, so the exact hostname depends on whether that service name is available in your account at deploy time.

### Option 1: Deploy with `render.yaml`

1. Push this project to GitHub.
2. In Render, choose **New +** -> **Blueprint**.
3. Connect the GitHub repository.
4. Render will detect `render.yaml` and create:
   - A free web service named `umdehub-edu-rw`
   - A free PostgreSQL database named `umdehub-edu-rw-db`
5. After the first deploy finishes, open a Render Shell and run:

```bash
python manage.py createsuperuser
```

### Option 2: Manual Web Service Setup

1. Push this project to GitHub.
2. In Render, create a new **PostgreSQL** database.
3. Create a new **Web Service** and connect the repository.
4. Use these values:

- Build command: `./build.sh`
- Start command: `gunicorn dental_platform.wsgi:application`
- Python version: `3.11.9` via `runtime.txt`

5. Add these environment variables in Render:

- `SECRET_KEY` = generate a long random secret
- `DEBUG` = `False`
- `DATABASE_URL` = paste the Render PostgreSQL connection string
- `ALLOWED_HOSTS` = optional extra hosts if needed
- `CSRF_TRUSTED_ORIGINS` = optional extra trusted origins if you add custom domains

6. After deploy, open a Render Shell and run:

```bash
python manage.py createsuperuser
```

## Render Notes

- `build.sh` installs dependencies, runs `collectstatic`, and applies migrations.
- Static files are served with WhiteNoise.
- PostgreSQL is loaded automatically from `DATABASE_URL`.
- Production security settings are enabled when `DEBUG=False`.
- The app trusts `.onrender.com` hosts and automatically supports `RENDER_EXTERNAL_HOSTNAME` when Render provides it.

## Authentication Behavior

- Homepage buttons:
  - `Login as Student`
  - `Login as Admin`
  - `Register`
- Login flow:
  - Staff users are redirected to `/admin/`
  - Non-staff users are redirected to `/dashboard/`

## Admin Checklist After Deployment

- Create subjects, topics, notes, questions, and past papers in Django Admin
- Review student contributions before approving them
- Use the staff question import page to upload `.docx` and text-based `.pdf` question files
- Publish imported questions after selecting the correct answer for each one
