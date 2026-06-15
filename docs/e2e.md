# End-to-end testing

Browser-driven tests that exercise the whole stack (frontend + backend + auth +
Postgres) with Playwright. These are not frontend-only or backend-only - they
prove the services integrate. Source of truth: `e2e/`.

## Stack

- **Playwright** (`@playwright/test`), Chromium project - config in
  `e2e/playwright.config.ts`, `baseURL` `http://localhost:5173`.
- Specs in `e2e/specs/` (auth, leaderboard, submit-score, unauthenticated).
- Fixtures in `e2e/fixtures/api.ts` set up state by calling the **real** auth and
  backend APIs (e.g. `createFreshUser`), which keeps setup fast and deterministic.

## Conventions

- **The stack must be running** (`make up`) before `make test-e2e`; the config
  does not start it.
- **Tests run serially** (`workers: 1`, `fullyParallel: false`) because they share
  database state. Do not assume isolation between specs.
- **Set up via the API, assert via the UI:** use `fixtures/api.ts` to create users
  and scores, then drive and assert on the browser.
- **Assert on visible text/roles**, not implementation details; include a negative
  / error-state case per flow.
- Reset data between runs with the backend `/test/scores` helper (enabled by
  `ENABLE_TEST_ENDPOINTS` in compose).

## Running

`make test-e2e` (needs the stack up). `make test` runs unit, integration, then
E2E in order. Full command list: `make help`.

Unit/component tests are separate: [frontend-testing.md](frontend-testing.md).
Service APIs under test: [backend.md](backend.md), [auth.md](auth.md).
