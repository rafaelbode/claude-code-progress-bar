# Progress bar in the Claude Code status line

Shows in the status line which step Claude is on in your request:

```
Overall ███░░░░░ 1/3 · Request ████░░░░ 2/4 · adjust CSS · update HTML price table
```

Two levels, both optional: **Overall** is the bigger goal of the session (e.g. rebuild the
reports page) and **Request** is the last request you made (e.g. update the HTML table).
Claude creates the steps during planning and marks each one as it finishes.

## What is in this folder

| File | Purpose |
|---|---|
| `install.py` | installs into the project without overwriting anything that already exists |
| `statusline.py` | the status line script (Python 3, no dependencies) |
| `skills/progress/SKILL.md` | the `/progress` skill with JSON templates |
| `CLAUDE-snippet.md` | the rules Claude follows; goes at the end of CLAUDE.md |
| `settings-snippet.json` | the `statusLine` key that goes into `.claude/settings.json` |

## Install (easy way)

Copy this folder into the project and run, at the project root:

```bash
python claude-code-progress-bar/install.py
```

Or point it at another folder: `python claude-code-progress-bar/install.py C:/my/project`.

The installer:
- copies `statusline.py` and the skill into `.claude/` **only if they don't exist yet**;
- adds `statusLine` to `.claude/settings.json` keeping everything already there
  (if a status line is already configured, it leaves it alone and says so);
- appends the rules section to the **end** of `CLAUDE.md` between markers,
  without touching what was already written;
- adds `.claude/progress.json` to `.gitignore`.
- writes `.claude/progress-bar.manifest.json` with what it added, so `--uninstall` removes only that.

Then restart the Claude Code session. The bar only appears after you accept the folder
trust prompt, because the status line runs a command.

After installing you can delete the `claude-code-progress-bar/` folder from the project.

## Install by hand

1. Copy `statusline.py` to `.claude/statusline.py`.
2. Copy `skills/progress/` to `.claude/skills/progress/`.
3. Paste the content of `CLAUDE-snippet.md` at the end of your `CLAUDE.md`.
4. In `.claude/settings.json`, add the key from `settings-snippet.json`.
   Use an absolute path with forward slashes in `command`, for example
   `python -I C:/my/project/.claude/statusline.py`, because Claude Code does not guarantee
   which folder the command runs in.

## `.claude/progress.json` format

```json
{
  "overall": {"summary": "rebuild the reports page", "steps": [{"name": "update HTML table", "done": false}], "current": "update HTML table"},
  "request": {"summary": "update HTML price table", "steps": [{"name": "read current table", "done": true}, {"name": "insert new rows", "done": false}], "current": "insert new rows"}
}
```

With only `request` the line is `███░░░░░ 1/3 · current step · request summary`.
Without the file, the status line shows just the model and the folder. The line is cut at 100 characters.

To see the line without opening Claude Code:

```bash
echo '{}' | python .claude/statusline.py
```

## Turn it off

```bash
python claude-code-progress-bar/install.py --uninstall
```

Removes only what the installer added, according to the manifest: the script, the skill, the
`statusLine` key and the section between markers in CLAUDE.md. A `statusline.py` or skill that
was already in the project before installing is left alone. Or, by hand, delete the `statusLine` key
from `.claude/settings.json` (the rules in CLAUDE.md can stay, they don't get in the way).
