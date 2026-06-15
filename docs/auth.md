# Auth service

FastAPI service for user registration, login, and JWT issuance. Owns the
`auth_db` database. It is the only service that mints tokens. Source of truth:
`auth/`.

## Endpoints

Router: `auth/app/routers/auth.py`. Schemas: `auth/app/schemas.py`.

| Method and path | Auth   | Description                                          |
| --------------- | ------ | ---------------------------------------------------- |
| `POST /register`| no     | Create a user. 201 on success, 409 if name taken.   |
| `POST /login`   | no     | Verify credentials, return a JWT. 401 on bad creds. |
| `GET /me`       | Bearer | Current user from the token. 401 if missing/invalid.|
| `GET /health`   | no     | Health check.                                       |

## Conventions

- **Passwords are hashed with bcrypt** (`app/security.py`). Never store or log
  plaintext; never return `password_hash` in a response (`UserResponse` omits it).
- **JWT issuance is HS256**, signed with `JWT_SECRET`, carrying `sub` (user id) and
  `username`, expiring after `token_expire_hours` (`app/config.py`). Issuing lives
  in `app/security.py` (`create_access_token`).
- **`/register` returns 201**; a duplicate username is `409 Conflict`.
- **`/login` and `/me` return 401** for bad credentials or an invalid/missing
  token, with a generic message (do not reveal whether the username exists).
- **Username/password constraints** are declared in `app/schemas.py` (Pydantic
  `Field`); change them there, not inline in the router.
- Python style follows PEP 8, enforced by `ruff` (`make lint-python`).

## Related

The JWT contract with `backend` (it verifies what auth issues):
[architecture.md](architecture.md). Data model: [database.md](database.md).
Tests: [python-testing.md](python-testing.md).
