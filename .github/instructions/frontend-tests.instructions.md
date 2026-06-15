---
description: 'Conventions for frontend unit and component tests (Vitest).'
applyTo: 'frontend/src/**/*.test.ts, frontend/src/**/*.test.tsx'
---

# Frontend test conventions

- **Tooling:** Vitest (`jsdom`) + Testing Library; config in
  `frontend/vite.config.ts`, shared setup in `frontend/src/test/setup.ts`.
- **Mock the network at the MSW boundary** (`frontend/src/test/handlers.ts`). Do
  not stub `fetch` or the `src/lib/api*` modules directly.
- **Test behavior, not implementation:** query by role or visible text and assert
  on rendered output, not internal state.
- **Co-locate** each test with its subject (`GameCard.tsx` -> `GameCard.test.tsx`).
- Full-screen flows use `*.integration.test.tsx`; keep pure-component tests
  separate.

More detail: `docs/frontend-testing.md`. Browser-level tests are separate (see the
e2e instructions).
