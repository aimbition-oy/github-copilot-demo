---
description: 'Conventions for backend and auth tests (pytest).'
applyTo: 'backend/tests/**, auth/tests/**'
---

# Python test conventions

Both Python services test the same way.

- **Test database is in-memory SQLite** via FastAPI `dependency_overrides`
  (`tests/conftest.py`). Unit and integration tiers never touch Postgres.
- **Mark integration tests** with the `integration` pytest marker (declared in each
  `pyproject.toml`); leave unit tests unmarked and fast.
- **Use the app `TestClient`** with overridden `get_db` and `get_settings`; do not
  start a real server for these tiers.
- **Mint JWTs with the test secret** (`make_token` in `conftest.py`), HS256, to
  match `app/security.py`.
- **Style:** PEP 8, enforced by `ruff`.

More detail: `docs/python-testing.md`.
