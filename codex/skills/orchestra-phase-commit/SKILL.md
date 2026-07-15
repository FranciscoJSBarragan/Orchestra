---
name: orchestra-phase-commit
description: Let the root commit one accepted Orchestra phase within an exact path scope using direct Git or the narrow commit helper. Use after implementation, targeted verification, and independent review pass; preserve unrelated work, verify the structured message and resulting SHA, and return a compact result without a committer profile or capability.
---

# Commit an accepted phase

Commit execution is a root responsibility. Do not resolve an assignment, spawn a committer profile, or create a commit capability. Require exact repository-relative authorized paths, passed review and verification evidence for the current revision, and a structured message covering why, acceptance, invariants, validation, and risks.

## Execute the direct path

1. Have the root inspect Git status and the relevant diff for the exact authorized paths. Return `blocked` if an unrelated path is staged or the relevant diff exceeds authority.
2. Write the structured message to a temporary file outside the repository and arrange cleanup.
3. Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root. Have the root directly run `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/commit_phase.py" --repo <root> --message-file <file> --path <path> [--path <path> ...]`.
4. Require exact literal final-commit pathspecs and changed-path verification with rename detection disabled.
5. Read the helper's compact JSON result. For `committed`, require the verified SHA and stored-message confirmation. For `nothing_to_commit`, make no commit. For `blocked`, report one stable reason and any SHA proving a commit exists.
6. When a blocked result contains a SHA, report that the commit already exists and do not retry, amend, reset, or recover it. Remove the temporary file in every path.

The root may use direct Git instead only when it preserves the same scope, structured-message, `git commit -F`, changed-path, stored-message, and SHA checks. Do not edit source, stage unrelated paths, create an alternate index, add a crash journal or recovery state, merge, push, release, deploy, or infer authority. Git is the commit truth.
