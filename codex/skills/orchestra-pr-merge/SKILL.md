---
name: orchestra-pr-merge
description: Use only when the user has separately authorized merging a clean Orchestra PR; merges exactly the reviewed head after fresh configured checks and cleans up conservatively.
---

# Merge a clean PR

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Merge one PR whose current head
[orchestra-pr-review](../orchestra-pr-review/SKILL.md) observed clean. Merge
authority is separate from `Open a PR`, as WORKFLOW "Delivery policy" states.

## Requires

- The user's merge authority and merge method.
- A complete clean observation of the current head, which equals the completed
  plan's terminal phase commit.
- The task's migrations ordered under WORKFLOW "Migrations at delivery".
- When the base moved under a pending task, WORKFLOW "Base refresh before
  delivery" first.

## Steps

1. Run `python3 "${ORCHESTRA_RUNTIME_ROOT}/scripts/pr.py" merge --repo
   <task-checkout> --base-worktree <base-checkout> --task-branch <task-branch>
   --base-branch <base-branch> --checkout-mode <managed|hybrid>
   [--start-revision <sha>] --remote <remote> --repository <OWNER/REPO> --pr
   <number> --clean-head <sha> --expected-task-revision <terminal-sha> --method
   <method> [--acknowledged-feedback <token> ...] [--preserve-task-resources]
   --authorized`. Pass `--start-revision` for a hybrid task and, in managed
   mode, `--preserve-task-resources` for a checkout the host owns, such as a
   T3 worktree. The helper deletes the remote task branch with a
   lease and retains anything moved, dirty or ambiguous.
2. Only once the result says `delivery_verified: true`, apply the
   post-delivery part of "Migrations at delivery".
3. With `--preserve-task-resources`, follow the cleanup handoff it returns
   once the host releases the checkout.

Never merge on stale clean evidence, bypass the policy or its checks, rewrite
a moved ref, or release, deploy or touch production.

## Report

`ok` with `delivery_revision` when the merge and every cleanup finished;
`partial` when the merge's post-state or its cleanup is unverified, naming
each retained resource; `blocked` with the reason otherwise.
