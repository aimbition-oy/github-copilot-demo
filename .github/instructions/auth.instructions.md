---
description: 'Conventions for the auth service (registration, login, JWT issuance).'
applyTo: 'auth/**'
---

# Auth service conventions

Auth owns `auth_db` and is the **only** service that issues JWTs.

- **Passwords use bcrypt** (`app/security.py`). Never store or log plaintext, and
  never return `password_hash` (keep it out of `UserResponse`).
- **JWT issuance is HS256**, signed with `JWT_SECRET`, carrying `sub` (user id) and
  `username`, expiring after `token_expire_hours`. Mint tokens in
  `app/security.py`.
- **Status codes:** `/register` returns 201, duplicate username is 409; bad
  credentials or an invalid/missing token is 401 with a generic message (do not
  reveal whether a username exists).
- **Validation lives in `app/schemas.py`** (Pydantic `Field`); change username and
  password constraints there, not inline in the router.
- **Style:** PEP 8, enforced by `ruff` (`make lint-python`).

More detail: `docs/auth.md`. The JWT contract with the backend:
`docs/architecture.md`.
