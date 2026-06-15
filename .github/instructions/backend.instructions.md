---
description: 'Conventions for the backend service (games, scores, leaderboards).'
applyTo: 'backend/**'
---

# Backend conventions

The backend owns `arcade_db` and **verifies** JWTs (it never issues them).

- **Thin routers:** every route declares `response_model=`; raise
  `HTTPException(status_code=404, detail="<Resource> not found")` for missing rows.
- **Protected routes depend on `get_current_user`** (`app/security.py`), which
  verifies the `Bearer` token with the shared `JWT_SECRET`.
- **Leaderboards** order by `Score.score.desc()` with a bounded `limit`; keep the
  query in the router thin.
- **Games seed at startup** when the table is empty (`app/seed.py`); edit the seed
  list there.
- **Test endpoints** (`/test/*`) must guard on `ENABLE_TEST_ENDPOINTS` and return
  404 when it is off.
- **Style:** PEP 8, enforced by `ruff` (`make lint-python`).

More detail: `docs/backend.md`. Database rules: `docs/database.md`. Tests: the
python-tests instructions.
