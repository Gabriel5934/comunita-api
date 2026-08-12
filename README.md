# Comunita API

Dockerized Django REST Framework API with JWT authentication, PostgreSQL, Gunicorn, and NGINX.

```sh
cp .env.example .env
docker compose up --build
```

The API is available at `http://localhost:8000`. Useful endpoints:

- `GET /health/`
- `POST /register` (or `/register/`) with `email` and `password`
- `POST /token` (or `/token/`) with `email` and `password`
- `POST /token/refresh` with a refresh token
- `/api/auth/register/`, `/api/auth/token/`, and `/api/auth/token/refresh/`
  provide equivalent namespaced endpoints for the web client
- `/api/buildings/` for authenticated building CRUD
- `/api/forms/` for authenticated form CRUD
- `GET /api/public/buildings/{slug}/form/` for the latest public form
- `POST /api/public/submissions/` for public entrance submissions

Create an admin user with `docker compose exec api python manage.py createsuperuser`.

Email is the public login identifier. Internally, registration stores the email
as Django's username as well, keeping the project compatible with databases that
already contain Django's standard auth migrations.
