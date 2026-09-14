---
name: orchestra-pr-review
description: Converge an authorized Orchestra pull request through host-adapted independent review, accepted fixes, required checks, and two clean observations on one HEAD; never merge implicitly.
---

# Converge an authorized PR

Keep the root responsible for GitHub observation, feedback disposition, routing,
blockers, pushes, and the clean conclusion. Read WORKFLOW `PR path`, `Review
policy`, and the selected host adapter before dispatching any reviewer. This
skill never merges, releases, deploys, publishes, or persists PR state.

## Observe and review

1. Run `python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/pr.py" observe
   --repo <root> --repository <OWNER/REPO> --pr <number>` with the optional
   in-memory `--previous-clean-head <sha>`. Include repeatable
   `--acknowledged-feedback <fingerprint>` only after independent disposition
   of supplemental review bodies and issue comments. Tokens bind repository,
   PR, head, and exact content. Never use acknowledgements to bypass unresolved
   threads; pass the accepted tokens to the merge helper too.
2. Treat current head, checks, review decision, merge state, unresolved
   non-outdated feedback, pagination completeness, and clean-observation
   fields as external facts. Malformed or incomplete evidence is `partial` or
   `blocked`, never clean.
3. Resolve `independent_review` through the selected host adapter. Codex reads
   its installed matrix and runs `session_model.py` only for dual Codex mode;
   Cursor reads `${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/cursor/roles.toml`
   and its adapter; Grok reads the corresponding `hosts/grok/roles.toml` and
   adapter. Cursor and Grok never use `CODEX_HOME` or `session_model.py`.
   Require the resolved mode and tier to match the approved plan, then pass
   the explicit model and effort fields supported by that host.
4. Require a current independent baseline review before declaring a PR clean;
   reuse it for unchanged code and feedback. Dispatch `orchestra_reviewer`
   when new feedback needs semantic judgment. Supply review authority, task and
   worktree identity, observation, exact head, PR-CONTEXT, complete current
   base..HEAD diff, approved overview and phase IDs, current
   `implementation-report`, every required `verification-report`, GitHub
   feedback, stop conditions, and only the new delta. A gate of `none` needs
   no verification report. The reviewer reads intent and acceptance from the
   exact artifacts.
5. Require `pr-review` when semantic findings must pass to the owner or before
   a delivery commit. Every actionable finding has a stable identifier.

## Fix and converge

1. Return accepted findings to the same logical implementation owner and keep
   its capability and playbook. If that owner is confirmed closed or
   unavailable, spawn one replacement with the exact approved artifacts,
   accepted IDs, and existing ownership label; do not invent a new role or
   silently transfer scope.
2. The owner applies only accepted in-scope fixes, runs every affected required
   deterministic check (including the canonical full suite when required),
   and publishes a replacement `implementation-report`. Rerun each applicable
   independent gate with the same verifier when available; replace it only
   after confirmed unavailability. Send the meaningful delta and replacement
   evidence to the same reviewer when available. If that reviewer is closed or
   unavailable, dispatch a fresh independent reviewer with the full-review
   base, prior dispositions, and exact current evidence.
3. Do not commit or push until the current reviewer accepts the meaningful
   delta, all required checks are fresh, and the affected phase's review and
   verification evidence is complete. Commit through
   [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) and update the
   phase terminal manifest before pushing under the existing PR authority.
   Refresh the PR-CONTEXT capsule from the complete resulting branch range
   through `orchestra-pr-open`; preserve the human body and approved intent.
4. Clear the remembered clean head and supplemental dispositions after a push or observed head change and
   resume direct observation. Do not restart discovery, planning, or unaffected
   verification.
5. Treat pending or failed checks, required review, changes requested,
   non-clean merge state, accepted feedback, incomplete pagination, or the
   first clean observation as `partial`.
   Clear the previous clean observation whenever new or unresolved feedback
   or non-clean checks interrupt convergence. Only consecutive clean
   observations count; adjudicating new feedback begins a new pair.
6. Return `ok` only after two complete clean observations on the same HEAD;
   pass the first clean head in memory to the second observation.
7. If pagination exceeds the helper's bound, collect all remaining pages with
   the same GitHub API under read-only authority. Keep the result partial until
   completeness is proven; do not loop on an unchanged truncated response.
8. Resolve an accepted fixed thread through GitHub only after the fix is
   reviewed and pushed, using its exact thread ID and current head. Resolution
   is covered by PR-processing authority; posting replies requires separate
   messaging authority. Re-observe after resolution. A rejected finding stays
   unresolved unless authorized resolution is justified by independent review.

`Open PR` authority covers opening, review, fixes, required checks, commits,
and pushes needed to make that PR clean. Merge still requires separate explicit
authorization through [orchestra-pr-merge](../orchestra-pr-merge/SKILL.md).
