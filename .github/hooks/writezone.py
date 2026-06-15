#!/usr/bin/env python3
"""Agent-scoped PreToolUse write-zone guard.

Usage (from a .agent.md hook): writezone.py <role>
Roles: coordinator | implementer | docwriter

Makes the documented write-zones a guarantee: an agent may only WRITE files inside
its zone, and no agent may write node_modules / .venv / .env. Reads, searches, and
everything else are always allowed - an agent must be free to read the plan, the
docs, and the code anywhere. The guard therefore fires only on write/edit tools.

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

# A tool counts as a write if its name contains any of these (VS Code Copilot
# file-writing tools: create_file, multi_replace_string_in_file,
# replace_string_in_file, insert_edit_into_file, apply_patch, create_directory,
# edit_notebook_file, ...). Reads/searches/terminal never match -> always allowed.
WRITE_HINTS = (
    "create_file",
    "create_directory",
    "replace_string",
    "multi_replace",
    "insert_edit",
    "apply_patch",
    "edit",
    "write_file",
    "notebook_edit",
    "rename",
    "move_file",
)

LOG = pathlib.Path("agent-runs/audit/hooks.log")


def is_write_tool(name):
    n = (name or "").lower()
    return any(h in n for h in WRITE_HINTS)


def is_env_secret(basename):
    return basename.startswith(".env") and basename != ".env.example"


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

    # Only gate writes. Reads/searches/terminal/etc. are always allowed.
    if not is_write_tool(data.get("tool_name", "")):
        sys.exit(0)

    ti = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    paths = [norm(p, cwd).lower() for p in extract_paths(ti)]
    if not paths:
        sys.exit(0)

    # Global hard guard for every role.
    for f in paths:
        if "node_modules/" in f or ".venv/" in f or is_env_secret(os.path.basename(f)):
            deny(role, f"Writing node_modules/.venv/.env is forbidden (AGENTS.md: Never). Blocked: {f}")

    allowed = ZONES.get(role, [])
    bad = [f for f in paths if not any(f.startswith(z) for z in allowed)]
    if bad:
        deny(role, f"{role} write-zone violation: {bad}. Allowed prefixes: {allowed}")

    sys.exit(0)


try:
    main()
except Exception:
    sys.exit(0)
