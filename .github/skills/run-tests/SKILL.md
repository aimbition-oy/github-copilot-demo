---
name: run-tests
description: "Run the project's tests and report a compact pass/fail summary. Use during a TDD loop or as a quick standalone check."
argument-hint: "optional: which tier or service (e.g. backend unit, frontend, all)"
user-invocable: true
disable-model-invocation: false
---

# Run tests

Run the right target and report results. Inline (not forked) so the raw outcome
is available to steer a TDD loop.

1. Choose the command from the request:
   - default -> `make test-unit`, then `make test-integration`.
   - a single service -> the targeted command, e.g.
     `cd backend && uv run pytest tests/unit/ -v`, or `cd frontend && npm test`.
   - all tiers -> `make test` (note: this includes e2e, which needs the stack up
     via `make up-d`).
   - `e2e` -> remind that the stack must be up (`make up-d`) then `make test-e2e`.
2. Run it with the terminal.
3. Report a compact summary: totals (passed/failed), and the names of any failing
   tests with their first error line. Do not paste the full log.

Commands reference: `Makefile` (`make help`) and `docs/python-testing.md`,
`docs/frontend-testing.md`, `docs/e2e.md`.
