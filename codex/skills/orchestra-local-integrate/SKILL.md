---
name: orchestra-local-integrate
description: Integrate one reviewed Orchestra task into its local base under hybrid or local-direct policy. Use only with explicit task-level local integration authority, clean task and base worktrees, fresh configured checks, conservative fast-forward integration, exact SHA verification, and safe merged-resource cleanup.
---

# Integrate one task locally

Keep the integration decision and blocker handling at the root; do not add an integration profile.

## Execute the local contract

1. Confirm [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md) allows local integration and the user explicitly requested it for this task.
2. Require exact task and base worktree roots, task and base branch names, reviewed task revision, and repository policy.
3. Run `python3 codex/scripts/integrate_local.py --task-worktree <task> --base-worktree <base> --task-branch <task-branch> --base-branch <base-branch> --authorized` through [integrate_local.py](../../scripts/integrate_local.py).
4. Require fresh configured argv checks in the clean task worktree, fast-forward-only integration, and confirmation that the base contains the exact captured task SHA.
5. Remove the task worktree only after verified integration and only while both worktrees remain clean. Delete the task branch only after Git proves it fully merged.
6. Return `partial` when integration succeeded but conservative cleanup could not finish; return `blocked` before mutation on dirty, divergent, unmerged, ambiguous, unauthorized, or failed-check state.

Never force, reset, clean, rewrite history, remove dirty or unmerged resources, release, deploy, publish, or mutate production.
