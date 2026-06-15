# Retro High-Score Arcade - agent instructions

Repo-wide agent instructions. This file is loaded into every session, so it is
short and contains only rules that hold everywhere. Commands live in the
`Makefile`; stack, domain, and API detail live in `docs/` and in the code.
This file points to those sources instead of repeating them, so it cannot drift
out of sync with the project.

## What this is

A three-service NES-themed arcade leaderboard, built to demo GitHub Copilot
customization. Players register, log in, submit high scores, and view per-game
leaderboards.

- `frontend/` - React + Vite + TypeScript (port 5173)
- `backend/` - FastAPI scores/games API (port 8000)
- `auth/` - FastAPI registration/login/JWT service (port 8001)
- `postgres` + `docker-compose.yml` - orchestration

## Commands

All commands are in the `Makefile`. Run `make help` to list them, or open the
`Makefile` (each recipe shows the underlying tool command). Run `make lint` and
`make test-unit` before declaring work done; the full `make test` also needs the
running Docker stack for E2E.

## Architecture

Both Python services share one layout: `routers/` (HTTP) -> `db.py` /
`models.py` / `schemas.py` (data) with `security.py` (JWT) and `config.py`
(settings). The two services never import each other; they communicate only over
HTTP and a shared JWT secret. Map and request flow: `docs/architecture.md`.

## Rules

These hold everywhere. Breaking them breaks tests, security, or the stack.

- **Python deps via `uv` only** (never global `pip`). Node deps via `npm`.
- **Database access goes through a SQLAlchemy session** injected with
  `Depends(get_db)`. Never open a connection in a router. The DB is chosen by the
  `DATABASE_URL` env var (PostgreSQL in Docker, SQLite locally and in tests), so
  do not assume a specific database in code.
- **JWT is HS256**, signed with the secret from the `JWT_SECRET` env var. `auth`
  issues tokens, `backend` verifies them, and both must share the same secret.
  Never hardcode or log it.
- **Passwords are hashed with bcrypt** (in `auth`). Never store or log plaintext.
- **Routers declare `response_model=`** on every route and raise
  `HTTPException(status_code, "<Resource> not found")` for missing rows.
- **Frontend talks to APIs through `src/lib/api*.ts`**, never raw `fetch` in
  components. Base URLs come from `import.meta.env.VITE_AUTH_URL` /
  `VITE_BACKEND_URL`. Styling uses `nes.css`.
- **Tests use in-memory SQLite + FastAPI `dependency_overrides`**; mark
  integration tests with the `integration` pytest marker.
- **Style:** Python follows PEP 8, enforced by `ruff`; the frontend by ESLint.
  Don't hand-fix what the linter owns.

## Boundaries

- **Always:** keep changes small and within one service; run `make lint` and
  `make test-unit` before finishing.
- **Ask first:** new dependencies; changes that cross service boundaries or
  change the shared JWT contract; schema changes.
- **Never:** read or print `.env` files or the JWT secret; commit a real secret;
  edit `node_modules` or `.venv`.

## Where to look

- `docs/architecture.md` - how the whole system integrates (start here)
- `docs/domain.md` - business concepts and where the values live
- `docs/` - per-domain references: `frontend`, `backend`, `auth`, `database`,
  `docker`, plus `frontend-testing`, `e2e`, `python-testing`
- `.github/instructions/` - per-path rules applied automatically by `applyTo`
- `.github/hooks/` - deterministic guardrails (secret/destructive-command gate,
  write-zone enforcement, auto-format); decisions logged to `agent-runs/audit/`
- `docs/agentic-workflows.md` - the two coordinator workflows + shared protocol
- `.github/agents/` - coordinators (Feature Builder, Refactor Lead) + shared
  subagents (Researcher, Test Lead, Integrator, Implementer, Doc Writer)
- `.github/skills/` - kickoff (`/build-feature`, `/refactor`) + reusable skills
- `README.md` - quickstart, troubleshooting, and Copilot demo ideas
