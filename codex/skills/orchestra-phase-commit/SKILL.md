---
name: orchestra-phase-commit
description: Let the root commit one accepted Orchestra phase directly, with the narrow exact-path helper available when useful. Use after implementation, targeted verification, and independent review pass; preserve unrelated work and return the resulting SHA without a committer profile or capability.
---

# Commit an accepted phase

Commit execution is a root responsibility. Do not resolve an assignment, spawn a committer profile, or create a commit capability. Require accepted repository-relative paths and passed review and verification evidence for the current revision. Use a concise title plus useful intent and validation; include risks only when material.

## Execute the direct path

1. Inspect Git status and the relevant diff once. Stop if unrelated work is already staged or the phase exceeds authority.
2. Write the message to a temporary file outside the repository, stage only the accepted paths, run `git commit -F <file>`, and read the resulting SHA and status once.
3. Use `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/commit_phase.py` instead when exact-path staging benefits from a compact structured result. Pass `--repo`, `--message-file`, and each exact `--path`.
4. Accept `committed` with its SHA or `nothing_to_commit`. For `blocked`, inspect current status and the latest commit once. If the intended commit exists and contains no paths outside scope, accept it and do not retry or amend.
5. Keep an isolated mechanical failure root-local. Make one obvious safe correction when available; delegate only when repeated evidence points to a deeper implementation problem. Remove the temporary message file.

Do not stage unrelated paths, create an alternate index, add a crash journal or recovery state, merge, push, release, deploy, or infer authority. Do not require byte-for-byte stored-message equality or empty ceremonial sections. Git and the root's observed scope are the commit truth.
