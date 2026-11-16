#!/usr/bin/env python3
"""Claude Code status line with a progress bar.

Reads .claude/progress.json and prints ONE line:

    Overall ███░░░░░ 1/3 · Request ████░░░░ 2/4 · adjust CSS · update HTML price table

With only the "request" block (or the flat format):

    ████░░░░ 2/4 · adjust CSS · update HTML price table

If the file is missing, empty or invalid, prints just the model and the folder
that Claude Code passes on stdin. Python 3, no dependencies.

Legacy Portuguese field names (progresso.json, pedido, etapas, feita, atual, geral)
are still accepted.
"""
import json
import os
import sys

MAX_WIDTH = 100
BAR_WIDTH = 8
FULL = "█"  # █
EMPTY = "░"  # ░
FILE_NAMES = ("progress.json", "progresso.json")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def locate_file(stdin_data):
    """Prefer <project_dir>/.claude/progress.json; fall back to the script's folder."""
    ws = stdin_data.get("workspace") or {}
    bases = [b for b in (ws.get("project_dir"), ws.get("current_dir"), stdin_data.get("cwd")) if b]
    bases = [os.path.join(b, ".claude") for b in bases] + [SCRIPT_DIR]
    for base in bases:
        for name in FILE_NAMES:
            candidate = os.path.join(base, name)
            if os.path.isfile(candidate):
                return candidate
    return os.path.join(SCRIPT_DIR, FILE_NAMES[0])


def read_stdin():
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def read_progress(path):
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        if not raw.strip():
            return None
        data = json.loads(raw)
        return data if isinstance(data, dict) and data else None
    except Exception:
        return None


def pick(d, *keys):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def normalize(block):
    """Return (summary, done, total, current) or None if the block is not usable."""
    if not isinstance(block, dict):
        return None
    steps = pick(block, "steps", "etapas") or []
    if not isinstance(steps, list) or not steps:
        return None
    steps = [s for s in steps if isinstance(s, dict)]
    total = len(steps)
    if not total:
        return None
    done = sum(1 for s in steps if pick(s, "done", "feita"))
    current = pick(block, "current", "atual") or ""
    if not current:
        pending = [pick(s, "name", "nome") or "" for s in steps if not pick(s, "done", "feita")]
        current = pending[0] if pending else "done"
    summary = pick(block, "summary", "pedido", "name", "nome") or ""
    return str(summary).strip(), done, total, str(current).strip()


def bar(done, total):
    filled = round(BAR_WIDTH * done / total) if total else 0
    return FULL * filled + EMPTY * (BAR_WIDTH - filled)


def truncate(text, limit):
    if len(text) <= limit:
        return text
    return text[: max(limit - 1, 0)].rstrip() + "…"


def default_line(stdin_data):
    model = (stdin_data.get("model") or {}).get("display_name") or ""
    folder = (stdin_data.get("workspace") or {}).get("current_dir") or stdin_data.get("cwd") or os.getcwd()
    parts = [p for p in (model, os.path.basename(folder.rstrip("/\\")) or folder) if p]
    return truncate(" · ".join(parts), MAX_WIDTH)


def progress_line(data):
    # Flat format ({"summary": "...", "steps": [...], "current": "..."}) = request only.
    if isinstance(pick(data, "steps", "etapas"), list):
        request = normalize(data)
    else:
        request = normalize(pick(data, "request", "pedido"))
    overall = normalize(pick(data, "overall", "geral"))

    if request is None and overall is None:
        return None

    blocks = []
    if overall and request:
        blocks.append(f"Overall {bar(overall[1], overall[2])} {overall[1]}/{overall[2]}")
        blocks.append(f"Request {bar(request[1], request[2])} {request[1]}/{request[2]}")
        main_block = request
    else:
        main_block = request or overall
        blocks.append(f"{bar(main_block[1], main_block[2])} {main_block[1]}/{main_block[2]}")

    prefix = " · ".join(blocks)
    text = " · ".join(t for t in (main_block[3], main_block[0]) if t)
    room = MAX_WIDTH - len(prefix) - 3
    if text and room > 3:
        return prefix + " · " + truncate(text, room)
    return truncate(prefix, MAX_WIDTH)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    stdin_data = read_stdin()
    data = read_progress(locate_file(stdin_data))
    line = progress_line(data) if data else None
    print(line if line else default_line(stdin_data))


if __name__ == "__main__":
    main()
