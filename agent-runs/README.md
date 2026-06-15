# agent-runs

The systematic home for everything the agentic workflows generate, so artifacts
never end up scattered as random `.md` files around the repo.

The structure is modeled on OpenSpec's lifecycle (in-flight changes -> durable
specs -> archive), adapted to our agents:

| OpenSpec | Here | What it is |
| --- | --- | --- |
| `changes/<id>/` | `agent-runs/active/<task-id>/` | the in-flight working set for one run |
| `specs/` (durable truth) | `docs/` | the durable documentation (updated at HITL-3) |
| `archive/` | `agent-runs/archive/<task-id>/` | completed runs, kept for the record |

## Lifecycle

1. **Kickoff** (`/build-feature` or `/refactor`) creates
   `agent-runs/active/<task-id>/run.md`.
2. **During the run**, each phase writes exactly one named file here (see below).
3. **At HITL-3**, after the durable docs in `docs/` are updated, the coordinator
   moves `active/<task-id>/` to `archive/<task-id>/`.

## Files in a run directory

```
run.md                 task statement + phase log (coordinator)
research.md            Researcher output
test-plan.md           Test Lead output
plan.md                the implementation / refactor plan (coordinator)
integration-report.md  Integrator output
arbitration.md         any escalation (append-only)
doc-changes.md         summary of the docs/ updates (Doc Writer's work)
```

## Write-zones (the no-scatter rule)

Every writer has exactly one zone. Nothing writes outside its zone.

| Writer | May write to |
| --- | --- |
| coordinator (Feature Builder / Refactor Lead) | `agent-runs/active/<task-id>/` only |
| Implementer | `src/**`, `tests/**`, `frontend/**` (the actual code + tests) |
| Doc Writer | `docs/**`, touched `.github/instructions/*` |
| read-only subagents (Researcher, Test Lead, Integrator) | nothing - they **return** their output; the coordinator persists it |

`active/` is git-ignored (scratch); `archive/` and this README are kept.
