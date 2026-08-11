---
name: orchestra-task
description: Use only for an explicit `$orchestra-task` invocation to durably capture one software task, start or continue its dedicated persistent Codex-Orchestra discovery thread, answer its exact checkpoint, inspect status, or archive/restore it. Do not use for ordinary mentions of tasks or Orchestra.
---

# Orchestra Task

Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root and invoke the
deterministic helper at
`${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/task_control.py`. Never write
`control.sqlite3` directly.

## Start a durable discovery task

1. Require an explicit user invocation and a non-empty objective.
2. Resolve the current canonical Git root when one exists. If no repository is
   known, create the task first and report its identifier plus
   `needs_repository`; do not invent a path.
3. Create the task with a caller-stable idempotency key and exact origin
   references when available.
4. Start the run only after creation succeeds. The helper launches the
   dedicated root, invokes `$orchestra`, and returns the first structured
   checkpoint.
5. Present the task ID, current checkpoint message, and next user decision.
   Never interpret task status as implementation authority.

Example:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/task_control.py" \
  task create --title "<title>" --brief "<brief>" \
  --source-harness codex --idempotency-key "<stable-key>" \
  --repository "<canonical-root>"
```

Then use the returned task ID:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/task_control.py" \
  run start --task "<task-id>" --repository "<canonical-root>"
```

## Continue or manage

- Answer a checkpoint with `run respond --task ... --response-to ... --text ...`
  and a new stable idempotency key.
- Inspect with `task get` or `run status`.
- Cancel reversibly with `task cancel`; preserve the task, thread UUID,
  checkpoint, and work. Continue with `run reopen` without replaying a command.
- Inspect App Server requests with `run interactions`, record one exact JSON
  response with `run resolve`, then reopen. Responses are exact and one-use.
- Add later context with `task note`.
- Archive only on explicit direction. `task archive` never deletes worktrees,
  branches, artifacts, or the Codex thread. Restore does not send a turn.
- On `busy`, `blocked`, or `needs_reconciliation`, report the exact reason and
  stop. Never retry a turn, replace a UUID, or bypass a denied approval.

The run first stops for the user's tier choice. After that response, its next
discovery stopping point is a candidate specification grounded by mandatory
Orchestra repository context. Formal planning and implementation retain the
existing `$orchestra` approval gates.
