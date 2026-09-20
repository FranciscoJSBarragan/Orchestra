---
name: orchestra-delivery-policy
description: Choose the authorized Orchestra delivery path after reviewed phase commits are complete. Use when a committed change must be held, opened as a PR, or integrated locally according to explicit repository policy and task-level user direction without inferring authority from Git, GitHub, or CI history.
---

# Choose an authorized delivery path

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Keep the root responsible for reading the user's delivery direction and making the routing decision. Delivery policy is a direct root/helper operation, not a profile or capability assignment. Have the root read repository policy with `${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/policy.py`; do not infer it from branches, PRs, checks, or history.

## Resolve policy and authority

1. Require an independently reviewed, fully verified, committed change, its exact revision, the
   completed plan manifest, its terminal phase commit, checkout mode, and
   recorded resource ownership. Require the effective task HEAD to match that
   terminal commit and require the current review and all configured checks for
   that revision before PR or local delivery; an unexplained mismatch blocks
   use of the completed plan. The durable knowledge checkpoint has already
   run; if it produced an `.agent/` commit, that commit is the terminal one.
   For an adopted Kanban task, require `task finish` to record that same exact
   terminal revision before choosing a delivery lane.
2. Have the root directly run `python3 "${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/policy.py" --repo <root> show` and read its structured result.
3. If the policy is missing, ask the user once and recommend `hybrid`. Return `blocked`; do not create the file or choose for the user.
4. If the user chooses hold, make no delivery mutation and return `ok` with the committed branch or worktree.
5. Allow the PR lane only for `pr-required` or `hybrid`. Require `open PR` or equivalent explicit task direction, then route to [orchestra-pr-open](../orchestra-pr-open/SKILL.md).
6. Allow local integration only for `hybrid` or `local-direct`. Require explicit task-level local integration direction, then route to [orchestra-local-integrate](../orchestra-local-integrate/SKILL.md).
7. If policy and user direction conflict, return `blocked` with the available authorized choices.

Opening a PR authorizes the create/review/fix/commit/push loop through clean status. It never authorizes merge. Local integration authority does not authorize release, deployment, publication, or production mutation. Delivery selection never changes a completed local plan back into execution state. Return only `ok`, `partial`, or `blocked` with compact evidence.

For a subsequent explicitly authorized release, use the repository's release
tooling and WORKFLOW "Review policy" / "Mechanical release metadata". That lane
does not replace the implementation review or terminal-revision delivery gate.

An accepted PR fix that remains inside approved intent may advance the affected
phase's terminal manifest commit after verification, review, and phase commit;
update it before push. New scope or user-visible behavior after `completed` or
`hold` requires a new task and plan.
