# Maistorly

Maistorly is a Django-based home repair marketplace where customers can post job requests, craftsmen can submit offers, and completed jobs can be reviewed. The project includes HTML pages, a small DRF API, and minimal Celery-based async processing for offer email notifications.

## Main Features

- Email-based authentication with customer profiles
- Job requests, offers, reviews, and craftsmen profiles
- Public pages plus owner-scoped management flows
- DRF endpoints for jobs and craftsmen
- Celery task for new-offer email notifications

## Stack

- Python 3.14
- Django 6
- PostgreSQL
- Redis
- Django REST Framework
- Celery
- Poetry

## Local Setup

1. Install Poetry if it is not already available.
2. Install dependencies from the lock file:

```bash
poetry install
```

3. Copy `.env.example` to `.env` and update the values for your machine.
4. Create the PostgreSQL database configured in `.env`.
5. Run migrations:

```bash
poetry run python manage.py migrate
```

6. Start the development server:

```bash
poetry run python manage.py runserver
```

## Environment Variables

Required and commonly used variables are documented in `.env.example`.

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `SECURE_SSL_REDIRECT`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SECURE_HSTS_SECONDS`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`
- `TIME_ZONE`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DB_SSLMODE`
- `DB_CONN_MAX_AGE`
- `EMAIL_BACKEND`
- `DEFAULT_FROM_EMAIL`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `CELERY_TASK_ALWAYS_EAGER`
- `CELERY_TASK_EAGER_PROPAGATES`
- `STATIC_URL`
- `STATIC_ROOT`
- `MEDIA_URL`
- `MEDIA_ROOT`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## PostgreSQL and Redis

### PostgreSQL

Example local PostgreSQL setup:

- database: `maistorly_db`
- user: `postgres`
- host: `127.0.0.1`
- port: `5432`

Create the database before running migrations.

### Redis

Celery uses Redis as broker and result backend.

Default local values:

- broker: `redis://127.0.0.1:6379/0`
- result backend: `redis://127.0.0.1:6379/1`

Start Redis locally before running Celery.

## Running Migrations

```bash
poetry run python manage.py makemigrations
poetry run python manage.py migrate
```

## Running Celery

Start a worker from the `backend` directory:

```bash
poetry run celery -A maistorly worker --loglevel=info
```

For local development without Redis, you can temporarily set:

```env
CELERY_TASK_ALWAYS_EAGER=True
```

That makes tasks run synchronously in-process.

## Running Tests

Run the full project tests:

```bash
poetry run python manage.py test
```

Run selected apps:

```bash
poetry run python manage.py test accounts jobs reviews craftsmen services
```

## Static and Media Files

Development settings now include:

- `STATIC_URL` and `STATIC_ROOT`
- Cloudinary-backed media upload settings

Uploaded media files are stored in Cloudinary. Static files remain local and are collected with Django.

For deployment, collect static files with:

```bash
poetry run python manage.py collectstatic --noinput
```

## API Endpoints

- `GET /api/jobs/`
- `GET /api/jobs/<id>/`
- `POST /api/jobs/`
- `GET /api/craftsmen/`
- `GET /api/craftsmen/<id>/`

## Azure App Service Deployment

Target platform:

- Azure App Service on Linux
- Azure Database for PostgreSQL
- Cloudinary for uploaded media
- Gunicorn for WSGI
- WhiteNoise for collected static files

Keep Poetry as the package manager for local dependency management. The Azure App Service deployment uses Oryx build automation and installs runtime packages from `backend/requirements.txt`.

Example dependency install command for a deployment pipeline that runs from the repository root:

```bash
pip install -r backend/requirements.txt
```

### Required Azure App Settings

Set these in Azure App Service Configuration. Do not commit production values to the repository.

```env
SECRET_KEY=<strong-production-secret>
DEBUG=False
ALLOWED_HOSTS=<app-name>.azurewebsites.net,<custom-domain>
CSRF_TRUSTED_ORIGINS=https://<app-name>.azurewebsites.net,https://<custom-domain>
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False

DB_ENGINE=django.db.backends.postgresql
DB_NAME=<postgres-database>
DB_USER=<postgres-user>
DB_PASSWORD=<postgres-password>
DB_HOST=<postgres-host>
DB_PORT=5432
DB_SSLMODE=require
DB_CONN_MAX_AGE=60

STATIC_URL=/static/
STATIC_ROOT=staticfiles
MEDIA_URL=/media/

SCM_DO_BUILD_DURING_DEPLOYMENT=true
POST_BUILD_COMMAND=cd backend && python manage.py collectstatic --noinput

CLOUDINARY_CLOUD_NAME=<cloudinary-cloud-name>
CLOUDINARY_API_KEY=<cloudinary-api-key>
CLOUDINARY_API_SECRET=<cloudinary-api-secret>
```

Also configure production values for email, Redis, and Celery if those services are used by the deployed environment. `SCM_DO_BUILD_DURING_DEPLOYMENT=true` enables Oryx during deployment. `POST_BUILD_COMMAND` runs after dependencies are installed and must `cd backend` before running `collectstatic` because the Django project lives in the `backend/` directory.

Leave `SECURE_SSL_REDIRECT=False` when Azure App Service HTTPS Only is enabled. Set it to `True` only if Django should perform HTTPS redirects itself. Increase `SECURE_HSTS_SECONDS` only after the production domain is confirmed to serve HTTPS correctly.

### Deployment Checklist

- Keep `backend/requirements.txt` synchronized with Poetry dependencies so Azure installs the same runtime packages.
- Run migrations after the database settings are configured:

```bash
cd backend && python manage.py migrate
```

- Let Azure run collectstatic during Oryx deployment through `POST_BUILD_COMMAND`:

```bash
cd backend && python manage.py collectstatic --noinput
```

- Static files are collected into `STATIC_ROOT` and served by WhiteNoise from the Django app.
- Uploaded media files are stored in Cloudinary through `django-cloudinary-storage`; App Service local storage is not used for media.
- Set the Azure App Service startup command. The WSGI entry point is `maistorly.wsgi:application`, and Gunicorn is included in the production dependencies.

```bash
gunicorn --chdir backend maistorly.wsgi:application --bind=0.0.0.0 --timeout 600
```

- Run Celery worker processes separately from the web App Service if asynchronous jobs are enabled.
