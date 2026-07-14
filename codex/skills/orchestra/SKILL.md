---
name: orchestra
description: Route software changes through Orchestra's proportional light, standard, or critical workflow. Use when the root must classify implementation risk, gather bounded repository or current external evidence, create and align a formal plan, require user approval before planned implementation, coordinate reviewed phase commits, diagnose repeated local failures, or run Chrome acceptance through Computer Use without taking delivery actions.
---

# Route an Orchestra change

Keep the root orchestrator responsible for problem framing, tier selection, user alignment, routing, compact synthesis, blocker resolution, ordinary reversible in-scope decisions, and final technical judgment. Use the root's current session configuration, selected outside Orchestra; do not configure or respawn the root.

## Classify before dispatch

Declare `Tier: light|standard|critical — reason` before execution. Select `light` only when all of these facts are proven:

- one small, fully understood objective;
- localized impact following an established pattern;
- no public API, schema, CLI, persisted format, dependency, or architecture change;
- no auth, security, privacy, payment, migration, production, deployment, destructive, or irreversible risk;
- no unresolved product decision;
- one direct targeted verification exists.

Fail closed to `standard` on any ambiguity, unknown scope, new coupling, or risk. Select `critical` for security-sensitive work, credentials, payments, migrations, destructive actions, production changes, or comparable high-impact risk.

## Resolve role assignments

Read [roles.toml](../../config/roles.toml) as the only machine-readable model and reasoning matrix for spawned specialists. Resolve `tiers.<tier>.<role>` and pass its `model` and `reasoning_effort` as explicit overrides for every spawned role:

- use [repo_context_explorer.toml](../../agents/repo_context_explorer.toml) for `repo_context_explorer`;
- use [planner.toml](../../agents/planner.toml) for `planner`;
- use [plan_scope_auditor.toml](../../agents/plan_scope_auditor.toml) for `plan_scope_auditor` only with a complete risk-based audit packet;
- use [implementation_worker.toml](../../agents/implementation_worker.toml) for `implementation_worker`;
- use [reviewer.toml](../../agents/reviewer.toml) for `reviewer` and a justified `reviewer_second_pass`;
- use [debugging_investigator.toml](../../agents/debugging_investigator.toml) for `debugging_investigator` after the same failure repeats;
- use [web_researcher.toml](../../agents/web_researcher.toml) for narrow, current `web_researcher` evidence;
- use [browser_acceptance_tester.toml](../../agents/browser_acceptance_tester.toml) for `browser_acceptance_tester` scenarios;
- use [phase_committer.toml](../../agents/phase_committer.toml) for `phase_committer`.

Do not copy assignments into profiles or this skill. Profiles report to the root; they never spawn agents or become orchestrators.

## Keep compact context

Keep one compact packet in memory with: objective; known decisions and context delta; allowed paths; acceptance; verification; exclusions; stop conditions; references and revision. Reuse still-valid evidence and send only changed context deltas after the first pass. Do not write packets, workflow state, transition logs, or authority bundles.

## Route light work

1. Send the packet to one `implementation_worker`.
2. Require targeted verification and observed results.
3. Send the packet, relevant diff, evidence, and revision to one independent `reviewer`. Do not ask the reviewer to edit.
4. Evaluate material findings at the root and return accepted findings to the same implementation owner.
5. Re-run affected verification and review only the meaningful delta.
6. Send accepted exact paths, structured message, and verification summary to `phase_committer` through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md).

## Route standard and critical work

1. Send focused discovery questions to one bounded `repo_context_explorer`. Add `web_researcher` only for necessary time-sensitive external questions, using current primary-source evidence.
2. Have the root synthesize evidence, align objective, constraints, acceptance, and product choices with the user, and update only the context delta.
3. Send the aligned packet to `planner` for a formal executable phase plan.
4. Dispatch `plan_scope_auditor` only when the packet names a measurable risk, its supporting evidence and affected area, and the independent defect class the audit could detect. Architectural complexity alone is insufficient; do not add ceremonial audit.
5. Have the root summarize the plan and request explicit user approval. Stop before any standard or critical implementation until approval is received.
6. Treat approval as authority for the approved phase implementation and successful phase commits only. Do not treat it as merge, delivery, release, deployment, or production authority.
7. For each approved phase, send its bounded packet to the same `implementation_worker`, run targeted verification, then send the revision and relevant evidence to one independent `reviewer` that reports without editing.
8. For critical work, add `reviewer_second_pass` only when the packet names a measurable risk, supporting evidence and affected area, and the independent defect class a second reviewer could detect. Reuse `reviewer.toml` and review only the relevant delta.
9. Return accepted findings to the same implementation owner, re-run affected verification, and commit an accepted phase through `phase_committer`.
10. When the same local failure repeats, stop retrying and send only that failure evidence and context delta to `debugging_investigator`. Return the diagnosis to the existing owner and resume the failed local step; never restart the whole workflow.
11. Use `browser_acceptance_tester` only for a named browser scenario. Require read-only Chrome interaction through Computer Use in a new tab, preservation of unrelated tabs and sessions, and reproducible evidence; never use the in-app Browser.

Stop for the user before destructive or irreversible operations, production mutation, data-loss risk, security or privacy policy changes, public-contract changes, new product choices, material external cost, or substantial scope expansion. End this skill with the reviewed, verified, committed implementation ready for a separately authorized delivery decision. Do not open a PR, merge, push, deploy, release, synchronize, or install.
