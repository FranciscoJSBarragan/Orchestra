---
name: orchestra-pr-merge
description: Merge one clean Orchestra pull request only after separate explicit merge authorization, current-head confirmation, and fresh configured checks. Use when PR review has produced two clean observations on one HEAD and the user has authorized a specific merge method; never infer merge, release, or deployment authority.
---

# Merge one clean PR

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Keep verification, direct helper invocation, and the merge decision at the root. PR merge is not a profile or capability assignment.

## Execute the merge contract

1. Require separate explicit merge authority, checkout mode, the exact clean head, the terminal revision from the completed plan manifest, PR number, explicit `OWNER/REPO`, task/base checkout identity, task and base branch names, remote name, chosen merge method, and the captured starting revision for hybrid tasks.
2. Confirm [orchestra-pr-review](../orchestra-pr-review/SKILL.md) returned two complete clean observations on that same head.
3. Have the root directly run `python3 "${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/pr.py" merge --repo <task-checkout> --base-worktree <base-checkout> --task-branch <task-branch> --base-branch <base-branch> --checkout-mode <managed|hybrid> [--start-revision <sha>] --remote <remote> --repository <OWNER/REPO> --pr <number> --clean-head <sha> --expected-task-revision <manifest-sha> --method <method> [--acknowledged-feedback <fingerprint> ...] --authorized` and read its structured result.
4. Require the helper to load `<repo>/orchestra.toml` through `${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/policy.py`, require a clean worktree, match the supplied terminal manifest revision, local HEAD, clean PR head, and current GitHub head, bind the merge to `--match-head-commit`, require a clean merge state, and run every configured argv check at the current repository.
5. Before and after checks, require the same clean worktree, exact local and GitHub head, open PR, complete feedback with independently adjudicated supplemental comments, and clean merge state. The merge command must pass `--match-head-commit <sha>` so GitHub rejects a head change during the final race.
6. After exact merged-state proof, require `delivery_verified: true` and the exact `delivery_revision` from GitHub's merge commit. If this is an adopted Kanban task, record it from the owning native chat with `task record-delivery --kind pr-merge`. Managed mode removes the clean task worktree and guarded refs. Hybrid mode restores the unchanged starting branch, preserves the checkout, and removes only guarded Orchestra task refs and private artifacts. Delete the unchanged remote task branch with a lease; an absent branch is clean and a moved branch is retained.
7. Return `ok` when merge and every cleanup action finish. Return `partial` after a successful merge only when intended post-state verification or cleanup is incomplete, with every retained resource named.

Never merge on stale clean evidence, bypass policy or configured checks, rewrite a moved ref, delete a dirty or ambiguous worktree, release, deploy, publish, or mutate production.

For an adopted host-owned isolated checkout, follow WORKFLOW "Task checkout and
branch": pass `--preserve-task-resources` in managed mode. The helper still
requires authority, exact revisions and checks. Follow the returned partial
cleanup handoff for the local ref after host release; PR merge still performs
guarded remote-ref cleanup. Preserving the checkout does not silently abandon
child-created refs.
