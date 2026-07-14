---
name: orchestra-pr-merge
description: Merge one clean Orchestra pull request only after separate explicit merge authorization, current-head confirmation, and fresh configured checks. Use when PR review has produced two clean observations on one HEAD and the user has authorized a specific merge method; never infer merge, release, or deployment authority.
---

# Merge one clean PR

Keep verification and the merge decision at the root; do not add a PR-merge profile.

## Execute the merge contract

1. Require separate explicit merge authority, the exact clean head, PR number, explicit `OWNER/REPO`, repository root, and chosen `merge`, `squash`, or `rebase` method.
2. Confirm [orchestra-pr-review](../orchestra-pr-review/SKILL.md) returned two complete clean observations on that same head.
3. Run `python3 codex/scripts/pr.py merge --repo <root> --repository <OWNER/REPO> --pr <number> --clean-head <sha> --method <method> --authorized` through [pr.py](../../scripts/pr.py).
4. Require the helper to load [orchestra.toml](../../../orchestra.toml) through [policy.py](../../scripts/policy.py), require a clean worktree, match local HEAD and current GitHub head, require a clean merge state, and run configured argv checks at the current repository.
5. After checks, require the same clean worktree, exact local and GitHub head, open PR, and clean merge state before calling `gh pr merge` directly.
6. Return `ok` only when a post-merge GitHub query reports `MERGED`, the same head, and a nonempty merge timestamp. Return `partial` after an exit-zero merge when that post-state is not proven, because a mutation may already exist.

Never merge on stale clean evidence, bypass policy or configured checks, push, force, release, deploy, publish, or mutate production.
