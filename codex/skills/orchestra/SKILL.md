---
name: orchestra
description: Route software changes through Orchestra's proportional light, standard, or critical workflow. Use when the root must classify implementation risk, gather bounded repository or current external evidence, create and align a formal plan, require user approval before planned implementation, coordinate reviewed phase commits, diagnose repeated local failures, run Chrome acceptance through Computer Use, and hand completed commits to explicit delivery-policy routing.
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

Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root. Read `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml` as the only machine-readable model and reasoning matrix for spawned specialists. Resolve `tiers.<tier>.<role>` and pass its `model` and `reasoning_effort` as explicit overrides for every spawned role:

- use the `${CODEX_HOME:-$HOME/.codex}/agents/repo_context_explorer.toml` profile for `repo_context_explorer`;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/planner.toml` profile for `planner`;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/plan_scope_auditor.toml` profile for `plan_scope_auditor` only with a complete risk-based audit packet;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/implementation_worker.toml` profile for `implementation_worker`;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/frontend_implementation_worker.toml` profile for `frontend_implementation_worker` as the exclusive owner of a primarily frontend standard or critical phase;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/reviewer.toml` profile for `reviewer` and a justified `reviewer_second_pass`;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/debugging_investigator.toml` profile for `debugging_investigator` after the same failure repeats;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/web_researcher.toml` profile for narrow, current `web_researcher` evidence;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/browser_acceptance_tester.toml` profile for `browser_acceptance_tester` scenarios;
- use the `${CODEX_HOME:-$HOME/.codex}/agents/phase_committer.toml` profile for `phase_committer`.

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
7. Select exactly one implementation owner for each approved phase. Use `frontend_implementation_worker` instead of `implementation_worker` when the phase is primarily frontend; never dispatch them together or as parallel collaborators. Split mixed work into frontend and non-frontend phases with one owner each. Keep the frontend owner within the approved brief, scope, and design system; require reuse of existing patterns and components plus responsive, accessibility, and interaction-state coverage. Run targeted verification, then send the revision and relevant evidence to one independent `reviewer` that reports without editing.
8. For critical work, add `reviewer_second_pass` only when the packet names a measurable risk, supporting evidence and affected area, and the independent defect class a second reviewer could detect. Reuse `reviewer.toml` and review only the relevant delta.
9. Return accepted findings to the same implementation owner, re-run affected verification, and commit an accepted phase through `phase_committer`.
10. When the same local failure repeats, stop retrying and send only that failure evidence and context delta to `debugging_investigator`. Return the diagnosis to the existing owner and resume the failed local step; never restart the whole workflow.
11. Use `browser_acceptance_tester` only for a named browser scenario. Require Computer Use with Chrome as its exclusive browser path, read-only interaction in a new tab, preservation of unrelated tabs and sessions, and reproducible evidence. It must never invoke, probe, or fall back to the in-app Browser and must return blocked when Computer Use or Chrome is unavailable. The root may use the in-app Browser separately.

Stop for the user before destructive or irreversible operations, production mutation, data-loss risk, security or privacy policy changes, public-contract changes, new product choices, material external cost, or substantial scope expansion. After all reviewed, verified phase commits are complete, route the delivery decision only through [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md). Do not choose a lane before that point, infer policy, merge without separate authority, deploy, release, synchronize, or install.
