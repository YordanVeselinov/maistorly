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
- `TIME_ZONE`
- `DB_ENGINE`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
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
poetry run python manage.py collectstatic
```

## API Endpoints

- `GET /api/jobs/`
- `GET /api/jobs/<id>/`
- `POST /api/jobs/`
- `GET /api/craftsmen/`
- `GET /api/craftsmen/<id>/`

## Deployment Notes

- Set `DEBUG=False`
- Use a strong production `SECRET_KEY`
- Configure real `ALLOWED_HOSTS`
- Use production PostgreSQL and Redis services
- Use a real email backend instead of the console backend
- Run `poetry run python manage.py collectstatic`
- Run Celery worker processes separately from the web app
- Serve static/media with your web server or storage provider

This setup is intentionally minimal and suitable for exam submission, local demos, and later deployment hardening.
