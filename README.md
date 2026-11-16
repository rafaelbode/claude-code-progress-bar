# claude-code-progress-bar

A progress bar in the Claude Code status line. It shows which step of your request Claude is on,
so you don't have to ask.

```
Overall █████░░░ 2/3 · Request ████░░░░ 2/4 · adjust CSS · update HTML price table
```

- **Overall**: the bigger goal of the session (e.g. "rebuild the reports page").
- **Request**: the last request you made (e.g. "update the HTML price table").
- Then: the step in progress and a one-line summary of the request.

Both levels are optional. With only the request, the line looks like this:

```
███░░░░░ 1/3 · insert new rows · update HTML price table
```

With nothing in progress, the status line shows just the model and the folder: `Opus · my-project`.

## How it works

1. When you make a request with more than one step, Claude breaks it into steps during
   planning and writes them to `.claude/progress.json`.
2. When it finishes each major step, it marks it done and moves the pointer.
3. A Python script reads that file and draws the bar in the status line.
4. If the request changes direction, the list is rewritten. When a session resumes with a
   summarized context, Claude checks the file before continuing.

Claude follows these rules because they are added to the project's `CLAUDE.md`. It only
updates the file on major steps, to save tokens.

## Install into a project

The installer **only adds**. It never overwrites the `CLAUDE.md`, `.claude/settings.json` or
`.gitignore` already in the project: it appends its section to the end of `CLAUDE.md` between
markers, adds the `statusLine` key to `settings.json` keeping permissions and hooks intact, and
copies the script and the skill only if they don't exist yet. Running it twice duplicates nothing.

Requirements: Python 3 on the PATH, and git.

### Easiest: ask Claude Code

Open Claude Code at the root of the project and paste:

```
Install the progress bar from this repository into the current project without overwriting anything:
https://github.com/YOUR-USER/claude-code-progress-bar

Clone the repository into a temporary folder (outside the project), run
python <temp-folder>/claude-code-progress-bar/install.py pointing at the root of this project,
check the installer output, delete the temporary clone, and show me the line the status line
will display (echo '{}' | python .claude/statusline.py).
```

Then restart the Claude Code session. The bar shows up from the next session on.

### Terminal (one command)

At the project root, in Git Bash, Linux or macOS:

```bash
git clone --depth 1 https://github.com/YOUR-USER/claude-code-progress-bar /tmp/ccpb \
  && python /tmp/ccpb/claude-code-progress-bar/install.py . \
  && rm -rf /tmp/ccpb
```

In PowerShell:

```powershell
git clone --depth 1 https://github.com/YOUR-USER/claude-code-progress-bar $env:TEMP\ccpb
python $env:TEMP\ccpb\claude-code-progress-bar\install.py .
Remove-Item -Recurse -Force $env:TEMP\ccpb
```

### Copying the folder

Copy the `claude-code-progress-bar/` folder into the project and run, at the root:

```bash
python claude-code-progress-bar/install.py
```

You can delete the copied folder afterwards. For a manual, file-by-file install, see
[claude-code-progress-bar/INSTRUCTIONS.md](claude-code-progress-bar/INSTRUCTIONS.md).

## What the installer creates in the project

| Path | What it is |
|---|---|
| `.claude/statusline.py` | script that draws the bar (Python 3, no dependencies) |
| `.claude/settings.json` → `statusLine` key | points the status line at the script |
| `CLAUDE.md` → section between markers | the rules Claude follows to keep the progress file |
| `.claude/skills/progress/SKILL.md` | the `/progress` skill with JSON templates |
| `.gitignore` → `.claude/progress.json` | the progress file is session state, it stays out of git |

## Usage

Nothing to do. Make a multi-step request and the bar appears:

> **You:** update the HTML price table with the values from the new spreadsheet
>
> **Status line:** `███░░░░░ 1/3 · insert new rows · update HTML price table`

For a sequence of related requests, state the bigger goal once and Claude keeps the **Overall**
level while the requests move forward:

> **You:** let's rebuild the reports page: new table, date filter and PDF export.
> Start with the table.
>
> **Status line:** `Overall ░░░░░░░░ 0/3 · Request ██░░░░░░ 1/4 · insert new rows · update HTML table`

Useful commands:

- `/progress` shows the JSON templates and the rules.
- `/progress <request text>` breaks the request into steps and writes the file right away.
- `echo '{}' | python .claude/statusline.py` prints the current line without opening Claude Code.

## `.claude/progress.json` format

```json
{
  "overall": {
    "summary": "rebuild the reports page",
    "steps": [
      {"name": "update HTML table", "done": false},
      {"name": "new date filter", "done": false},
      {"name": "PDF export", "done": false}
    ],
    "current": "update HTML table"
  },
  "request": {
    "summary": "update HTML price table",
    "steps": [
      {"name": "read current table", "done": true},
      {"name": "insert new rows", "done": false},
      {"name": "adjust CSS", "done": false}
    ],
    "current": "insert new rows"
  }
}
```

The flat format `{"summary": "text", "steps": [...], "current": "..."}` is also accepted and
means just the `request` block. The line is truncated at 100 characters.

## Uninstall

```bash
python claude-code-progress-bar/install.py --uninstall
```

Removes only what the installer added: the script, the skill, the `statusLine` key and the
section between markers in `CLAUDE.md`. The rest of the project stays as it was.

To turn off just the bar and keep the rest, delete the `statusLine` key from
`.claude/settings.json`.

## Details

- The status line is loaded when the session starts. After installing, restart Claude Code.
- Claude Code asks you to trust the folder the first time, because the status line runs a
  command. Until you accept, the line stays blank.
- On Windows the command uses an absolute path with forward slashes (`C:/...`), because Claude
  Code doesn't guarantee which folder the command runs in. If you move the project, run the
  installer again or fix the path in `settings.json`.
- The script finds `progress.json` through the `project_dir` that Claude Code sends on stdin.
