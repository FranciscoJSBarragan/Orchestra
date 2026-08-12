---
name: orchestra-pr-review
description: Converge an authorized Orchestra pull request through direct root observation, independent review of current feedback, accepted fixes by the same implementation owner, affected verification, reviewed commits, and pushes until two clean observations occur on one HEAD. Use only after an authorized PR exists; never merge implicitly or persist local PR state.
---

# Converge an authorized PR

Keep the root responsible for GitHub observation, feedback decisions, routing, blockers, pushes, and the clean conclusion. Keep the previous clean head only in root memory for the immediately following observation. There is no polling or PR-triage profile and no PR observation capability.

## Observe and evaluate

1. Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root. Have the root directly run `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/pr.py" observe --repo <root> --repository <OWNER/REPO> --pr <number> [--previous-clean-head <sha>]`.
2. Read the helper's factual current head, checks, review decision, merge state, unresolved non-outdated feedback, pagination completeness, and clean-observation result. Treat malformed or incomplete evidence as `partial` or `blocked`, never clean.
3. When feedback needs code-review judgment, read `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml`. For a dual matrix, read the immutable model configuration from the approved plan, run the installed `session_model.py`, require its `modelconfig` to match the plan, and resolve `modes.<modelconfig>.tiers.<tier>.independent_review`; a mismatch blocks review dispatch and requires the matching root entry. For a legacy matrix resolve `tiers.<tier>.independent_review`. Dispatch the configured `orchestra_reviewer` with explicit model and reasoning overrides. Supply explicit review authority, task and worktree identity, observation, exact head, PR-CONTEXT capsule, complete current base..HEAD diff, exact approved overview and relevant phase identifiers, current implementation and verification report identifiers, GitHub feedback references, stop conditions, and only the new delta. The reviewer reads intent, scope, and acceptance from those exact artifacts.
4. Require the reviewer to publish `pr-review` only when its semantic analysis must pass to the implementation owner or another reviewer; otherwise its complete inline result is sufficient. Every actionable finding has a stable identifier. The root decides disposition and returns the artifact plus accepted identifiers without restating findings.

## Fix and converge

1. Return every accepted finding to the same `orchestra_implementation_worker` that owned the affected implementation, preserving its original `general_implementation` or `frontend_implementation` capability and playbook. Do not silently transfer ownership.
2. Run affected `runtime_verification` and any required `browser_acceptance`, then send only the meaningful delta to `independent_review`.
3. Commit accepted fixes through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), update the affected phase's terminal manifest commit and, for an adopted Kanban task, update its terminal SHA with `task finish` from the same owning native chat. Then have the root push the current branch directly under the existing `open PR` authority. The fix must remain inside approved intent; new scope requires a new task rather than a manifest update.
4. Clear any remembered clean head after a push or observed head change. Resume with direct observation; do not restart discovery, planning, or unaffected verification.
5. Treat pending or failed checks, required review, changes requested, non-clean merge state, accepted feedback, incomplete thread pagination, or a first clean observation as `partial`.
6. Return `ok` only after two complete clean observations on the same HEAD. Pass the first clean head directly as `--previous-clean-head` for the second observation; never write it to disk.
7. When the PR helper reports `partial` because review threads are paginated (more than 100 threads), the root escalates to the user instead of looping; thread pagination is out of scope.

`Open PR` authority covers this review/fix/commit/push loop only. Stop before merge unless the user separately authorized it, then route to [orchestra-pr-merge](../orchestra-pr-merge/SKILL.md). Never release, deploy, publish, mutate production, or create a local PR state file.
