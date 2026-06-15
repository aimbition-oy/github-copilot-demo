# Backend service

FastAPI service for the game catalogue, score submission, and leaderboards. Owns
the `arcade_db` database. Verifies (does not issue) JWTs. Source of truth:
`backend/`.

## Endpoints

Routers: `backend/app/routers/` (`games.py`, `scores.py`, `users.py`). Schemas:
`backend/app/schemas.py`.

| Method and path                      | Auth   | Description                                  |
| ------------------------------------ | ------ | -------------------------------------------- |
| `GET /games`                         | no     | List the game catalogue.                     |
| `GET /games/{slug}`                  | no     | One game by slug. 404 if unknown.            |
| `GET /games/{slug}/leaderboard`      | no     | Top scores, `?limit=` 1-100 (default 10).    |
| `POST /scores`                       | Bearer | Submit a score. 201; 404 if game unknown.    |
| `GET /users/{username}/scores`       | no     | Score history for a player, `?limit=` 1-100 (default 10), ordered `achieved_at DESC`. Unknown username returns `200 []` (backend has no User table; a 404 would require a cross-service call to `auth`). |
| `GET /health`                        | no     | Health check.                                |
| `DELETE /test/scores`                | no     | Test helper; only when `ENABLE_TEST_ENDPOINTS=1`, else 404. |

## Conventions

- **Every route declares `response_model=`**; shapes live in `schemas.py`.
- **Missing rows raise** `HTTPException(status_code=404, detail="<Resource> not found")`.
- **Protected routes depend on `get_current_user`** (`app/security.py`), which
  verifies the `Bearer` JWT with the shared `JWT_SECRET`. The backend never issues
  tokens.
- **Leaderboards** order by `Score.score.desc()` with a bounded `limit`; keep the
  query in the router thin (see `routers/scores.py`).
- **Score history** (`routers/users.py`) joins `Score` to `Game`, filters by
  `username_cached`, and orders by `achieved_at DESC`. An unknown username returns
  `200 []` — the backend owns no User table, so a 404 would require a
  cross-service call to `auth`. Response schema: `PlayerScoreOut` (`schemas.py`).
- **Games are seeded at startup** if the table is empty (`app/seed.py`, via
  `init_db()`).
- **The `/test` router is always registered** but each handler returns 404 unless
  `ENABLE_TEST_ENDPOINTS` is set, so test overrides work without leaking in prod.
- Python style follows PEP 8, enforced by `ruff` (`make lint-python`).

## Related

Shared layering and the JWT contract: [architecture.md](architecture.md).
Data model and rules: [database.md](database.md), [domain.md](domain.md).
Tests: [python-testing.md](python-testing.md).
