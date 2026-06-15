# Database

Both Python services use SQLAlchemy 2.0 with an env-driven `DATABASE_URL`. The ORM
models are the source of truth for the schema - tables are created from them at
startup, not from hand-written SQL or migrations.

## Where the database lives

`DATABASE_URL` is read in `*/app/config.py`:

- **Docker stack:** PostgreSQL 16, two separate databases `auth_db` and
  `arcade_db`, created by `postgres/init/01-create-databases.sql`.
- **Local default:** a SQLite file next to the service.
- **Tests:** in-memory SQLite (`tests/conftest.py`).

`init_db()` in `app/db.py` calls `Base.metadata.create_all` and seeds.

## Models (source of truth)

- `auth/app/models.py` - `users` (owned by the auth service, `auth_db`).
- `backend/app/models.py` - `games` and `scores` (owned by the backend,
  `arcade_db`).

Use the SQLAlchemy 2.0 typed style: `Mapped[...]` + `mapped_column(...)`, models
inherit `Base` from `app.db`.

## Conventions

- **Sessions only through `Depends(get_db)`** (`app/db.py`). Never construct an
  engine or open a connection inside a router or service helper.
- **No migrations:** schema changes are made by editing the models; tables come
  from `create_all` at startup. (This is a demo; a real app would add Alembic.)
- **Do not assume a specific database** in code - it must work on both Postgres and
  SQLite, so avoid backend-specific SQL.
- **Two databases, no cross-database FK.** `scores.user_id` mirrors `users.id` by
  value only; `scores.username_cached` is denormalized for leaderboard speed.
- **Seeding is idempotent** (`backend/app/seed.py`): it inserts games only when the
  table is empty.

## Related

System view and the two-database rationale: [architecture.md](architecture.md).
Business concepts: [domain.md](domain.md).
