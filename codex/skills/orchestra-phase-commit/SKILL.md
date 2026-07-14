---
name: orchestra-phase-commit
description: Commit one accepted Orchestra phase with an exact path scope and verified structured message. Use after implementation, targeted verification, and independent review have passed and the phase committer must preserve unrelated work, block on unrelated staged paths, stage only authorized paths, commit with git commit -F, verify the stored message and SHA, and return a compact status.
---

# Commit an accepted phase

Receive exact repository-relative authorized paths, the verification summary, revision evidence, and a structured message covering why, acceptance, invariants, validation, and risks. Use [phase_committer.toml](../../agents/phase_committer.toml) as the narrow agent contract.

## Execute the thin path

1. Confirm review and relevant verification passed for the supplied revision.
2. Inspect Git status and the relevant diff for the exact authorized paths.
3. Return `blocked` if any unrelated path is staged or the relevant diff exceeds authority.
4. Write the supplied message to a temporary file outside the repository and arrange its cleanup.
5. Run `python3 codex/scripts/commit_phase.py --repo <root> --message-file <file> --path <path> [--path <path> ...]`. Require the helper to use those exact paths as literal final-commit pathspecs and verify the created commit's changed paths with rename detection disabled.
6. Read the helper's compact JSON result. For `committed`, confirm it contains the verified SHA. For `nothing_to_commit`, make no commit. For `blocked`, report the stable reason and any SHA proving a commit exists; when a SHA is present, do not retry, amend, reset, or recover the created commit.
7. Remove the temporary message file.

Do not edit source, stage unrelated paths, create an alternate index, add recovery state, reset work, merge, push, release, deploy, or infer authority. Git is the commit truth.
