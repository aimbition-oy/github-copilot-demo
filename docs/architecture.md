# Architecture (whole system)

How the pieces fit together. This doc is the system map; each domain has its own
doc (linked below) for detail. The code and `docker-compose.yml` are the source
of truth.

## Services

| Service  | Port | Stack                                             | Doc                         |
| -------- | ---- | ------------------------------------------------- | --------------------------- |
| frontend | 5173 | React 18, Vite, TypeScript, react-router, nes.css | [frontend](frontend.md)     |
| backend  | 8000 | FastAPI, SQLAlchemy 2.0, PyJWT                     | [backend](backend.md)       |
| auth     | 8001 | FastAPI, SQLAlchemy 2.0, bcrypt, PyJWT            | [auth](auth.md)             |
| postgres | 5432 | PostgreSQL 16 (Docker only)                        | [database](database.md)     |

Orchestration and env wiring: [docker.md](docker.md) and `docker-compose.yml`.

## How they integrate

```
browser -> frontend (:5173)
              |  VITE_AUTH_URL        |  VITE_BACKEND_URL
              v                       v
           auth (:8001)            backend (:8000)
              |                       |
              +------ PostgreSQL (:5432) ------+
                 auth_db            arcade_db
```

- **Frontend to services.** The frontend calls `auth` and `backend` directly over
  HTTP; base URLs come from `VITE_AUTH_URL` / `VITE_BACKEND_URL`. CORS allows the
  frontend origin (`CORS_ORIGINS`). The two clients live in
  `frontend/src/lib/apiAuth.ts` and `apiBackend.ts`.
- **The JWT trust boundary.** `auth` issues a JWT (HS256) on login; `backend`
  verifies it on protected routes. They never call each other - they share only
  the `JWT_SECRET` and the token claims (`sub` = user id, `username`). This is the
  one contract that ties the services together. Issue: `auth/app/security.py`.
  Verify: `backend/app/security.py`.
- **Two databases, one Postgres.** `auth_db` (users) and `arcade_db` (games,
  scores) are separate databases created by `postgres/init/`. `scores.user_id`
  mirrors `users.id` by value; there is **no cross-database foreign key**. Details:
  [database.md](database.md).
- **A contract test guards the seam.** `backend/tests/integration/` imports the
  auth service to check that a token `auth` issues is one `backend` accepts. If
  the JWT contract drifts, this test fails.

## Shared service layout

Both Python services use the same layering (one-way: a layer imports only those
below it):

```
routers/  ->  schemas.py / models.py / db.py
              security.py (JWT)   config.py (settings)
```

| Layer    | Responsibility                                | Path              |
| -------- | --------------------------------------------- | ----------------- |
| Routers  | HTTP only: validate, call DB, return schema   | `app/routers/`    |
| Schemas  | Pydantic request/response models              | `app/schemas.py`  |
| Models   | SQLAlchemy ORM tables                          | `app/models.py`   |
| DB       | Engine, session, `get_db`, seeding            | `app/db.py`       |
| Security | JWT issue (auth) / verify (backend)           | `app/security.py` |
| Config   | Env-driven settings (`get_settings`, cached)  | `app/config.py`   |

## End-to-end flow

A typical session ties every service together:

1. **Register / login** - frontend posts to `auth`; `auth` returns a JWT.
2. **Submit a score** - frontend posts to `backend` with the `Bearer` token;
   `backend` verifies it, looks up the game, inserts a `Score`.
3. **View leaderboard** - frontend reads `backend`; `backend` returns the top
   scores for the game ordered by score.
4. **View score history** - frontend reads `backend` (no token needed); `backend`
   joins `Score` to `Game` and returns the player's scores ordered by date.

Business concepts (users, games, scores, leaderboards): [domain.md](domain.md).
Per-domain conventions live in `.github/instructions/` and the docs linked above.
