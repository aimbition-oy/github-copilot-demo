#!/usr/bin/env python3
"""SessionStart orientation digest.

Injects a short reminder of the system shape and which guardrails are
hook-enforced, plus any in-flight workflow runs. Fail-open (exit 0).
"""

import glob
import json
import os
import sys


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    active = sorted(os.path.basename(p.rstrip("/")) for p in glob.glob("agent-runs/active/*/"))
    runs = ", ".join(active) if active else "none"

    ctx = (
        "Retro Arcade harness. Services: frontend:5173, backend:8000, auth:8001 "
        "(shared JWT secret; two databases). Secret/destructive-command guards and "
        "per-agent write-zones are hook-enforced - see .github/hooks/ and the trail "
        "in agent-runs/audit/hooks.log. "
        f"In-flight workflow runs: {runs}. "
        "Before declaring work done: make lint && make test-unit."
    )

    print(
        json.dumps(
            {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}
        )
    )
    sys.exit(0)


try:
    main()
except Exception:
    sys.exit(0)
