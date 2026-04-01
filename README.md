# UMOL'S DENTAL HUB

A production-ready Django MVP for dental students with notes, quizzes, mock exams, past papers, document-to-question import, moderated contributions, and role-aware login for admins, students, and practitioners.

## Key Production Files

- `requirements.txt`
- `Procfile`
- `runtime.txt`
- `build.sh`
- `render.yaml`
- `railway.json`
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

If you need to recreate the local trial admin safely, use:

```powershell
python manage.py bootstrap_admin
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
- `EMAIL_HOST` = your SMTP host
- `EMAIL_PORT` = your SMTP port, usually `587`
- `EMAIL_HOST_USER` = your SMTP username
- `EMAIL_HOST_PASSWORD` = your SMTP password or app password
- `EMAIL_USE_TLS` = `True` for most providers
- `DEFAULT_FROM_EMAIL` = sender address for platform notifications
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
- The app now fails fast if `DATABASE_URL` is missing while `DEBUG=False`, which prevents accidental live fallbacks to SQLite.
- Production security settings are enabled when `DEBUG=False`.
- The app trusts `.onrender.com` hosts and automatically supports `RENDER_EXTERNAL_HOSTNAME` when Render provides it.
- Fallback bootstrap admin creation is disabled in production unless `BOOTSTRAP_ADMIN_ENABLED=True` is set explicitly.
- Practitioner-request emails and contribution-review emails use SMTP automatically when the `EMAIL_*` variables are configured.

## Railway Deployment

### Railway Setup

1. Push this project to GitHub.
2. In Railway, create a new project from the GitHub repository.
3. Add a PostgreSQL service to the project.
4. In the web service, make sure these variables exist:

- `SECRET_KEY` = generate a strong secret
- `DEBUG` = `False`
- `DATABASE_URL` = use Railway's Postgres connection string or reference variable

5. Railway will use:

- `railway.json` for the start command
- `Procfile` as a fallback
- `.python-version` to pin Python `3.11.9`

6. After the first deploy, open the Railway shell and run:

```bash
python manage.py createsuperuser
```

### Railway Notes

- The app accepts Railway's public domain via `RAILWAY_PUBLIC_DOMAIN`.
- If `DATABASE_URL` is not set but Railway exposes `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, and `PGPORT`, the app can build the Postgres URL automatically.
- The `gunicorn` command binds to Railway's injected `PORT`, which is required for a successful boot.

## Authentication Behavior

- Homepage buttons:
  - `Login as Student`
  - `Login as Practitioner`
  - `Login as Admin`
  - `Register`
- Login flow:
  - Staff users are redirected to `/admin/`
  - Approved practitioners are redirected to `/practitioner/cases/`
  - Students are redirected to `/dashboard/`

## Admin Checklist After Deployment

- Create subjects, topics, notes, questions, and past papers in Django Admin
- Review student contributions before approving them
- Review practitioner signup requests at `/admin/users/profile/practitioner-requests/`
- Use the staff question import page to upload `.docx` and text-based `.pdf` question files
- Publish imported questions after selecting the correct answer for each one

## Trial Readiness Notes

- Uploaded files still use the app filesystem by default. For an official launch, move media storage to persistent disk or cloud object storage before relying on long-term uploads.
- Run the regression suite before each release:

```powershell
python manage.py test
```
