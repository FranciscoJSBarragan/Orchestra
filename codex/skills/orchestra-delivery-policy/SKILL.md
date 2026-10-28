---
name: orchestra-delivery-policy
description: Use when a reviewed, committed Orchestra task must be held, opened as a PR or integrated locally; routes by the repository's declared policy and the user's direction for this task.
---

# Choose the delivery path

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Route a finished task to hold, a PR or local integration. The rules are
WORKFLOW "Delivery policy"; this skill applies them.

## Requires

- The task HEAD equals the completed plan's terminal phase commit, and the
  current independent review and every configured check cover it. A mismatch
  you cannot explain blocks delivery.
- The durable knowledge checkpoint has run; an `.agent/` commit it made is the
  terminal one.

## Steps

1. Run `python3 "${ORCHESTRA_RUNTIME_ROOT}/scripts/policy.py" --repo <root> show`.
2. No policy: ask the user once, recommend `hybrid` and return `blocked`. Never
   write the file yourself.
3. Hold: change nothing and return `ok` with the branch or worktree.
4. A PR the user asked for, under `pr-required` or `hybrid`:
   [orchestra-pr-open](../orchestra-pr-open/SKILL.md).
5. Local integration the user asked for, under `hybrid` or `local-direct`:
   [orchestra-local-integrate](../orchestra-local-integrate/SKILL.md).
6. Direction and policy conflict: return `blocked` with the choices the policy
   allows.

New scope or a visible change after `completed` or `hold` is a new task.

## Report

`ok`, `partial` or `blocked`, with the chosen path and its evidence.
