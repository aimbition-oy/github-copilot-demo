# Frontend

React 18 + Vite + TypeScript single-page app, styled with `nes.css`. Talks to the
`auth` and `backend` services over HTTP. No build-time backend coupling beyond two
env vars. Source of truth: `frontend/`.

## Layout

```
frontend/src/
  pages/        Route screens (Home, Login, Register, Leaderboard, SubmitScore)
  components/   Reusable UI (GameCard, NavBar, ScoreRow, PixelButton)
  lib/          API clients + auth state (apiAuth.ts, apiBackend.ts, auth-context.tsx)
  styles/       nes-overrides.css
  test/         Vitest setup + MSW handlers
```

Routing is `react-router-dom` v6, wired in `src/App.tsx`. Entry: `src/main.tsx`.

## Conventions

- **Styling via `nes.css`** classes plus `src/styles/nes-overrides.css`. Keep the
  retro aesthetic; avoid inline `style` props.
- **All network calls go through `src/lib/apiAuth.ts` / `apiBackend.ts`.** Never
  call `fetch` directly from a component or page.
- **Base URLs come from the environment:** `import.meta.env.VITE_AUTH_URL` and
  `import.meta.env.VITE_BACKEND_URL`. Never hardcode `localhost` ports in
  components.
- **Auth state** lives in `src/lib/auth-context.tsx` (the JWT and current user).
  Read it through the context, not from storage directly.
- **Display formatting:** score values use `toLocaleString()` for thousands
  separators.
- TypeScript throughout; ESLint is the style authority (`npm run lint`).

## How it connects

The frontend is the only service the browser talks to. It calls `auth` for
register/login and `backend` for games/scores/leaderboards, attaching the JWT as
a `Bearer` token on protected calls. See [architecture.md](architecture.md) for
the trust boundary and [api docs in backend.md](backend.md) / [auth.md](auth.md)
for the endpoints it consumes.

Testing this layer: [frontend-testing.md](frontend-testing.md) (unit) and
[e2e.md](e2e.md) (full-stack).
