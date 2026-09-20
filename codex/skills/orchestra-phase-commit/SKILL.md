---
name: orchestra-phase-commit
description: Commit one accepted Orchestra phase directly or one explicitly authorized bounded standalone change, using exact path scope and useful intent and verification evidence.
---

# Commit an accepted phase

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Choose `orchestra_phase` or `standalone` using the shared conduct router and
the canonical `${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/WORKFLOW.md` (`Standalone
tools`; source checkout: [runtime resources](../orchestra/runtime.md)). A formal
assignment with missing phase fields is blocked rather than downgraded to a
direct commit.

Commit execution is a root responsibility in `orchestra_phase` mode. Do not
resolve an assignment, spawn a committer profile, or create a commit
capability. The same skill also supports a direct `standalone` commit when the
caller explicitly authorizes that commit. In either mode, stage only exact
repository-relative paths, preserve unrelated work, and let Git remain the
commit truth.

In `orchestra_phase` mode, require the exact current phase artifact, accepted
repository-relative paths, an accepted current-review identifier —
`implementation-review` for ordinary phase completion or `pr-review` for an
accepted PR fix — and every verification-report identifier required by that
phase's `Independent verification gate` for the current revision. A gate of
`none` requires no `verification-report`. Use a concise title plus useful
intent and validation; include risks only when material. The resulting Git
commit is authoritative; never create a duplicate commit artifact.

In `standalone` mode, require explicit commit authority, the target repository
or worktree, exact scoped paths, target and intent, current revision identity
including dirty paths, and a useful verification summary covering the
repository-required checks. Do not require or invent a plan, phase, artifact
ID, `.orchestra` setup, coordination record, tier, or model. Honor any
repository-required review; report whether independent review is present,
absent, or not supplied by the evidence. A standalone commit records the
requested change and its evidence but never certifies independent review.
Return the commit result inline unless the caller supplies an explicit output
path.
For subsequent authorized release preparation, apply WORKFLOW "Mechanical
release metadata" rather than creating a new phase or reviewer dispatch merely
to commit release metadata.

## Execute the direct path

1. In standalone mode, confirm the explicit commit authority and verify that
   the supplied target, intent, exact paths, current revision, required checks,
   and review status are coherent. In phase mode, confirm the exact phase and
   current review and verification identifiers. Stop if the required authority
   or evidence is missing.
2. Inspect Git status and the relevant diff once. Stop if unrelated work is
   already staged or the phase or standalone scope exceeds authority.
3. Write the message to a temporary file outside the repository, stage only
   the accepted or standalone-scoped paths, run `git commit -F <file>`, and
   read the resulting SHA and status once.
4. Use `${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/commit_phase.py` instead
   when exact-path staging benefits from a compact structured result. Pass
   `--repo`, `--message-file`, and each exact `--path`.
5. Accept `committed` with its SHA or `nothing_to_commit`. For `blocked`,
   inspect current status and the latest commit once. If the intended commit
   exists and contains no paths outside scope, accept it and do not retry or
   amend.
6. Keep an isolated mechanical failure root-local. Make one obvious safe
   correction when available; delegate only when repeated evidence points to a
   deeper implementation problem. Remove the temporary message file.

## Result contract

Return `committed`, `nothing_to_commit`, or `blocked` first, followed by the
mode, exact paths, revision or resulting SHA, intent, verification summary,
review status, blockers, and material risks. In phase mode include the exact
phase, review, and required verification IDs. In standalone mode omit those
IDs unless the caller supplied them as ordinary evidence, and state plainly
that the commit does not certify independent review.

## Stop conditions

In standalone mode, stop before mutation when explicit commit authority,
target, intent, exact paths, revision identity, required checks, or any
repository-required review is missing or failing; when unrelated work is
staged; or when the requested commit exceeds the stated scope. In phase mode,
stop when the approved phase, current review, required verification evidence,
or exact path scope cannot be resolved. Never invent approval, weaken a check,
stage unrelated paths, or use a commit as proof that independent review took
place.

Do not stage unrelated paths, create an alternate index, add a crash journal or recovery state, merge, push, release, deploy, or infer authority. Do not require byte-for-byte stored-message equality or empty ceremonial sections. Git and the root's observed scope are the commit truth.
