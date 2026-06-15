# Agentic workflows

This repo ships two coordinator agents that orchestrate a small shared library of
subagents through a research -> plan -> test -> implement -> document pipeline.
This document is the **single source of the shared protocol**; the agent files
point here instead of repeating it.

> Demo note: this is intentionally elaborate to show the pattern. It is also
> deliberately expensive (Opus coordinators). Run it on real tasks sparingly.

## The two workflows

Both mutate code and both are test-driven, but they are distinct disciplines -
which is why each gets its own coordinator agent rather than one mode flag.

| | **feature-builder** (`/build-feature`) | **refactor-lead** (`/refactor`) |
| --- | --- | --- |
| Intent | add or change behavior | preserve behavior, improve structure |
| Test discipline | write **failing** tests for new behavior (red -> green) | write **characterization** tests that pass against current code (a green safety net), then transform keeping them green |
| Terminal state | new passing tests + code + docs | same behavior, cleaner code, unchanged test outcomes + docs |

Phase sequence (identical skeleton, different test discipline):

```
research -> test plan -> plan -> integration check -> [HITL-1 plan]
   -> tests -> implement loop -> unit + integration -> [HITL-2 output]
   -> docs -> [HITL-3 docs]
```

## Roster

| Agent (`name`) | Role | Model | Mutates |
| --- | --- | --- | --- |
| Feature Builder | coordinator (feature) | Opus 4.7 | yes |
| Refactor Lead | coordinator (refactor) | Opus 4.7 | yes |
| Researcher | scoped read-only investigation | Sonnet 4.6 | no |
| Test Lead | non-vanity test plan; may spawn researchers | Opus 4.7 | no |
| Integrator | integration/contract risk review of the plan | Sonnet 4.6 | no |
| Implementer | writes tests then code (TDD) | Sonnet 4.6 | yes |
| Doc Writer | updates docs to match the diff | Sonnet 4.6 | docs only |

The **`name`** values above are what `agents:` whitelists and the agent picker
match (file slugs differ: `feature-builder.agent.md` -> "Feature Builder", and the
kickoff skills are `/build-feature` and `/refactor`).

Researcher, Test Lead, Integrator, and Doc Writer are shared by both
coordinators. Only Implementer and the coordinators carry `edit`.

## Run artifacts

Subagents are single-input / single-output with a clean context, so state is
threaded through files, not memory. To keep those files from scattering, every
run uses one directory: **`agent-runs/active/<task-id>/`**. The convention (and
its OpenSpec lineage) is documented in `agent-runs/README.md`.

```
run.md                 task statement + phase log (coordinator)
research.md            Researcher output
test-plan.md           Test Lead output
plan.md                the implementation / refactor plan (coordinator)
integration-report.md  Integrator output
arbitration.md         any escalation (append-only)
doc-changes.md         summary of the docs/ updates
```

### Write-zones (the no-scatter rule)

Each writer has exactly one zone and writes nowhere else. This is what keeps
artifacts systematic instead of strewn around the repo.

| Writer | May write to |
| --- | --- |
| coordinator | `agent-runs/active/<task-id>/` only |
| Implementer | `src/**`, `tests/**`, `frontend/**` (code + tests) |
| Doc Writer | `docs/**`, touched `.github/instructions/*` |
| Researcher, Test Lead, Integrator | nothing - they **return** their output; the coordinator persists it to the named file |

The read-only subagents have no `edit` tool by design, so they cannot write
files: they return their content and the coordinator saves it. Code and test
changes are the real deliverable (Implementer); the durable documentation is
`docs/` (Doc Writer) - the run directory is only the process paper trail.

### Lifecycle

`agent-runs/active/<task-id>/` is the in-flight working set. At **HITL-3**, after
the `docs/` updates are accepted, the coordinator moves the run directory to
`agent-runs/archive/<task-id>/`. This mirrors OpenSpec: in-flight ->
durable (`docs/`) -> archived. `active/` is git-ignored (scratch); `archive/`
and the README are kept.

## Human-in-the-loop gates

Subagents cannot pause for a human. **Every gate is the coordinator ending its
turn**: it writes the artifact, prints the banner, makes no further tool calls,
and stops. Your next chat message is the resume signal.

- `=== HITL-1: APPROVE PLAN? [approve / revise: ... / abort] ===` after the
  plan + test-plan + integration report.
- `=== HITL-2: ACCEPT OUTPUT? [accept / request changes: ...] ===` after the
  implementation is green and the unit + integration suites have run once.
- `=== HITL-3: MERGE DOCS? [merge / edit: ...] ===` after the doc-writer drafts
  doc changes.

## Implementation loop

- **feature-builder:** implementer writes the failing tests first and confirms
  RED, then edits code toward GREEN, re-running the targeted test command each
  pass. Refactor only once green, keeping green.
