#!/usr/bin/env python3
"""Global PostToolUse: auto-format the just-edited file.

.py  -> `uv run ruff format` + `uv run ruff check --fix` in the owning service
        (auth/ or backend/) so it picks up that service's pyproject + venv.
.ts/.tsx -> `npx eslint --fix` in frontend/ (the repo has ESLint, no Prettier).
Other extensions (incl. .css) are skipped.

Only the edited file is touched. Fail-open: formatter errors are ignored and the
exit code is always 0, so a missing tool never blocks an edit.
"""

import json
import os
import pathlib
import subprocess
import sys


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


def main():
    data = json.load(sys.stdin)
    ti = data.get("tool_input") or {}
    cwd = data.get("cwd") or os.getcwd()
    formatted = []

    for raw in extract_paths(ti):
        p = raw.replace("file://", "")
        absf = p if os.path.isabs(p) else os.path.join(cwd, p)
        try:
            rel = pathlib.PurePosixPath(os.path.relpath(absf, cwd)).as_posix()
        except Exception:
            rel = p
        low = rel.lower()
        if "node_modules/" in low or ".venv/" in low:
            continue
        try:
            if low.endswith(".py"):
                svc = "auth" if low.startswith("auth/") else "backend"
                svcdir = os.path.join(cwd, svc)
                subprocess.run(
                    ["uv", "run", "ruff", "format", absf],
                    cwd=svcdir,
                    capture_output=True,
                    timeout=25,
                )
                subprocess.run(
                    ["uv", "run", "ruff", "check", "--fix", absf],
                    cwd=svcdir,
                    capture_output=True,
                    timeout=25,
                )
                formatted.append(rel)
            elif low.endswith(".ts") or low.endswith(".tsx"):
                subprocess.run(
                    ["npx", "eslint", "--fix", absf],
                    cwd=os.path.join(cwd, "frontend"),
                    capture_output=True,
                    timeout=25,
                )
                formatted.append(rel)
        except Exception:
            pass

    if formatted:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": "Auto-formatted: " + ", ".join(formatted),
                    }
                }
            )
        )
    sys.exit(0)


try:
    main()
except Exception:
    sys.exit(0)
