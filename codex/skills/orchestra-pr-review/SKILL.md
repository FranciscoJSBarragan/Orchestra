---
name: orchestra-pr-review
description: Converge an authorized Orchestra pull request through factual polling, independent feedback triage, accepted fixes by the existing owner, affected verification, reviewed commits, and pushes until two clean observations occur on the same HEAD. Use only after an authorized PR exists; never merge implicitly or persist local PR state.
---

# Converge an authorized PR

Keep the root responsible for decisions, accepted findings, routing, blockers, and the clean conclusion. Keep the previous clean head only in root memory for the immediately following observation.

## Observe and triage

1. Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root. Resolve `pr_polling_specialist` and `pr_triage_specialist` assignments for the task tier from `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml`. Pass explicit model and reasoning overrides when spawning each profile.
2. Send repository, explicit `OWNER/REPO`, PR number, current revision, and any in-memory previous clean head to the `${CODEX_HOME:-$HOME/.codex}/agents/pr_polling_specialist.toml` profile. It runs `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/pr.py" observe ...` and reports current head, checks, review decision, merge state, and unresolved non-outdated feedback without deciding disposition.
3. If the snapshot has unresolved non-outdated feedback, send that snapshot, PR-CONTEXT, full current diff, intent, code, verification, and scope to the `${CODEX_HOME:-$HOME/.codex}/agents/pr_triage_specialist.toml` profile. It reports only; it never fixes or routes.
4. Have the root accept or reject findings from evidence. Return accepted fixes to the same `${CODEX_HOME:-$HOME/.codex}/agents/implementation_worker.toml` profile that owned implementation.

## Fix and converge

1. Apply accepted fixes, run affected verification, and send the meaningful delta to the reviewer.
2. Commit accepted fixes through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), then have the root push the current branch directly under the existing `open PR` authority.
3. Clear any remembered clean head after a push or observed head change. Resume at polling; do not restart discovery, planning, or unaffected verification.
4. Treat pending or failed checks, required review, changes requested, non-clean merge state, triaged actionable feedback, incomplete thread pagination, or a first clean observation as `partial`.
5. Return `ok` only after two complete clean observations on the same HEAD. Pass the first clean head directly as `--previous-clean-head` for the second observation; never write it to disk.

`Open PR` authority covers this review/fix/commit/push loop only. Stop before merge unless the user separately authorized it, then route to [orchestra-pr-merge](../orchestra-pr-merge/SKILL.md). Never release, deploy, publish, or mutate production.