- **refactor-lead:** implementer writes characterization tests that pass against
  the current code (establish the baseline), then transforms in small steps,
  re-running tests after each to confirm behavior is unchanged.
- **Iteration cap: 3.** If still not green (feature) or behavior cannot be
  preserved (refactor) after 3 attempts, stop and escalate (arbitration).
- During the loop, run the **targeted** service test command for speed. Before
  HITL-2, run `make test-unit` and `make test-integration` once. Run
  `make test-e2e` only when the change affects end-to-end flows **and** the Docker
  stack is up (`make up-d`) - never inside the loop, and never assume it is
  running.

## Arbitration (failure protocol)

Iron rule: **subagents never decide scope.** When any subagent hits a gap
between the plan and reality - a missing field, a contract mismatch, an
`AGENTS.md` "Ask first" boundary (new dependency, cross-service / JWT-contract
change, schema change), or the 3-attempt cap - it returns **only** this block:

```
ARBITRATION
phase:        <research|test|plan|integrate|implement>
expected:     <what plan.md said>
encountered:  <reality>
options:      [A ..., B ...]
recommendation: <one option + why - explicitly non-binding>
blocking:     <yes|no>
```

The coordinator does not auto-resolve. It writes the block to `arbitration.md`,
copies it verbatim into chat under **ARBITRATION REQUIRED**, adds a short read of
the options, and ends the turn. Only the human changes scope or crosses an "Ask
first" boundary. On reply, the coordinator updates `plan.md` / `test-plan.md` and
re-dispatches.

## Hooks (guardrails and automation)

Instructions are wishes; hooks are guarantees. Deterministic scripts run at fixed
points in an agent's lifecycle and either gate an action or react to it. They live
in `.github/hooks/` (Python, stdlib only, cross-platform). Every hook **fails
open** - on any error it allows the action and exits 0, so a hook bug can never
brick a run. Decisions are logged to `agent-runs/audit/hooks.log`.

**Global** (apply to every agent, configured in `.github/hooks/*.json`):

| Hook | Event | What it guarantees |
| --- | --- | --- |
| `gatekeeper.py` | PreToolUse | Denies secret reads (`.env`, the JWT secret) and destructive commands (`rm -rf`, `git push --force`, `git reset --hard`, `down -v`, dropping tables); **asks** before adding a dependency or changing the schema (the AGENTS.md "Ask first" boundaries). Normal workflow commands (`uv run pytest`, `npm test`, `make *`, `docker compose up`, `git add/commit`) pass untouched. |
| `format_edited.py` | PostToolUse | Auto-formats the edited file only - `ruff` for `.py`, `eslint --fix` for `.ts/.tsx`. Self-healing quality, never blocks. |
| `orient.py` | SessionStart | Injects a short orientation digest (services, which guardrails are hook-enforced, in-flight runs). |

**Agent-scoped** (in each `.agent.md` frontmatter; needs the setting below). These
turn the documented [write-zones](#write-zones-the-no-scatter-rule) into hard
guarantees via `writezone.py <role>`:

| Agent | Event | Guarantee |
| --- | --- | --- |
| Implementer | PreToolUse | may edit only `backend/ auth/ frontend/ e2e/` |
| Implementer | PostToolUse | every edit is logged to `agent-runs/audit/implementer.log` |
| Doc Writer | PreToolUse | may edit only `docs/`, `.github/instructions/`, README/AGENTS |
| Feature Builder / Refactor Lead | PreToolUse | may edit only `agent-runs/active/` |

No agent (any role) may edit `node_modules`, `.venv`, or a `.env` file. The
read-only subagents (Researcher, Test Lead, Integrator) get no write-zone hook -
they have no `edit` tool, so the tool boundary already guarantees it.

Demo tip: open `agent-runs/audit/hooks.log` mid-run to show a `deny`/`ask` line -
that line is the guarantee the AGENTS.md prose alone could only wish for.

## Required VS Code settings

Merged into `.vscode/settings.json`:

- `chat.subagents.allowInvocationsFromSubagents: true` - lets `test-lead` spawn
  `researcher` (subagent nesting; default off, depth <= 5).
- `github.copilot.chat.skillTool.enabled: true` - required for the `context: fork`
  skills.
- `chat.useCustomAgentHooks: true` - required for the agent-scoped hooks above.

`.vscode/settings.json` is force-tracked (a `!.vscode/settings.json` exception in
`.gitignore`) so these settings travel with the repo.

## Model / cost notes

A subagent's model cannot exceed the coordinator's tier. Coordinators and
`test-lead` are Opus 4.7; the rest are Sonnet 4.6 (safely below). If you run a
coordinator on a cheaper model from the picker, its Opus subagents silently
downgrade - run coordinators on Opus as declared for the demo. Tool names follow
this repo's existing short-form convention (see `researcher.agent.md`); adjust to
your VS Code build's exact tool ids if an agent fails to load.
