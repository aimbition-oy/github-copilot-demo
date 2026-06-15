# Docker and orchestration

The whole stack runs with Docker Compose. Source of truth: `docker-compose.yml`,
the per-service `Dockerfile`s, and `postgres/init/`.

## Services and startup order

`postgres` -> `auth` -> `backend` -> `frontend`, wired with `depends_on` +
health checks so each waits for the one below it:

| Service  | Image / build | Host port | Depends on (healthy) |
| -------- | ------------- | --------- | -------------------- |
| postgres | postgres:16-alpine | 5432 | -               |
| auth     | `./auth`      | 8001      | postgres             |
| backend  | `./backend`   | 8000      | auth, postgres       |
| frontend | `./frontend`  | 5173      | backend, auth        |

## Conventions

- **Env vars are the configuration surface.** `JWT_SECRET` must be **identical**
  for `auth` and `backend` (the shared token contract). `DATABASE_URL` points each
  service at its own database. `CORS_ORIGINS` must include the frontend origin.
  `VITE_AUTH_URL` / `VITE_BACKEND_URL` tell the frontend where the services are.
- **The dev `JWT_SECRET` in compose is a placeholder.** Never commit a real
  secret; never hardcode secrets in a `Dockerfile`.
- **The two databases are created on first boot** by `postgres/init/`. They live in
  the named volume `arcade-data`; `make down-v` wipes it.
- **Health checks gate startup** - if you add a service that others depend on, give
  it a health check so `depends_on: condition: service_healthy` works.
- **`ENABLE_TEST_ENDPOINTS=1`** is set for `backend` in compose so demos can reset
  data; do not enable it in a real deployment.

## Commands

`make up` / `make up-d` / `make down` / `make down-v`. Full list: `make help`.

## Related

System integration: [architecture.md](architecture.md). Database details:
[database.md](database.md).
