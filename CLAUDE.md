<!-- claude-code-progress-bar:start -->
# Progress bar in the status line

This project's status line shows a progress bar read from `.claude/progress.json`.
You (Claude) maintain that file. Rules:

## When to use it
- Request with **more than one step**: at the start (or when planning is done, before executing),
  write the list of steps to the file.
- **Single-step** request: leave the file alone.
- Update it **only on major steps**, not on every small action (don't spend tokens on it).

## Format (two levels, both optional)
```json
{
  "overall": {"summary": "bigger goal of the session/project", "steps": [{"name": "...", "done": false}], "current": "..."},
  "request": {"summary": "one-line summary of the LAST request", "steps": [{"name": "...", "done": true}], "current": "name of the step in progress"}
}
```
- `request` = the user's last request (e.g. "update HTML table"). This is the level that changes most.
- `overall` = the bigger goal when the user is working through a sequence of related requests
  (e.g. "rebuild the reports page"). Fill it only when that context exists; the current request
  is usually one step of `overall`: mark it done there when the request is finished.
- The flat format `{"summary": "text", "steps": [...], "current": "..."}` is also accepted
  and means just the `request` block.

## Cycle
1. **Planning**: define the steps and write the file with all of them `done: false`
   and `current` = first step.
2. **When a step is finished**: set `done: true` and move `current` to the next one.
3. **If the request changes direction**: rewrite the whole list.
4. **New request**: replace the `request` block; keep `overall` if it still applies.
5. **Resuming a session (summarized context)**: read the file before continuing and pick up from it.
6. **All done**: leave every step `done: true` (the bar fills up). No need to delete the file.

Write the file directly (Write/heredoc), without reading it first if you already know its content.
The `/progress` skill has ready-made templates.
<!-- claude-code-progress-bar:end -->
