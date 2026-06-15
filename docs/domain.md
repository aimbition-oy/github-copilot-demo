# Domain

Concepts and rules, with pointers to where the values and logic live. Actual
values are in the code; this file does not copy them, so it cannot drift.

## Concepts

- **User** - a player. Owned by the `auth` service (`auth_db`). Model:
  `auth/app/models.py`.
- **Game** - an arcade title with a unique `slug`. Owned by `backend`
  (`arcade_db`). Model: `backend/app/models.py`.
- **Score** - a submitted high score, tied to a user and a game. `user_id`
  mirrors `auth` `users.id`; `username_cached` is denormalized for fast
  leaderboards. Model: `backend/app/models.py`.
- **Leaderboard** - the top scores for a game, ordered by score descending.
  Built in `backend/app/routers/scores.py`.
- **Score history** - all scores submitted by a player, ordered by `achieved_at`
  descending. Built in `backend/app/routers/users.py`.

## Where values and rules live

- **Seeded game catalogue:** `backend/app/seed.py` (the source of truth for which
  games exist; seeded on startup if the table is empty).
- **Registration and login rules** (username/password constraints, conflict and
  auth errors): `auth/app/routers/auth.py` and `auth/app/schemas.py`.
- **Score validation** (e.g. non-negative score) and response shapes:
  `backend/app/schemas.py`.
- **JWT claims and verification:** `auth/app/security.py` (issue),
  `backend/app/security.py` (verify). Tokens carry the user id (`sub`) and
  `username`.

## Cross-service contract

`auth` issues a JWT; `backend` trusts it. The two services share only the
`JWT_SECRET` and the token claims - they do not share a database and never call
each other directly. A contract test guards this: `backend/tests/integration/`.
