# 🕹️ Retro High-Score Arcade — Copilot Training Demo

A purpose-built, three-service NES-themed arcade leaderboard application designed to demonstrate **GitHub Copilot customization** features: repo-level instructions, path-scoped instructions, reusable prompts, skills, custom agent modes, and MCP server integration.

Players register, log in, submit high scores for classic NES games (Super Mario Bros., The Legend of Zelda, Metroid …), and compete on per-game leaderboards. The stack is intentionally simple so that demos stay focused on Copilot behavior rather than framework complexity.

> **Agent harness:** repo-wide rules live in [`AGENTS.md`](AGENTS.md); architecture, domain, API, and testing detail live in [`docs/`](docs/). Commands live in the `Makefile` (`make help`). The multi-agent workflows are described under [Agentic workflows](#agentic-workflows) below, with runnable items in [`BACKLOG.md`](BACKLOG.md).

---

## Architecture

| Service      | Port | Tech                         | Responsibility                                    |
|--------------|------|------------------------------|---------------------------------------------------|
| `frontend`   | 5173 | React + Vite + TypeScript (nes.css) | NES-styled UI — leaderboards, login, score entry  |
| `backend`    | 8000 | FastAPI + SQLAlchemy (via `uv`)     | Scores, games, leaderboard API                    |
| `auth`       | 8001 | FastAPI + SQLAlchemy (via `uv`)     | User registration, login, JWT issuance            |

All services run as Docker containers against a PostgreSQL 16 instance that holds two databases (`arcade_db`, `auth_db`, created by `postgres/init/`). The named volume `arcade-data` persists the Postgres data. SQLAlchemy makes the database configurable via `DATABASE_URL`, so local runs default to SQLite and tests use in-memory SQLite.

```
┌─────────────────────────────────────────────────────┐
│                   Browser                           │
└──────────────────────┬──────────────────────────────┘
                       │ :5173
              ┌────────▼────────┐
              │    frontend     │
              │  React / Vite   │
              └──┬──────────┬───┘
          :8000  │          │  :8001
     ┌───────────▼──┐  ┌────▼──────────┐
     │   backend    │  │     auth      │
     │  FastAPI     │  │   FastAPI     │
     └───────┬──────┘  └───────┬───────┘
             │  :5432          │
        ┌────▼─────────────────▼────┐
        │   PostgreSQL 16           │
        │  arcade_db   auth_db      │
        └───────────────────────────┘
```

---

## Quickstart

### Prerequisites

- **Docker** ≥ 24 with Compose v2 (`docker compose`)
- **Node** 20 (for local frontend development outside Docker)
- **Python** 3.12 (for local backend/auth development outside Docker)
- **uv** — fast Python package manager (`pip install uv` or `brew install uv`)

### Run with Docker Compose

```bash
# Build images and start all three services
docker compose up --build

# Run in the background
docker compose up --build -d
```

Once all health-checks pass, open:

| URL                            | What you'll see                  |
|--------------------------------|----------------------------------|
| <http://localhost:5173>        | Arcade frontend                  |
| <http://localhost:8000/docs>   | Backend interactive API docs     |
| <http://localhost:8001/docs>   | Auth service interactive API docs|

### Local development (without Docker)

```bash
# Auth service
cd auth
uv sync
uv run uvicorn app.main:app --reload --port 8001

# Backend service (new terminal)
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Testing

Each service has its own test suite. A top-level `Makefile` aggregates them.

```bash
# Unit tests only (fast, no running services required)
make test-unit

# Integration tests (spins up service under test, uses test DB)
make test-integration

# End-to-end tests (requires all three services running)
make test-e2e
```

Individual service tests:

```bash
# Backend unit tests
cd backend && uv run pytest tests/unit -v

# Auth unit tests
cd auth && uv run pytest tests/unit -v

# E2E with Playwright
cd e2e && npx playwright test
```

---

## Data Model

Tables are defined as SQLAlchemy ORM models and created at startup, not from
hand-written SQL. The models are the source of truth — see them rather than
copying field lists here:

- **`auth_db`** (managed by `auth`): `users` — `auth/app/models.py`. Passwords
  are stored as bcrypt hashes in `password_hash`.
- **`arcade_db`** (managed by `backend`): `games` and `scores` —
  `backend/app/models.py`. `scores.user_id` mirrors `users.id` from the auth
  database (no cross-database foreign key); `username_cached` is denormalized for
  leaderboard speed.

Seeded game catalogue: `backend/app/seed.py`. Domain concepts and where each
rule lives: [`docs/domain.md`](docs/domain.md).

---

## Agentic workflows

This repo ships a small multi-agent system you can drive from the agent picker:
two **coordinator** agents that orchestrate a shared library of **subagents**
through a research → plan → test → implement → document pipeline, with human
approval at each major step. Full protocol:
[`docs/agentic-workflows.md`](docs/agentic-workflows.md). Things to run:
[`BACKLOG.md`](BACKLOG.md).

> It is intentionally elaborate (and Opus-powered, so not cheap) - the point is to
> demonstrate the pattern: subagents, a model chosen per role, human-in-the-loop
> gates, and an arbitration/escalation path.

### The two workflows

| Coordinator | Start with | Use it for |
| --- | --- | --- |
| **Feature Builder** | `/build-feature` | adding or changing behavior - TDD: write failing tests, then code to green |
| **Refactor Lead** | `/refactor` | behavior-preserving cleanup - characterization tests first, then transform keeping them green |

### The agents

| Agent | Role | Model |
| --- | --- | --- |
| Feature Builder / Refactor Lead | coordinators - own the plan, the gates, the run log | Opus 4.7 |
| Researcher | scoped, read-only investigation | Sonnet 4.6 |
| Test Lead | designs a non-vanity test plan (may spawn Researchers) | Opus 4.7 |
| Integrator | reviews the plan for integration / contract hazards | Sonnet 4.6 |
| Implementer | writes tests then code under TDD | Sonnet 4.6 |
| Doc Writer | updates `docs/` to match the change | Sonnet 4.6 |

Researcher, Test Lead, Integrator, and Doc Writer are shared by both
coordinators. The agent definitions live in `.github/agents/`; this table is a
summary, the source of truth is [`docs/agentic-workflows.md`](docs/agentic-workflows.md).

### The pipeline

```
research → test plan → plan → integration check → [HITL-1: approve plan]
   → tests → implement loop → unit + integration → [HITL-2: accept output]
   → docs → [HITL-3: merge docs]
```

Each `[HITL-...]` is a stop: the coordinator posts a summary and ends its turn;
your next message resumes it. If an agent hits a gap between the plan and reality
(or an `AGENTS.md` "Ask first" boundary), it raises an **arbitration** block and
the coordinator asks you to decide - it never silently changes scope.

### Where the outputs go

Everything a run generates is kept under one roof (no scattered files):

- `agent-runs/active/<task-id>/` - the in-flight working files (research, plan,
  test plan, integration report, ...); convention in `agent-runs/README.md`.
- `docs/**` - the durable documentation, updated at HITL-3.
- finished runs move to `agent-runs/archive/<task-id>/`.

This mirrors OpenSpec's in-flight → durable → archive lifecycle. Each agent has a
single write-zone, which is what keeps artifacts systematic (see the protocol doc).

### Skills

| Skill | What it does |
| --- | --- |
| `/build-feature`, `/refactor` | kick off a run (scaffold the run folder, point you at the coordinator) |
| `/run-tests` | run the right test target and summarize pass / fail |
| `/research` | one-off scoped investigation |
| `/check-integration` | one-off integration / contract hazard scan |
| `/sync-docs` | find docs that have drifted from the code |

### Running one

1. Pick an item from [`BACKLOG.md`](BACKLOG.md) (or describe your own).
2. Run `/build-feature <item>` or `/refactor <item>` to scaffold the run.
3. Switch to the coordinator it names and approve at each gate.

This needs three settings, already in `.vscode/settings.json`:
`chat.subagents.allowInvocationsFromSubagents` (so the Test Lead can spawn
Researchers), `github.copilot.chat.skillTool.enabled` (for the forked skills), and
`chat.useCustomAgentHooks` (for the agent-scoped hooks below).

### Hooks (guardrails)

Instructions are wishes; hooks are guarantees. `.github/hooks/` holds deterministic
scripts that run at fixed lifecycle points:

- **Global** - a PreToolUse `gatekeeper` (denies secret reads and destructive
  commands; asks before new dependencies or schema changes, while letting the
  normal `make`/`npm`/`uv`/`docker`/`git` commands through), a PostToolUse
  auto-format of the edited file, and a SessionStart orientation digest.
- **Agent-scoped** - each writing agent gets a write-zone guard so the
  Implementer can only touch code/tests, the Doc Writer only docs, and the
  coordinators only their run folder; the Implementer's edits are audit-logged.

Every hook fails open (a hook bug never blocks work) and every decision is logged
to `agent-runs/audit/hooks.log`. Full detail:
[`docs/agentic-workflows.md`](docs/agentic-workflows.md#hooks-guardrails-and-automation).

### Inventory of agentic assets

| Asset | Path |
| --- | --- |
| Coordinators | `.github/agents/feature-builder.agent.md`, `refactor-lead.agent.md` |
| Subagents | `.github/agents/{researcher,test-lead,integrator,implementer,doc-writer}.agent.md` |
| Kickoff skills | `.github/skills/build-feature/`, `refactor/` |
| Reusable skills | `.github/skills/{run-tests,research,check-integration,sync-docs}/` |
| Global hooks | `.github/hooks/{gatekeeper,format,orient}.json` + matching `*.py` |
| Hook scripts | `.github/hooks/{gatekeeper,writezone,format_edited,audit_implementer,orient}.py` |
| Repo-wide rules | `AGENTS.md` |
| Path-scoped rules | `.github/instructions/*.instructions.md` (8) |
| Reference docs | `docs/` (architecture, domain, per-domain, testing, agentic-workflows) |
| Run artifacts / audit | `agent-runs/active/`, `agent-runs/archive/`, `agent-runs/audit/` |
| Settings | `.vscode/settings.json` (4 keys; git-ignored, set per workspace) |

---

## Copilot Training Suggestions

This section is the reason this repo exists. Each sub-section maps to a Copilot customization feature and shows a concrete, project-specific example you can drop in and demo.

> **Shipped vs. illustrative.** The repo's actual, working harness is: `AGENTS.md`,
> `.github/instructions/` (eight path-scoped files), the agents and skills in
> `.github/agents/` and `.github/skills/`, and the workflow system in
> [`docs/agentic-workflows.md`](docs/agentic-workflows.md). The code blocks in the
> sub-sections below (e.g. `dba.agent.md`, `add-new-domain-entity.md`, the
> `.github/prompts/` files) are **illustrative templates, not shipped files** -
> they show the shape of each feature so you can build your own on the fly during a
> demo. Note skills live at `.github/skills/<name>/SKILL.md`, not flat `.md` files.

---

### 1. Repo-level instructions

Repo-wide conventions that Copilot applies to every conversation. **This repo already ships a real one: [`AGENTS.md`](AGENTS.md)** (the cross-tool standard; Copilot also supports the name `.github/copilot-instructions.md`). Keep it short, state only rules that hold everywhere, and point to the `Makefile` and `docs/` for detail instead of restating them. The style:

```markdown
# Retro High-Score Arcade - agent instructions

## Stack
- Backend / Auth: Python 3.12, FastAPI, SQLAlchemy 2.0 (PostgreSQL in Docker; SQLite locally and in tests)
- Frontend: React 18, TypeScript, Vite, react-router, nes.css
- Package manager: uv for Python, npm for Node

## Conventions
- Database access goes through a SQLAlchemy session injected with `Depends(get_db)`; never open a connection in a router.
- FastAPI routers live in `app/routers/`; each owns one resource. Every route declares `response_model=`.
- Passwords are hashed with bcrypt (auth service). Never store or log plaintext.
- JWT is HS256; the secret comes from `JWT_SECRET`. auth issues, backend verifies. Never hardcode it.
- Frontend API calls go through `src/lib/api*.ts`, never raw `fetch` in components.
- Integration tests carry the `integration` pytest marker.
```

---

### 2. Path-scoped instructions (`applyTo` globs)

File-specific rules that Copilot applies automatically when the matching files are
in context. **This repo ships eight of them in `.github/instructions/`**, each
paired with a doc in `docs/`. Each uses a frontmatter `applyTo` glob:

| File | `applyTo` |
| ---- | --------- |
| `frontend.instructions.md`       | `frontend/src/**` |
| `frontend-tests.instructions.md` | `frontend/src/**/*.test.ts, *.test.tsx` |
| `e2e.instructions.md`            | `e2e/**` |
| `backend.instructions.md`        | `backend/**` |
| `auth.instructions.md`           | `auth/**` |
| `python-tests.instructions.md`   | `backend/tests/**, auth/tests/**` |
| `database.instructions.md`       | `**/app/db.py, **/app/models.py` |
| `docker.instructions.md`         | `**/Dockerfile, docker-compose.yml, postgres/**` |

The example shape (see the real files for full content):

```markdown
---
description: 'Conventions for the backend service (games, scores, leaderboards).'
applyTo: 'backend/**'
---
# Backend conventions

- Every route declares `response_model=`; raise `HTTPException(404, "<Resource> not found")`.
- Protected routes depend on `get_current_user` (verifies the JWT).
- Style: PEP 8, enforced by `ruff`.

More detail: `docs/backend.md`.
```

Globs **stack**: a file matched by several instruction files gets all of them, so
each file owns only its own slice and repo-wide rules stay in `AGENTS.md`.

---

### 3. Reusable prompts (`.github/prompts/`)

Store these as `.prompt.md` files. Copilot Chat can invoke them with `/scaffold-new-endpoint` etc.

**`.github/prompts/scaffold-new-endpoint.prompt.md`**
```markdown
---
mode: agent
description: "Scaffold a new FastAPI router, Pydantic schema, DB helper, and unit test stub for a given resource."
---
Create a new FastAPI resource for **$RESOURCE_NAME** in the **$SERVICE** service (backend or auth).

Steps:
1. Add `app/routers/$RESOURCE_NAME.py` with CRUD endpoints following the existing router pattern.
2. Add Pydantic request/response models in `app/schemas.py`.
3. Add DB helper functions in `app/db.py`.
4. Register the router in `app/main.py`.
5. Create `tests/unit/test_$RESOURCE_NAME.py` with at least one happy-path and one error-path test.
```

**`.github/prompts/add-seed-game.prompt.md`**
```markdown
---
mode: agent
description: "Add a new arcade game to the seed data and wire it to the leaderboard."
---
Add a new arcade game called **$GAME_TITLE** (slug: `$GAME_SLUG`) to the project.

1. Insert a seed row in `backend/app/seed.py`.
2. Add a helper in `frontend/src/lib/apiBackend.ts` if the game needs a new call.
3. Extend the E2E fixtures in `e2e/fixtures/api.ts` if the flow needs setup.
```

**`.github/prompts/new-leaderboard-view.prompt.md`**
```markdown
---
mode: agent
description: "Generate a new React leaderboard page component for a given game."
---
Create a leaderboard page for the game with slug **$GAME_SLUG**.

1. Create `frontend/src/pages/$GameSlug/LeaderboardPage.tsx`.
2. Fetch via the leaderboard helper in `frontend/src/lib/apiBackend.ts` (add one if missing).
3. Render an `nes.css` styled table with rank, username, score, and date columns.
4. Add a route in `frontend/src/App.tsx` (react-router).
```

**`.github/prompts/add-playwright-spec.prompt.md`**
```markdown
---
mode: agent
description: "Add a Playwright E2E spec for a given user flow."
---
Write a Playwright test in `e2e/specs/$SPEC_NAME.spec.ts` that covers: **$FLOW_DESCRIPTION**.

Requirements:
- Use the helpers in `e2e/fixtures/api.ts` (e.g. `createFreshUser`) for setup.
- Assert on visible text, not implementation details.
- Include a negative / error-state test case.
```

---

### 4. Skills (`.github/skills/`)

Skills orchestrate multi-step, cross-cutting changes that span several files or services.

**`.github/skills/add-new-domain-entity.md`** — adds a full vertical slice:
```markdown
# Skill: Add new domain entity

Orchestrates adding a new data entity end-to-end:

1. **Backend model** — SQLAlchemy ORM model in `backend/app/models.py`
2. **Pydantic schemas** — request/response models in `backend/app/schemas.py`
3. **FastAPI router** — CRUD endpoints in `backend/app/routers/<entity>.py`
4. **API client** — TypeScript fetch wrapper in `frontend/src/lib/<entity>.ts`
5. **UI component** — `nes.css` styled list/detail component in `frontend/src/components/`
7. **Unit tests** — pytest stubs in `backend/tests/unit/test_<entity>.py`
8. **E2E spec stub** — Playwright spec in `e2e/specs/<entity>.spec.ts`
```

**`.github/skills/rotate-jwt-secret.md`** — guided secret rotation:
```markdown
# Skill: Rotate JWT secret

Guides rotating the `JWT_SECRET` across all affected files without breaking running sessions.

Steps:
1. Generate a new secret: `openssl rand -hex 32`
2. Update `docker-compose.yml` environment vars for `auth` and `backend`.
3. Remind operator to update any CI/CD secrets (GitHub Actions, etc.).
4. Remind operator that existing tokens will be invalidated on restart.
5. Verify no hardcoded secrets remain: `grep -r "retro-arcade" . --include="*.py" --include="*.ts"`
```

---

### 5. Custom agents and agentic workflows

The flagship example is the multi-agent system this repo ships — two coordinators
and a shared subagent library. It has its own section above
([Agentic workflows](#agentic-workflows)) and full protocol in
[`docs/agentic-workflows.md`](docs/agentic-workflows.md).

The same `.agent.md` mechanism also supports simple scoped modes. These two are
illustrative sketches (not shipped):

**`.github/agents/dba.agent.md`** — read-only database advisor:
```markdown
---
description: "Read-only DBA mode — analyses schema and queries, never modifies migrations."
tools:
  - read_file
  - grep
  - search_files
applyTo:
  - "**/models.py"
  - "**/db.py"
---
# DBA Mode

You are a read-only database advisor. You may read schema files, explain queries, suggest
indexes, and identify N+1 patterns. You must NOT generate or apply migration files, ALTER
TABLE statements, or any write operations.

When asked to optimise a query, explain the execution plan and the index that should be used
(refer to `idx_scores_game_score` for leaderboard queries).
```

**`.github/agents/frontend-only.agent.md`** — frontend-scoped mode:
```markdown
---
description: "Frontend-only mode — edits restricted to the frontend/ directory."
tools:
  - read_file
  - edit_file
  - create_file
  - run_terminal_command
applyTo:
  - "frontend/**"
---
# Frontend-Only Mode

You operate exclusively within the `frontend/` directory. Do not read, suggest, or modify
files in `backend/`, `auth/`, `e2e/`, or any root-level config.

Stack reminders: React 18, TypeScript, Vite, react-router, nes.css.
Always maintain the NES retro aesthetic.
```

---

### 6. MCP server — database inspector

Point an MCP server at the development database so Copilot can inspect live data
during a demo.

The Docker stack runs **PostgreSQL**, so use a Postgres MCP server against the
exposed port (`localhost:5432`, user/password `arcade`, databases `arcade_db` and
`auth_db` — see `docker-compose.yml`). For example, with the Postgres MCP server:

```json
{
  "github.copilot.chat.mcpServers": {
    "arcade-db": {
      "command": "uvx",
      "args": ["postgres-mcp", "postgresql://arcade:arcade@localhost:5432/arcade_db"]
    }
  }
}
```

If instead you run a service locally without Docker (default SQLite URL), point the
[SQLite MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite)
at the generated `.db` file. Either way, you can then ask Copilot Chat:

- *"Show me the top 5 scores for Super Mario Bros."*
- *"How many users have registered today?"*
- *"Which game has the most score submissions?"*

> **Note:** Start the stack with `docker compose up` first so the database is running
> before attaching the MCP server. Local `.db` files are git-ignored.

---

## Troubleshooting

### Port conflicts

```bash
# Find what's using port 8000
lsof -i :8000

# Or check all three ports at once
lsof -i :5173 -i :8000 -i :8001
```

Stop the conflicting process, or change the host port in `docker-compose.yml`
(e.g. `"8080:8000"`) and update the `VITE_BACKEND_URL` env var accordingly.

### Wipe everything and start fresh

```bash
# Stop containers AND delete the named volume (all DB data is lost)
docker compose down -v

# Rebuild from scratch
docker compose up --build
```

### Health-check failures on first boot

The `backend` service waits for `auth` to be healthy before starting. If `auth` takes longer
than 50 s (10 s × 5 retries) on a slow machine, increase `retries` in `docker-compose.yml`.

### `uv sync` fails locally

Ensure Python 3.12 is active: `python --version`. If using `pyenv`:

```bash
pyenv install 3.12
pyenv local 3.12
```

---

## Contributing

This repo is a training demo. Feel free to extend it — adding a new game, a global leaderboard,
or a React component is an excellent way to practice driving Copilot with the customisations
described above.
