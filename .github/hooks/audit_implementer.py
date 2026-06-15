#!/usr/bin/env python3
"""Implementer PostToolUse audit log.

Appends one JSON line per edit to agent-runs/audit/implementer.log so a run leaves
a tamper-evident trail of exactly what the Implementer changed. Fail-open: an
audit failure never blocks the agent (exit 0).
"""

import datetime
import json
import pathlib
import sys

LOG = pathlib.Path("agent-runs/audit/implementer.log")


def main():
    data = json.load(sys.stdin)
    ti = data.get("tool_input") or {}

    files = []
    v = ti.get("files")
    if isinstance(v, list):
        for item in v:
            if isinstance(item, str):
                files.append(item)
            elif isinstance(item, dict):
                files.append(item.get("path") or item.get("filePath") or "")
    for key in ("file_path", "filePath", "path"):
        if isinstance(ti.get(key), str):
            files.append(ti[key])
    files = [f for f in files if f]

    resp = data.get("tool_response")
    entry = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "session": data.get("session_id"),
        "agent": data.get("agent_type") or data.get("agent_id"),
        "tool": data.get("tool_name"),
        "files": files,
        "ok": resp.get("success") if isinstance(resp, dict) else None,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    sys.exit(0)


try:
    main()
except Exception:
    sys.exit(0)
