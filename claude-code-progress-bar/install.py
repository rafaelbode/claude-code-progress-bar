#!/usr/bin/env python3
"""Installs the progress bar into a project WITHOUT overwriting anything that already exists.

Usage (from the root of the target project, or passing its path):
    python claude-code-progress-bar/install.py              # installs into .
    python claude-code-progress-bar/install.py C:/my/project
    python claude-code-progress-bar/install.py --uninstall

What it does:
- copies statusline.py to .claude/statusline.py (only if missing)
- copies the skill to .claude/skills/progress/SKILL.md (only if missing)
- adds the "statusLine" key to .claude/settings.json, keeping everything else
  (leaves it alone if a statusLine is already configured)
- appends the rules section to the end of CLAUDE.md (does not repeat it if present)
- adds .claude/progress.json to .gitignore

--uninstall removes only what this installer added (recognized by the markers).
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK_START = "<!-- claude-code-progress-bar:start -->"
MARK_END = "<!-- claude-code-progress-bar:end -->"
IGNORE_ENTRY = ".claude/progress.json"


def log(msg):
    print("  " + msg)


def copy_if_missing(src, dst):
    if os.path.exists(dst):
        log(f"already exists, kept: {dst}")
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    log(f"created: {dst}")


def install_settings(root):
    path = os.path.join(root, ".claude", "settings.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            raw = f.read().strip()
        if raw:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                log(f"ERROR: {path} is not valid JSON; statusLine was NOT configured. Edit it by hand.")
                return
    if "statusLine" in data:
        if "statusline.py" in str((data["statusLine"] or {}).get("command", "")):
            log(f"progress bar statusLine already configured in {path}, kept")
        else:
            log(f"a DIFFERENT statusLine already exists in {path}, kept. Replace it by hand if you want the bar:")
            log('  "statusLine": {"type": "command", "command": "python <root>/.claude/statusline.py"}')
        return
    with open(os.path.join(HERE, "settings-snippet.json"), encoding="utf-8") as f:
        snippet = json.load(f)
    command = snippet["statusLine"]["command"]
    # Absolute path with forward slashes: the docs do not guarantee which folder
    # the status line command runs in.
    script_abs = os.path.join(root, ".claude", "statusline.py").replace("\\", "/")
    snippet["statusLine"]["command"] = command.replace(".claude/statusline.py", script_abs)
    data["statusLine"] = snippet["statusLine"]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    log(f"statusLine added to {path}")


def install_claude_md(root):
    path = os.path.join(root, "CLAUDE.md")
    with open(os.path.join(HERE, "CLAUDE-snippet.md"), encoding="utf-8") as f:
        snippet = f.read().strip()
    block = f"\n\n{MARK_START}\n{snippet}\n{MARK_END}\n"
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = f.read()
        if MARK_START in existing:
            log(f"section already present in {path}, kept")
            return
    with open(path, "w", encoding="utf-8") as f:
        f.write(existing.rstrip("\n") + block if existing.strip() else block.lstrip("\n"))
    log(f"section appended to {path}" if existing else f"created: {path}")


def install_gitignore(root):
    path = os.path.join(root, ".gitignore")
    text = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
    if IGNORE_ENTRY in [line.strip() for line in text.splitlines()]:
        return
    with open(path, "a", encoding="utf-8", newline="") as f:
        if text and not text.endswith("\n"):
            f.write("\n")
        f.write(IGNORE_ENTRY + "\n")
    log(f"{IGNORE_ENTRY} added to .gitignore")


def install(root):
    print(f"Installing into {root}")
    copy_if_missing(os.path.join(HERE, "statusline.py"), os.path.join(root, ".claude", "statusline.py"))
    copy_if_missing(os.path.join(HERE, "skills", "progress", "SKILL.md"),
                    os.path.join(root, ".claude", "skills", "progress", "SKILL.md"))
    install_settings(root)
    install_claude_md(root)
    install_gitignore(root)
    print("Done. Restart the Claude Code session for the status line to show up.")


def uninstall(root):
    print(f"Uninstalling from {root}")
    for rel in (".claude/statusline.py", ".claude/skills/progress/SKILL.md", ".claude/progress.json"):
        path = os.path.join(root, rel)
        if os.path.exists(path):
            os.remove(path)
            log(f"removed: {rel}")
    skill_dir = os.path.join(root, ".claude", "skills", "progress")
    if os.path.isdir(skill_dir) and not os.listdir(skill_dir):
        os.rmdir(skill_dir)
    path = os.path.join(root, ".claude", "settings.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        cmd = (data.get("statusLine") or {}).get("command", "")
        if "statusline.py" in cmd:
            del data["statusLine"]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            log("statusLine removed from .claude/settings.json")
    path = os.path.join(root, "CLAUDE.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if MARK_START in text and MARK_END in text:
            start = text.index(MARK_START)
            end = text.index(MARK_END) + len(MARK_END)
            rest = (text[:start].rstrip("\n") + "\n" + text[end:].lstrip("\n")).strip("\n")
            if rest:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(rest + "\n")
                log("section removed from CLAUDE.md")
            else:
                os.remove(path)
                log("CLAUDE.md removed (it only had the progress bar section)")
    print("Done.")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    args = list(sys.argv[1:])
    remove = "--uninstall" in args
    args = [a for a in args if a != "--uninstall"]
    root = os.path.abspath(args[0] if args else os.getcwd())
    if not os.path.isdir(root):
        sys.exit(f"Folder not found: {root}")
    (uninstall if remove else install)(root)


if __name__ == "__main__":
    main()
