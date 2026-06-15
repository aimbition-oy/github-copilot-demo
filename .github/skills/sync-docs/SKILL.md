---
name: sync-docs
description: "Find documentation that has drifted from the code and report (or draft) the updates. Checks docs/** and the path-scoped instructions against a change."
argument-hint: "the diff or area that changed"
context: fork
user-invocable: true
disable-model-invocation: false
---

# Sync the docs

Forked review of documentation drift after a change.

1. Determine what changed (the diff or the named area).
2. Check the docs that cover it:
   - `docs/**` - the per-domain doc for the area (e.g. `docs/backend.md`,
     `docs/database.md`).
   - `.github/instructions/*.instructions.md` - any path-scoped rule the change
     affects.
   - `README.md` / `AGENTS.md` - only repo-wide facts.
3. Report each drift: the file, the stale statement, and the corrected text.

Follow the repo's docs style: **point to the source-of-truth file, do not restate
values that will drift** (see how the docs reference `models.py`, `seed.py`).
Flag drift only where it is real; do not rewrite untouched docs.
