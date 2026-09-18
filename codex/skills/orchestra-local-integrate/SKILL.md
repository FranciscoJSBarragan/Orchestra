---
name: orchestra-local-integrate
description: Integrate one reviewed Orchestra task into its local base under hybrid or local-direct policy. Use only with explicit task-level local integration authority, clean task and base worktrees, fresh configured checks, conservative fast-forward integration, exact SHA verification, and safe merged-resource cleanup.
---

# Integrate one task locally

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Keep the integration decision, helper invocation, and blocker handling at the root. Local integration is not a profile or capability assignment.

## Execute the local contract

1. Confirm [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md) allows local integration and the user explicitly requested it for this task. Require the current independent code-review artifact for the terminal revision; local delivery never skips review because it has no PR.
2. Require checkout mode, exact task/base checkout identity, task and base branch names, the terminal task revision from the completed plan manifest, repository policy, and the captured starting revision for hybrid tasks.
3. Have the root directly run `python3 "${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/integrate_local.py" --task-worktree <task> --base-worktree <base> --task-branch <task-branch> --base-branch <base-branch> --expected-task-revision <manifest-sha> --checkout-mode <managed|hybrid> [--start-revision <sha>] --authorized` and read its structured result. Managed task/base roots are distinct; hybrid uses the same checkout root.
4. Before integration, require the clean task HEAD to match the supplied terminal manifest revision, the independent review to accept that exact revision, and every configured delivery check to run fresh with its complete result. Then require fast-forward-only integration and confirmation that the base contains that exact task SHA.
5. After verified integration, require `delivery_verified: true` and the exact base `delivery_revision`. If this is an adopted Kanban task, record it from the owning native chat with `task record-delivery --kind local-integration`. Managed mode removes the exact task worktree and branch. Hybrid mode restores and fast-forwards the unchanged starting branch, preserves the checkout, and deletes only the fully merged Orchestra task branch and private task artifacts.
6. Return `partial` when integration succeeded but conservative cleanup could not finish; return `blocked` before mutation on dirty, divergent, unmerged, ambiguous, unauthorized, or failed-check state.

Never force, reset, clean, rewrite history, remove dirty or unmerged resources, release, deploy, publish, or mutate production.
