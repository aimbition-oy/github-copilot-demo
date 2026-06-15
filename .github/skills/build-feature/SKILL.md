---
name: build-feature
description: "Kick off a test-driven feature build. Scaffolds a run folder for the task, then hands you to the Feature Builder coordinator agent."
argument-hint: "the feature or change to build"
user-invocable: true
disable-model-invocation: true
---

# Start a feature build

This skill primes a run. (A skill cannot spawn agents - it sets the stage, then
you switch to the coordinator.)

Do this:

1. Pick a short kebab-case `task-id` from the request (e.g. `harvest-field`).
2. Create `agent-runs/active/<task-id>/run.md` containing:
   - the task statement (the text passed to this command),
   - the workflow: `feature-builder`,
   - an empty `## Phase log`.
3. Tell the user: open the **Feature Builder** agent from the agent picker and
   give it the task, pointing at `agent-runs/active/<task-id>/`.

The full pipeline, gates, and artifacts are defined in
`docs/agentic-workflows.md`. Do not start implementing here - that is the
coordinator's job.
