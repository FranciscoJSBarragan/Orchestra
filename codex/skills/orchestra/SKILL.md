---
name: orchestra
description: Route software changes through Orchestra's proportional light, standard, or critical workflow. Use when the root must select explicit capabilities, compose four stable profiles with internal playbooks, maintain a local plan for planned work, coordinate implementation, independent review and verification, commit accepted phases, and hand completed commits to explicit delivery-policy routing.
---

# Route an Orchestra change

Keep the root orchestrator responsible for problem framing, tier selection, user alignment, capability routing, compact synthesis, blocker resolution, ordinary reversible in-scope decisions, the local plan, phase commits, direct PR observation, and final technical judgment. Use the root's current session configuration selected outside Orchestra; the root has no assignment in `roles.toml` and is never respawned.

## Classify before dispatch

Declare `Tier: light|standard|critical — reason` before execution. Select `light` only when every condition is proven:

- one small, fully understood objective;
- localized impact following an established pattern;
- no public API, schema, CLI, persisted-format, dependency, or architecture change;
- no auth, security, privacy, payment, migration, production, deployment, destructive, or irreversible risk;
- no unresolved product decision;
- one direct targeted verification exists.

Fail closed to `standard` on ambiguity, unknown scope, new coupling, or risk. Select `critical` for security-sensitive work, credentials, payments, migrations, destructive actions, production changes, or comparable high-impact risk. Frontend implementation or named browser acceptance is at least standard.

## Resolve assignments and references

Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root. Read `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml` as the only machine-readable assignment matrix. Resolve exactly `tiers.<tier>.<capability>` and require that entry to contain only `profile`, `model`, and `reasoning_effort`. Load `${CODEX_HOME:-$HOME/.codex}/agents/<profile>.toml`, pass the capability in the packet, and use the assignment's explicit model and reasoning overrides when spawning. A profile never selects its capability or assignment.

Compose assignments as follows:

| Capability | Profile | Internal reference |
| --- | --- | --- |
| `repository_context` | `analyst` | [repository context](references/repository_context.md) |
| `web_research` | `analyst` | [web research](references/web_research.md) |
| `technical_planning` | `analyst` | [technical planning](references/technical_planning.md), plus [architecture guidance](references/architecture_guidance.md) when architecture is named |
| `architecture_analysis` | `analyst` | [architecture guidance](references/architecture_guidance.md); no playbook |
| `difficult_debugging` | `analyst` | [difficult debugging](references/difficult_debugging.md) |
| `general_implementation` | `implementation_worker` | none; behavior lives only in the base profile |
| `frontend_implementation` | `implementation_worker` | [frontend implementation](references/frontend_implementation.md) |
| `independent_review` | `reviewer` | none; behavior lives only in the base profile, plus [architecture guidance](references/architecture_guidance.md) when architecture is named |
| `browser_acceptance` | `verifier` | [browser acceptance](references/browser_acceptance.md) |
| `runtime_verification` | `verifier` | [runtime verification](references/runtime_verification.md) |

These seven files are the complete playbook inventory: `repository_context`, `web_research`, `technical_planning`, `difficult_debugging`, `frontend_implementation`, `browser_acceptance`, and `runtime_verification`. Architecture guidance is one shared reference, not an eighth playbook. Do not create a playbook for `general_implementation`, `independent_review`, or `architecture_analysis`.

Light has assignments only for `general_implementation`, `independent_review`, and `runtime_verification`. Standard and critical may use all ten capabilities. Do not dispatch a capability absent from the selected tier and never create root, commit, polling, PR-triage, or delivery assignments.

## Keep compact context

Keep one compact in-memory packet with: explicit capability; objective; known decisions and context delta; allowed paths or interactions; acceptance; verification; exclusions; stop conditions; relevant references and revision. Reuse still-valid evidence and send only changed context deltas after the first pass. Do not persist packets, agent transitions, previous clean PR heads, authority bundles, or workflow logs.

## Maintain the local task plan

