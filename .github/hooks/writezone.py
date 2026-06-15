#!/usr/bin/env python3
"""Agent-scoped PreToolUse write-zone guard.

Usage (from a .agent.md hook): writezone.py <role>
Roles: coordinator | implementer | docwriter

Makes the documented write-zones a guarantee: an agent may only edit files inside
its zone, and no agent may edit node_modules / .venv / .env. Denies out-of-zone
edits; allows everything else.

Fail-closed on a matched violation (the guarantee); fail-open on any error
(exit 0, no decision) so a hook bug never freezes the agent.
"""

import datetime
import json
import os
import pathlib
import sys

ZONES = {
    "coordinator": ["agent-runs/active/"],
    "implementer": ["backend/", "auth/", "frontend/", "e2e/"],
    "docwriter": ["docs/", ".github/instructions/", "readme.md", "agents.md"],
}

LOG = pathlib.Path("agent-runs/audit/hooks.log")


def log(role, decision, reason):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
                        "hook": "writezone",
                        "role": role,
                        "decision": decision,
                        "reason": reason,
                    }
                )
                + "\n"
            )
    except Exception:
        pass


def deny(role, reason):
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    log(role, "deny", reason)
    sys.exit(0)


def extract_paths(ti):
    out = []
    for key in ("files", "filePaths", "paths"):
        v = ti.get(key)
        if isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    out.append(item)
                elif isinstance(item, dict):
                    out.append(item.get("path") or item.get("filePath") or item.get("uri") or "")
    for key in ("file_path", "filePath", "path", "uri"):
        v = ti.get(key)
        if isinstance(v, str):
            out.append(v)
    return [p for p in out if p]


def norm(p, cwd):
    p = p.replace("file://", "")
    if os.path.isabs(p) and cwd:
        try:
            p = os.path.relpath(p, cwd)
        except Exception:
            pass
    return pathlib.PurePosixPath(p).as_posix().removeprefix("./")


def main():
    role = sys.argv[1] if len(sys.argv) > 1 else ""
    data = json.load(sys.stdin)
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    paths = [norm(p, cwd).lower() for p in extract_paths(ti)]
    if not paths:
        sys.exit(0)  # not an edit -> allow

    # Global hard guard for every role.
    for f in paths:
        if "node_modules/" in f or ".venv/" in f or os.path.basename(f).startswith(".env"):
            deny(role, f"Editing node_modules/.venv/.env is forbidden (AGENTS.md: Never). Blocked: {f}")

    allowed = ZONES.get(role, [])
    bad = [f for f in paths if not any(f.startswith(z) for z in allowed)]
    if bad:
        deny(role, f"{role} write-zone violation: {bad}. Allowed prefixes: {allowed}")

    sys.exit(0)


try:
    main()
except Exception:
    sys.exit(0)
