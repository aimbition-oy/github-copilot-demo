---
name: check-integration
description: "Scan a change or area for cross-service / contract integration hazards (JWT, request shapes, schema, CORS, the two databases). Read-only review; returns a ranked risk list."
argument-hint: "the change, plan, or area to check"
context: fork
user-invocable: true
disable-model-invocation: false
---

# Check integration hazards

Forked read-only review. The authoritative description of the integration points
is `docs/architecture.md`; check the target against it.

Walk the checklist and report each as **blocking / caution / ok**:

1. **JWT contract** - `auth` issues HS256, `backend` verifies with the same
   `JWT_SECRET` and claims (`sub`, `username`). Any change to token shape, claims,
   expiry, or secret handling?
2. **Cross-service shapes** - the frontend calls `auth` / `backend` via
   `src/lib/api*.ts`. Any request/response shape changing on one side only?
3. **Database** - two separate databases, no cross-DB FK; tables come from
   `create_all` (no migrations). Schema change without a matching model update?
4. **CORS / config** - new origin, port, or env var compose must also set?
5. **Test endpoints** - anything relying on `ENABLE_TEST_ENDPOINTS`?

Report: each hazard with the seam, the specific risk, and a suggested guard
(often a test). If nothing is at risk, say so - do not invent hazards.
