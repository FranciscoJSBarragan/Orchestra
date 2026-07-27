---
name: orchestra-pr-merge
description: Merge one clean Orchestra pull request only after separate explicit merge authorization, current-head confirmation, and fresh configured checks. Use when PR review has produced two clean observations on one HEAD and the user has authorized a specific merge method; never infer merge, release, or deployment authority.
---

# Merge one clean PR

Keep verification, direct helper invocation, and the merge decision at the root. PR merge is not a profile or capability assignment.

## Execute the merge contract

1. Require separate explicit merge authority, the exact clean head, PR number, explicit `OWNER/REPO`, distinct task and base worktree roots, task and base branch names, remote name, and chosen `merge`, `squash`, or `rebase` method.
2. Confirm [orchestra-pr-review](../orchestra-pr-review/SKILL.md) returned two complete clean observations on that same head.
3. Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root, then have the root directly run `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/pr.py" merge --repo <task-worktree> --base-worktree <base-worktree> --task-branch <task-branch> --base-branch <base-branch> --remote <remote> --repository <OWNER/REPO> --pr <number> --clean-head <sha> --method <method> --authorized` and read its structured result.
4. Require the helper to load `<repo>/orchestra.toml` through `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/policy.py`, require a clean worktree, match local HEAD and current GitHub head, require a clean merge state, and run configured argv checks at the current repository.
5. After checks, require the same clean worktree, exact local and GitHub head, open PR, and clean merge state before calling `gh pr merge` directly.
6. After a post-merge GitHub query reports `MERGED`, the same head, matching task/base branches, and a nonempty merge timestamp, remove the exact clean task worktree and guarded local ref. Delete the unchanged remote task branch with a lease; an already absent remote branch is clean and a moved branch is retained.
7. Return `ok` when merge and every cleanup action finish. Return `partial` after a successful merge only when intended post-state verification or cleanup is incomplete, with every retained resource named.

Never merge on stale clean evidence, bypass policy or configured checks, rewrite a moved ref, delete a dirty or ambiguous worktree, release, deploy, publish, or mutate production.