For standard or critical work, the root resolves `git rev-parse --git-path orchestra/plan.md` in the task worktree and maintains exactly that one unversioned plan. Record objective, tier, branch, base revision, decisions, phase contracts, verification, current phase, blocker, next action, and uncommitted-work note.

Use only these statuses:

- `draft`: alignment incomplete; implementation not authorized;
- `active`: explicit user approval received and approved execution is underway;
- `blocked`: stopped at a named blocker with the next action recorded;
- `completed`: all phases reviewed, verified, and committed; delivery authority remains separate.

User approval moves `draft` directly to `active`; approval is not a status. Only the root writes the plan. On resume, resolve the Git path again and reconcile the plan with current status, branch, HEAD, merge base, relevant commits, and user authority. Git is authoritative for code and history; the plan carries approved intent and progress only. A missing or unreadable plan blocks automatic continuation until the root reconstructs it and realigns with the user. Remove it only with safe task-worktree cleanup. Do not add a plan CLI, global index, Kanban board, event log, or state engine.

## Route light work

1. Dispatch `general_implementation` to one `implementation_worker` with the compact approved packet.
2. Dispatch `runtime_verification` to one source-read-only `verifier` for the exact revision and read its observed evidence.
3. Dispatch `independent_review` to one read-only `reviewer` with the packet, diff, revision, and verification evidence.
4. Evaluate material findings at the root and return accepted findings to the same implementation owner.
5. Re-run affected verification and review only the meaningful delta.
6. Have the root commit the accepted phase through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md).

## Route standard and critical work

1. Dispatch `repository_context` to an `analyst` with focused discovery questions. Add `web_research` only for necessary time-sensitive external evidence.
2. Have the root synthesize evidence and align objective, constraints, acceptance, exclusions, and unresolved product choices with the user.
3. Dispatch `technical_planning` to an `analyst`; use `architecture_analysis` instead or additionally only for a bounded named architecture question. The root writes the returned plan into the local `draft` plan.
4. For a critical plan audit, dispatch `independent_review` only when the packet names a measurable risk, supporting evidence, affected area, and an independently detectable defect class. Complexity alone is insufficient.
5. Have the root summarize the plan and request explicit user approval. Stop before implementation. On approval, update the plan directly from `draft` to `active`.
6. For each approved phase, select exactly one implementation capability and owner. Use `general_implementation` normally or `frontend_implementation` for a primarily frontend phase; never dispatch both as parallel owners of the same phase.
7. Dispatch `runtime_verification` for applicable checks and `browser_acceptance` only for a named browser scenario. Then dispatch `independent_review` against the exact revision and evidence.
8. For a second critical review, reuse `independent_review` with the critical assignment only for a named measurable risk and independently detectable defect class.
9. Return accepted findings to the same implementation owner, preserve its original implementation capability and playbook, rerun affected verification, and review the meaningful delta.
10. Have the root commit the accepted phase through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), then update phase progress in the local plan.
11. After the same local failure demonstrably repeats, stop blind retries and dispatch `difficult_debugging` with only the failure evidence and context delta. Return the diagnosis to the same owner and resume the failed local step, not the whole workflow.
12. Set the local plan to `completed` only after every phase is reviewed, verified, and committed.

Frontend visual iteration and browser acceptance use Computer Use with Chrome only when their references require browser interaction. Neither path may invoke, probe, or fall back to Codex's in-app Browser. The frontend owner never accepts its own work; browser acceptance is an independent verifier dispatch and returns `blocked` if Computer Use or Chrome is unavailable.

## Root-owned mechanical operations

Phase commit is not a profile or capability. After review and verification pass, the root invokes `commit_phase.py` directly through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md). PR observation is also direct: the root invokes `pr.py observe` through [orchestra-pr-review](../orchestra-pr-review/SKILL.md), then reuses `independent_review` when PR feedback needs code-review judgment. Accepted PR fixes return to the same implementation owner.

Stop for the user before destructive or irreversible operations, production mutation, data-loss risk, security or privacy policy changes, public-contract changes, new product choices, material external cost, or substantial scope expansion. After all phase commits are complete, route only through [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md). Do not infer delivery policy, merge without separate authority, deploy, release, synchronize, or install.
