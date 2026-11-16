---
name: progress
description: Creates or updates .claude/progress.json, which feeds the progress bar in the status line. Use when planning a request with more than one step, when a major step is finished, when the request changes direction, or when resuming a session to check where things stopped.
---

# Progress bar (progress.json)

File: `.claude/progress.json` at the project root. The full rules are in CLAUDE.md.

## Template for the last request
```json
{
  "request": {
    "summary": "update HTML price table",
    "steps": [
      {"name": "read current table", "done": false},
      {"name": "insert new rows", "done": false},
      {"name": "adjust CSS", "done": false},
      {"name": "test in the browser", "done": false}
    ],
    "current": "read current table"
  }
}
```

## Template with overall goal + last request
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

## Steps
1. **Plan**: write the file with every step `done: false` and `current` = the first one.
   If a bigger goal is in progress, fill in or keep `overall`.
2. **Finish a step**: set `done: true`, move `current`. Major steps only.
3. **Changed direction**: rewrite the list.
4. **Resuming a session**: read the file and continue from the `current` step.
5. **Request finished**: all `done: true`; if it was a step of `overall`, mark it there too.

To see the line the status line will show:
```bash
echo '{}' | python .claude/statusline.py
```

Invoked with an argument (`/progress <text>`): treat the text as the request summary,
break it into 3 to 8 major steps and write the file.
