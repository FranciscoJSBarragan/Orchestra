---
name: orchestra-delivery-policy
description: Choose the authorized Orchestra delivery path after reviewed phase commits are complete. Use when a committed change must be held, opened as a PR, or integrated locally according to explicit repository policy and task-level user direction without inferring authority from Git, GitHub, or CI history.
---

# Choose an authorized delivery path

Keep the root responsible for reading the user's delivery direction and making the routing decision. Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root and read the repository policy with `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/policy.py`; do not infer it from branches, PRs, checks, or history.

## Resolve policy and authority

1. Require a reviewed, verified, committed change and its exact revision.
2. Run `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/policy.py" --repo <root> show`.
3. If the policy is missing, ask the user once and recommend `hybrid`. Return `blocked`; do not create the file or choose for the user.
4. If the user chooses hold, make no delivery mutation and return `ok` with the committed branch or worktree.
5. Allow the PR lane only for `pr-required` or `hybrid`. Require `open PR` or equivalent explicit task direction, then route to [orchestra-pr-open](../orchestra-pr-open/SKILL.md).
6. Allow local integration only for `hybrid` or `local-direct`. Require explicit task-level local integration direction, then route to [orchestra-local-integrate](../orchestra-local-integrate/SKILL.md).
7. If policy and user direction conflict, return `blocked` with the available authorized choices.

Opening a PR authorizes the create/review/fix/commit/push loop through clean status. It never authorizes merge. Local integration authority does not authorize release, deployment, publication, or production mutation. Return only `ok`, `partial`, or `blocked` with compact evidence.
