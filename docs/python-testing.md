# Python testing (backend + auth)

Both Python services test the same way with pytest. Unit tests need no running
services; integration tests exercise the FastAPI app in-process against a test
database. Source of truth: each service's `pyproject.toml` and `tests/conftest.py`.

## Layout

```
backend/tests/unit/         auth/tests/unit/
backend/tests/integration/  auth/tests/integration/   (carry the integration marker)
```

`backend/tests/integration/` also holds the cross-service **contract test** that
imports the auth service to verify the shared JWT contract.

## Conventions

- **Test database is in-memory SQLite** via FastAPI `dependency_overrides`
  (`tests/conftest.py`) - independent of the running stack, so unit/integration
  runs never touch Postgres.
- **Mark integration tests** with the `integration` pytest marker (declared in
  each `pyproject.toml`); unit tests stay unmarked and fast.
- **Use the `TestClient`** from the app with overridden `get_db` and
  `get_settings`; do not spin up a real server for these tiers.
- **Mint JWTs with the test secret** (`make_token` in `conftest.py`) and keep them
  HS256 to match `app/security.py`.
- Python style follows PEP 8, enforced by `ruff`.

## Running

`make test-unit` (unit, no services) and `make test-integration` (marked
integration). Single service: `cd backend && uv run pytest tests/unit -v`. Full
list: `make help`.

Browser-level tests are separate: [e2e.md](e2e.md).
