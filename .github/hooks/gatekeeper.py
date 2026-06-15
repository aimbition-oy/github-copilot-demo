#!/usr/bin/env python3
"""Global PreToolUse gatekeeper.

Turns AGENTS.md wishes into guarantees for terminal commands:
- DENY secret access (.env reads, the JWT secret) and destructive commands.
- ASK before adding dependencies or changing the schema (AGENTS.md "Ask first").
- ALLOW everything else (the normal workflow commands).

Fail-open: the decision lives in the stdout JSON and the exit code is always 0.
Any parse/exec error degrades to allow, so a hook bug never bricks a live demo.
"""

import datetime
import json
import pathlib
import re
import sys

LOG = pathlib.Path("agent-runs/audit/hooks.log")


def log(decision, reason, cmd):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "hook": "gatekeeper",
                        "decision": decision,
                        "reason": reason,
                        "command": cmd,
                    }
                )
                + "\n"
            )
    except Exception:
        pass


def decide(decision, reason, cmd):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    log(decision, reason, cmd)
    sys.exit(0)


def main():
    data = json.load(sys.stdin)
    ti = data.get("tool_input") or {}
    cmd = ti.get("command") or ti.get("cmd") or data.get("command") or ""
    if not isinstance(cmd, str) or not cmd.strip():
        sys.exit(0)
    low = cmd.lower()

    # --- DENY: secret access ---
    if "jwt_secret" in low or "jwt-secret" in low:
        decide("deny", "Never touch the JWT secret (AGENTS.md: Never).", cmd)
    if re.search(r"\.env\b", cmd) and re.search(
        r"\b(cat|less|more|head|tail|bat|xxd|strings|grep|nl|od|printenv)\b", low
    ):
        decide("deny", "Never read or print .env files (AGENTS.md: Never).", cmd)

    # --- DENY: destructive ---
    if re.search(r"\brm\s+-[a-z]*[rf]", low):
        decide("deny", "Destructive: 'rm -rf' is blocked.", cmd)
    if re.search(r"\bgit\s+push\b.*(--force|\s-f\b)", low):
        decide("deny", "Destructive: 'git push --force' is blocked.", cmd)
    if re.search(r"\bgit\s+reset\s+--hard\b", low):
        decide("deny", "Destructive: 'git reset --hard' is blocked.", cmd)
    if re.search(r"\b(drop|truncate)\s+(table|database)\b", low):
        decide("deny", "Destructive: dropping/truncating a table or database is blocked.", cmd)
    if re.search(r"\bdocker\s+compose\s+down\b.*(-v\b|--volume)", low) or re.search(
        r"\bmake\s+down-v\b", low
    ):
        decide("deny", "Destructive: wiping the database volume (down -v) is blocked.", cmd)
    if ":(){" in cmd.replace(" ", ""):
        decide("deny", "Destructive: fork bomb is blocked.", cmd)

    # --- ASK: new dependency / schema change (AGENTS.md "Ask first") ---
    if (
        re.search(r"\buv\s+(add|remove)\b", low)
        or re.search(r"\bpip\s+install\b", low)
        or re.search(r"\bnpm\s+(install|i|add)\s+\S", low)
        or re.search(r"\b(pnpm|yarn)\s+add\s+\S", low)
    ):
        decide("ask", "Adds/removes a dependency - an AGENTS.md 'Ask first' boundary.", cmd)
    if re.search(r"\balembic\b", low) or re.search(r"\b(create|alter)\s+table\b", low):
        decide("ask", "Schema change - an AGENTS.md 'Ask first' boundary.", cmd)

    # --- ALLOW: everything else ---
    sys.exit(0)


try:
    main()
except Exception:
    sys.exit(0)
