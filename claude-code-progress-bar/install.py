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
- records what it did in .claude/progress-bar.manifest.json

--uninstall removes only what this installer added. It reads the manifest; without one,
it only removes a file whose content matches the package copy, and the statusLine key only
when it points at a script that is ours.
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARK_START = "<!-- claude-code-progress-bar:start -->"
MARK_END = "<!-- claude-code-progress-bar:end -->"
IGNORE_ENTRY = ".claude/progress.json"
MANIFEST = os.path.join(".claude", "progress-bar.manifest.json")

# (package source, path inside the project)
FILES = (
    (os.path.join(HERE, "statusline.py"), os.path.join(".claude", "statusline.py")),
    (os.path.join(HERE, "skills", "progress", "SKILL.md"),
     os.path.join(".claude", "skills", "progress", "SKILL.md")),
)


def log(msg):
    print("  " + msg)


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def read_json(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    return json.loads(raw) if raw else {}


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ---------------------------------------------------------------- install

def copy_if_missing(src, dst):
    """Returns True when the file was created by us."""
    if os.path.exists(dst):
        log(f"already exists, kept: {dst}")
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    log(f"created: {dst}")
    return True


def install_settings(root):
    """Returns True when the statusLine key was added by us."""
    path = os.path.join(root, ".claude", "settings.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {}
    if os.path.exists(path):
        try:
            data = read_json(path)
        except json.JSONDecodeError:
            log(f"ERROR: {path} is not valid JSON; statusLine was NOT configured. Edit it by hand.")
            return False
    if "statusLine" in data:
        if "statusline.py" in str((data["statusLine"] or {}).get("command", "")):
            log(f"progress bar statusLine already configured in {path}, kept")
        else:
            log(f"a DIFFERENT statusLine already exists in {path}, kept. Replace it by hand if you want the bar:")
            log('  "statusLine": {"type": "command", "command": "python -I <root>/.claude/statusline.py"}')
        return False
    snippet = read_json(os.path.join(HERE, "settings-snippet.json"))
    command = snippet["statusLine"]["command"]
    # Absolute path with forward slashes: the docs do not guarantee which folder
    # the status line command runs in.
    script_abs = os.path.join(root, ".claude", "statusline.py").replace("\\", "/")
    snippet["statusLine"]["command"] = command.replace(".claude/statusline.py", script_abs)
    data["statusLine"] = snippet["statusLine"]
    write_json(path, data)
    log(f"statusLine added to {path}")
    return True


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
    manifest_path = os.path.join(root, MANIFEST)
    manifest = {"files": [], "statusLine": False}
    if os.path.exists(manifest_path):
        try:
            manifest.update(read_json(manifest_path))
        except json.JSONDecodeError:
            pass
    for src, rel in FILES:
        if copy_if_missing(src, os.path.join(root, rel)) and rel not in manifest["files"]:
            manifest["files"].append(rel)
    if install_settings(root):
        manifest["statusLine"] = True
    install_claude_md(root)
    install_gitignore(root)
    write_json(manifest_path, manifest)
    print("Done. Restart the Claude Code session for the status line to show up.")


# -------------------------------------------------------------- uninstall

def ours(root, rel, manifest):
    """True if we installed this file (manifest) or its content matches the package copy."""
    if manifest is not None:
        return rel in manifest.get("files", [])
    src = next((s for s, r in FILES if r == rel), None)
    return src is not None and sha256(os.path.join(root, rel)) == sha256(src)


def uninstall(root):
    print(f"Uninstalling from {root}")
    manifest_path = os.path.join(root, MANIFEST)
    manifest = None
    if os.path.exists(manifest_path):
        try:
            manifest = read_json(manifest_path)
        except json.JSONDecodeError:
            manifest = None
    if manifest is None:
        log("no manifest found; removing only files identical to the package copies")

    script_was_ours = False
    for _, rel in FILES:
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            continue
        if ours(root, rel, manifest):
            os.remove(path)
            log(f"removed: {rel}")
            if rel.endswith("statusline.py"):
                script_was_ours = True
        else:
            log(f"not installed by us, kept: {rel}")
    skill_dir = os.path.join(root, ".claude", "skills", "progress")
    if os.path.isdir(skill_dir) and not os.listdir(skill_dir):
        os.rmdir(skill_dir)

    progress = os.path.join(root, IGNORE_ENTRY)
    if os.path.exists(progress):
        os.remove(progress)
        log(f"removed: {IGNORE_ENTRY}")

    path = os.path.join(root, ".claude", "settings.json")
    if os.path.exists(path):
        try:
            data = read_json(path)
        except json.JSONDecodeError:
            data = None
            log("settings.json is not valid JSON; statusLine key left alone")
        if data is not None and "statusLine" in data:
            cmd = str((data.get("statusLine") or {}).get("command", ""))
            added_by_us = manifest.get("statusLine", False) if manifest is not None else script_was_ours
            if added_by_us and "statusline.py" in cmd:
                del data["statusLine"]
                write_json(path, data)
                log("statusLine removed from .claude/settings.json")
            else:
                log("statusLine not added by us, kept")

    path = os.path.join(root, "CLAUDE.md")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        start = text.find(MARK_START)
        end = text.find(MARK_END, start if start >= 0 else 0)
        if start >= 0 and end > start:
            end += len(MARK_END)
            rest = (text[:start].rstrip("\n") + "\n" + text[end:].lstrip("\n")).strip("\n")
            if rest:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(rest + "\n")
                log("section removed from CLAUDE.md")
            else:
                os.remove(path)
                log("CLAUDE.md removed (it only had the progress bar section)")

    if os.path.exists(manifest_path):
        os.remove(manifest_path)
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
