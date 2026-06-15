---
description: 'Conventions for end-to-end browser tests (Playwright).'
applyTo: 'e2e/**'
---

# E2E test conventions

These tests exercise the whole stack through the browser; they are not
frontend-only or backend-only.

- **Tooling:** Playwright; specs in `e2e/specs/`, config in
  `e2e/playwright.config.ts` (`baseURL` is `http://localhost:5173`).
- **The stack must already be running** (`make up`); the config does not start it.
- **Tests run serially and share database state** - do not assume isolation
  between specs.
- **Set up state via the real APIs** (`e2e/fixtures/api.ts`, e.g.
  `createFreshUser`), then drive and assert through the UI.
- **Assert on visible text or roles**, not implementation details; include a
  negative / error-state case per flow.

More detail: `docs/e2e.md`.
