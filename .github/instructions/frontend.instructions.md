---
description: 'Conventions for the React frontend application code.'
applyTo: 'frontend/src/**'
---

# Frontend conventions

- **Styling:** use `nes.css` classes plus `src/styles/nes-overrides.css`. No inline
  `style` props; keep the retro aesthetic.
- **Network:** call services only through `src/lib/apiAuth.ts` and
  `src/lib/apiBackend.ts`. Never use `fetch` directly in a component or page.
- **Base URLs:** read from `import.meta.env.VITE_AUTH_URL` and
  `VITE_BACKEND_URL`. Never hardcode hosts or ports.
- **Auth state:** read the JWT and current user through `src/lib/auth-context.tsx`,
  not from storage directly.
- **Routing:** `react-router-dom` v6, wired in `src/App.tsx`.
- **Style authority:** TypeScript + ESLint (`make lint-frontend`); don't hand-fix
  what the linter owns.

More detail: `docs/frontend.md`. Testing this layer is covered by the frontend-test
and e2e instruction files.
