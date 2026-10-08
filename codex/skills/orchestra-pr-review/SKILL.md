---
name: orchestra-pr-review
description: Converge an authorized Orchestra pull request through host-adapted independent review, accepted fixes, required checks, and a clean observation of the current HEAD; never merge implicitly.
---

# Converge an authorized PR

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Keep the root responsible for GitHub observation, feedback disposition, routing,
blockers, pushes, and the clean conclusion. Read WORKFLOW `PR path`, `Review
policy`, and the selected host adapter before dispatching any reviewer. This
skill never merges, releases, deploys, publishes, or persists PR state.

## Observe and review

1. Run `python3 "${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/pr.py" observe
   --repo <root> --repository <OWNER/REPO> --pr <number>`. Include repeatable
   `--acknowledged-feedback <fingerprint>` only after triage of supplemental
   review bodies and issue comments. Tokens bind repository,
   PR, head, and exact content. Never use acknowledgements to bypass unresolved
   threads; pass the accepted tokens to the merge helper too.
2. Treat current head, checks, review decision, merge state, unresolved
   non-outdated feedback, pagination completeness, and clean-observation
   fields as external facts. Malformed or incomplete evidence is `partial` or
   `blocked`, never clean.
3. Resolve `independent_review` through the owning host adapter's native
   matrix or the explicitly selected execution preset. Match the approved
   host, tier, and recorded assignments before dispatch, including WORKFLOW's
   transition boundary for a plan from the retired external integration.
   Pass the exact model and effort fields supported by that host.
4. Require the terminal review WORKFLOW `Review policy` defines before
   declaring a PR clean, and reuse it for unchanged code. Triage GitHub
   feedback under that policy; dispatch `orchestra_reviewer` only for
   feedback whose validity needs investigation. Supply review authority, task
   and worktree identity, observation, exact head, PR-CONTEXT, complete current
   base..HEAD diff, approved overview and phase IDs, current
   `implementation-report`, every required `verification-report` (none for a
   gate of `none`), GitHub feedback, stop conditions, and only the new delta.
   A multi-phase baseline packet carries no earlier implementation or PR
   review.
5. Require `pr-review` when semantic findings must pass to the owner or before
   a delivery commit. Every actionable finding has a stable identifier.

## Fix and converge

1. Return accepted findings to the same logical implementation owner and keep
   its capability and playbook. If that owner is confirmed closed or
   unavailable, spawn one replacement with the exact approved artifacts,
   accepted IDs, and existing ownership label; do not invent a new role or
   silently transfer scope.
2. The owner applies only accepted fixes, reruns the checks they affect, and
   publishes a replacement `implementation-report`. Rerun only an affected
   independent gate, with the same verifier when available; replace it only
   after confirmed unavailability. Send the meaningful delta and replacement
   evidence to the same reviewer when available. If that reviewer is closed or
   unavailable, dispatch a fresh independent reviewer with the full-review
   base, prior dispositions, and exact current evidence.
3. Do not commit or push until the current reviewer accepts the meaningful
   delta, the affected checks are fresh, and the affected phase's review and
   verification evidence is complete. Commit through
   [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) and update the
   phase terminal manifest before pushing under the existing PR authority.
   Refresh the PR-CONTEXT capsule from the complete resulting branch range
   through `orchestra-pr-open`; preserve the human body and approved intent.
4. Clear supplemental dispositions after a push or observed head change and
   resume direct observation. Do not restart discovery, planning, or unaffected
   verification.
5. Treat pending or failed checks, a bot review of the current head still in
   progress, required review, changes requested, non-clean merge state,
   accepted feedback, or incomplete pagination as `partial`.
6. Return `ok` after one complete clean observation of the current HEAD.
7. If pagination exceeds the helper's bound, collect all remaining pages with
   the same GitHub API under read-only authority. Keep the result partial until
   completeness is proven; do not loop on an unchanged truncated response.
8. Resolve a thread through GitHub, by exact thread ID on the current head,
   once its fix is reviewed and pushed or its triage rejected it with
   evidence. Resolution is covered by PR-processing authority; posting replies
   requires separate messaging authority. Re-observe after resolution.

`Open PR` authority covers opening, review, fixes, required checks, commits,
and pushes needed to make that PR clean. Merge still requires separate explicit
authorization through [orchestra-pr-merge](../orchestra-pr-merge/SKILL.md).
