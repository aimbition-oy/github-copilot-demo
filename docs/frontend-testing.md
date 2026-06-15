# Frontend testing (unit / component)

Component and unit tests for the frontend, run with Vitest. These are fast and
need no running services - the network is mocked. Source of truth:
`frontend/vite.config.ts` and `frontend/src/test/`.

## Stack

- **Vitest** (`jsdom` environment, globals on) - config in `frontend/vite.config.ts`.
- **Testing Library** (`@testing-library/react`, `user-event`, `jest-dom`).
- **MSW** for network mocking; request handlers live in
  `frontend/src/test/handlers.ts`, wired in `frontend/src/test/setup.ts`.

Test files sit next to the code: `src/**/*.test.ts(x)`.

## Conventions

- **Test behavior, not implementation:** query by role/text the user sees; assert
  on rendered output, not internal state.
- **Mock the network at the MSW boundary** (`src/test/handlers.ts`), never by
  stubbing `fetch` or the `src/lib/api*` modules directly - this keeps tests close
  to real request/response shapes.
- **Co-locate** the test with its component (`GameCard.tsx` ->
  `GameCard.test.tsx`).
- Pages have `*.integration.test.tsx` variants that exercise a full screen against
  MSW; keep pure-component tests separate from those.

## Running

`make test-unit` runs these alongside the Python unit tests. Frontend only:
`cd frontend && npm test`. Full command list: `make help`.

Full-stack browser tests are separate: [e2e.md](e2e.md). The frontend itself:
[frontend.md](frontend.md).
