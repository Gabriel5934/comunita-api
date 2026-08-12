# Backend guidance

- Keep Django settings environment-driven and never hard-code secrets.
- Build API endpoints with Django REST Framework and protect non-public endpoints with JWT permissions.
- Keep container changes reproducible and preserve the `/health/` readiness endpoint.
- Run `docker compose config` and Django checks after infrastructure or backend changes.
