---
name: refactor
description: "Kick off a behavior-preserving refactor. Scaffolds a run folder for the task, then hands you to the Refactor Lead coordinator agent."
argument-hint: "the code to refactor and the goal"
user-invocable: true
disable-model-invocation: true
---

# Start a refactor

This skill primes a run. (A skill cannot spawn agents - it sets the stage, then
you switch to the coordinator.)

Do this:

1. Pick a short kebab-case `task-id` from the request (e.g. `scores-service`).
2. Create `agent-runs/active/<task-id>/run.md` containing:
   - the refactor target and goal (the text passed to this command),
   - the workflow: `refactor-lead`,
   - an empty `## Phase log`.
3. Tell the user: open the **Refactor Lead** agent from the agent picker and give
   it the task, pointing at `agent-runs/active/<task-id>/`.

The defining rule is **no behavior change** - characterization tests first. Full
pipeline and gates: `docs/agentic-workflows.md`. Do not start refactoring here.

**Two steps by design.** This skill only primes the run and stops - a skill
cannot launch an agent, so the actual work happens after you switch to the
**Refactor Lead** agent. If you prefer one step, skip this skill entirely and just
invoke the Refactor Lead agent directly with your task; it will create the run
folder itself.
