---
description: 'Conventions for SQLAlchemy models and database access.'
applyTo: '**/app/db.py, **/app/models.py'
---

# Database conventions

- **SQLAlchemy 2.0 typed style:** `Mapped[...]` + `mapped_column(...)`; models
  inherit `Base` from `app.db`.
- **Sessions only through `Depends(get_db)`** (`app/db.py`). Never construct an
  engine or open a connection in a router or service helper.
- **Models are the schema source of truth.** There are no migrations; tables come
  from `Base.metadata.create_all` at startup (`init_db()`). Change the schema by
  editing the models. (A real app would add Alembic.)
- **Stay database-agnostic:** code runs on PostgreSQL (Docker) and SQLite (local
  and tests). Avoid backend-specific SQL.
- **Two databases, no cross-database FK:** `scores.user_id` mirrors `users.id` by
  value; `scores.username_cached` is denormalized for leaderboard speed.
- **Seeding is idempotent** - insert only when the table is empty.

More detail: `docs/database.md`. Business concepts: `docs/domain.md`.
