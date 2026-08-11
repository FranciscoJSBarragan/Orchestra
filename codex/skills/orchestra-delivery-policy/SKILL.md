---
name: orchestra-delivery-policy
description: Choose the authorized Orchestra delivery path after reviewed phase commits are complete. Use when a committed change must be held, opened as a PR, or integrated locally according to explicit repository policy and task-level user direction without inferring authority from Git, GitHub, or CI history.
---

# Choose an authorized delivery path

Keep the root responsible for reading the user's delivery direction and making the routing decision. Delivery policy is a direct root/helper operation, not a profile or capability assignment. Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root and have the root read repository policy with `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/policy.py`; do not infer it from branches, PRs, checks, or history.

## Resolve policy and authority

1. Require a reviewed, verified, committed change, its exact revision, the
   completed plan manifest, its terminal phase commit, checkout mode, and
   recorded resource ownership. Require the effective task HEAD to match that
   terminal commit before PR or local delivery; an unexplained mismatch blocks
   use of the completed plan.
2. Have the root directly run `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/policy.py" --repo <root> show` and read its structured result.
3. If the policy is missing, ask the user once and recommend `hybrid`. Return `blocked`; do not create the file or choose for the user.
4. If the user chooses hold, make no delivery mutation and return `ok` with the committed branch or worktree.
5. Allow the PR lane only for `pr-required` or `hybrid`. Require `open PR` or equivalent explicit task direction, then route to [orchestra-pr-open](../orchestra-pr-open/SKILL.md).
6. Allow local integration only for `hybrid` or `local-direct`. Require explicit task-level local integration direction, then route to [orchestra-local-integrate](../orchestra-local-integrate/SKILL.md).
7. If policy and user direction conflict, return `blocked` with the available authorized choices.

Opening a PR authorizes the create/review/fix/commit/push loop through clean status. It never authorizes merge. Local integration authority does not authorize release, deployment, publication, or production mutation. Delivery selection never changes a completed local plan back into execution state. Return only `ok`, `partial`, or `blocked` with compact evidence.

An accepted PR fix that remains inside approved intent may advance the affected
phase's terminal manifest commit after verification, review, and phase commit;
update it before push. New scope or user-visible behavior after `completed` or
`hold` requires a new task and plan.
