# Backlog - demoable workflow items

Small, real changes to run through the agentic workflows
([`docs/agentic-workflows.md`](docs/agentic-workflows.md)). Each is sized for a
single demo run.

**How to run one:** invoke the kickoff skill with the item as the task -
`/build-feature <item>` or `/refactor <item>` - then switch to the coordinator it
names and approve at each HITL gate. Artifacts land in
`agent-runs/active/<task-id>/`.

The "lights up" column is what makes each one worth demoing: which part of the
pipeline becomes visible.

## Feature workflow (`/build-feature` -> Feature Builder)

| # | Item | Scope | Lights up |
| - | --- | --- | --- |
| F1 | **Player score history**: `GET /users/{username}/scores` returns a player's scores across all games, newest first. | backend: new route + `schemas.py` model + unit/integration tests | The clean happy path end to end - good first run to show research -> plan -> red -> green -> docs. |
| F2 | **Rank on submit**: `POST /scores` response also returns the player's rank on that game's leaderboard. | backend: extend `scores.py` + response schema + tests | TDD on real logic (write the failing rank test first); the Integrator checks it reuses the leaderboard ordering, not a second code path. |
| F3 | **Leaderboard pagination**: add `offset` (alongside `limit`) to `GET /games/{slug}/leaderboard`. | backend: query param + bounds + tests for edge cases | Tight red-green loop with obvious edge cases (offset past the end). Small enough to finish fast. |
| F4 | **Admin-gated reset** (advanced): add an `is_admin` claim to the JWT and gate `DELETE /test/scores` on it. | auth: issue the claim · backend: read + enforce it | **Integrator + arbitration.** It changes the shared JWT contract (an `AGENTS.md` "Ask first" boundary) - expect the Integrator to flag it and the coordinator to escalate for your decision before any code is written. |

## Refactor workflow (`/refactor` -> Refactor Lead)

| # | Item | Scope | Lights up |
| - | --- | --- | --- |
| R1 | **Extract the leaderboard query** from `backend/app/routers/scores.py` into a reusable helper, used by the leaderboard route (and F2 if built). | backend: move logic, no behavior change | The core refactor discipline: characterization tests pin the endpoint's current output first, then the move keeps them green. |
| R2 | **Centralize frontend API calls**: move any remaining inline `fetch` in components/pages into `src/lib/apiAuth.ts` / `apiBackend.ts`. | frontend: relocate calls, no behavior change | Enforces the `frontend.instructions.md` rule via the refactor path; existing component/integration tests are the safety net. |
| R3 | **De-duplicate service setup** (advanced): the near-identical `config.py` / `db.py` in `auth/` and `backend/` into one shared pattern. | both Python services | **Arbitration.** A shared module crosses service boundaries (an "Ask first" boundary) - a deliberate demo of the escalation path: the Refactor Lead should stop and ask you how to proceed rather than silently coupling the services. |

## Suggested demo order

1. **F3** or **F1** - a clean run to show the whole pipeline and the three HITL gates.
2. **R1** - show the refactor discipline (characterization-first, stays green).
3. **F4** or **R3** - show the Integrator and the arbitration/escalation path (the
   interesting failure mode, not just the happy path).
