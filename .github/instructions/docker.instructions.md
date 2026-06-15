---
description: 'Conventions for Docker Compose, Dockerfiles, and Postgres init.'
applyTo: '**/Dockerfile, docker-compose.yml, postgres/**'
---

# Docker and orchestration conventions

- **`JWT_SECRET` must be identical for `auth` and `backend`** - it is the shared
  token contract. Never commit a real secret or hardcode one in a `Dockerfile`;
  the value in compose is a dev placeholder.
- **Each service's `DATABASE_URL`** points at its own database (`auth_db`,
  `arcade_db`); `CORS_ORIGINS` must include the frontend origin; the frontend reads
  `VITE_AUTH_URL` / `VITE_BACKEND_URL`.
- **Services that others depend on need a health check** so
  `depends_on: condition: service_healthy` works.
- **The two databases are created on first boot** by `postgres/init/` and persist
  in the `arcade-data` volume (`make down-v` wipes it).
- **`ENABLE_TEST_ENDPOINTS`** is for demos/tests only; never enable it in a real
  deployment.

More detail: `docs/docker.md`. Database details: `docs/database.md`.
