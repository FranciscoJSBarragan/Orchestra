---
name: orchestra
description: Route software changes through Orchestra's proportional light, standard, or critical workflow. Use when the root must select explicit capabilities, compose four stable profiles with internal playbooks, maintain a local plan for planned work, coordinate implementation, independent review and verification, commit accepted phases, and hand completed commits to explicit delivery-policy routing.
---

# Route an Orchestra change

Keep the root orchestrator responsible for problem framing, tier selection, user alignment, capability routing, compact synthesis, blocker resolution, ordinary reversible in-scope decisions, the local plan, phase commits, direct PR observation, and final technical judgment. Use the root's current session configuration selected outside Orchestra; the root has no assignment in `roles.toml` and is never respawned.

## Classify before dispatch

Declare `Tier: light|standard|critical — reason` before execution. Strengthen that declaration to `Tier: <tier> — <matching condition>: <one-line evidence>`: cite the exact gating condition that places the work in the selected tier with one line of supporting evidence. If the cited condition is disproven by evidence, reclassify before dispatching. Select `light` only when every condition is proven:

- one small, fully understood objective;
- localized impact following an established pattern;
- no public API, schema, CLI, persisted-format, dependency, or architecture change;
- no auth, security, privacy, payment, migration, production, deployment, destructive, or irreversible risk;
- no unresolved product decision;
- one direct targeted verification exists.

Destructive means irreversible loss of unique data or work. An operation whose reversibility is proven by a cheap preflight (for example `git branch --contains` showing the commits exist in the base, or state that is regenerable) is not destructive and does not force critical.

Fail closed to `standard` on ambiguity, unknown scope, new coupling, or risk. Select `critical` for security-sensitive work, credentials, payments, migrations, destructive actions, production changes, or comparable high-impact risk. Named browser acceptance makes a task at least standard. A frontend change may be light only when every light condition holds, including one direct targeted verification; otherwise it is standard.

Tier exemplars:

- light: typo/copy fix; deleting a fully merged worktree/branch after a containment check; bugfix covered by an existing targeted test.
- standard: multi-file feature or fix; anything needing discovery or a formal plan.
- critical: schema migration; auth/payment/credential changes; deleting unrecoverable data; production mutation.

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

Light has assignments only for `general_implementation` and `independent_review`. Light has no `frontend_implementation` assignment; a light frontend change routes through `general_implementation`. Standard and critical may use all ten capabilities. Do not dispatch a capability absent from the selected tier and never create root, commit, polling, PR-triage, or delivery assignments.

## Keep compact context

Keep one compact in-memory packet with: explicit capability; objective; known decisions and context delta; allowed paths or interactions; acceptance; verification; exclusions; stop conditions; relevant references and revision identity. Reuse still-valid evidence and send only changed context deltas after the first pass. Do not persist packets, agent transitions, previous clean PR heads, authority bundles, or workflow logs.

Request outcome-first, lossless structured returns: omit packet and routine process replay, preserve material evidence appropriate to the capability, and never impose a token, line, file, finding, test, or explanation cap.

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
2. The root itself runs the single direct targeted verification that qualified the task as light and records the observed command and exit status. Light has no `verifier` dispatch; if verification needs more than the direct targeted check, the task is not light — escalate to standard.
3. Dispatch `independent_review` to one read-only `reviewer` with the packet, diff, revision, and the root's recorded verification evidence.
4. Findings return to the same owner; the root re-runs the direct verification after fixes, the reviewer re-checks the meaningful delta, and the root commits the accepted phase through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md).

## Route standard and critical work

1. Dispatch `repository_context` to an `analyst` with focused discovery questions. The root may skip or reduce this dispatch only when it cites the specific prior evidence it reuses (artifact and HEAD, same session); otherwise dispatch. A reduced dispatch requests only the targeted context delta. Add `web_research` only for necessary time-sensitive external evidence.
2. Have the root synthesize evidence and align objective, constraints, acceptance, exclusions, and unresolved product choices with the user.
3. The root writes the plan, dispatching `technical_planning` (or `architecture_analysis` for a bounded named architecture question) when useful; for a small single-phase standard task the root may write the compact plan directly. The root records the resulting plan in the local `draft` plan. A single-phase standard plan is explicitly compact: objective, one phase contract, verification, nothing else.
4. For a critical plan audit, dispatch `independent_review` only when the packet names a measurable risk, supporting evidence, affected area, and an independently detectable defect class. Complexity alone is insufficient.
5. Have the root summarize the plan and request explicit user approval. Stop before implementation. On approval, update the plan directly from `draft` to `active`.
6. For each approved phase, select exactly one implementation capability and owner. Use `general_implementation` normally or `frontend_implementation` for a primarily frontend phase; never dispatch both as parallel owners of the same phase.
7. Dispatch `runtime_verification` for applicable checks and `browser_acceptance` only for a named browser scenario. If verification returns `failed`, return findings to the same implementation owner and re-verify before dispatching `independent_review`. If it returns `blocked`, the root decides whether review proceeds on source alone and, when it does, records the blocked reason in the review evidence. Then dispatch `independent_review` against the exact revision and evidence.
8. For a second critical review, reuse `independent_review` with the critical assignment only for a named measurable risk and independently detectable defect class.
9. Return accepted findings to the same implementation owner, preserve its original implementation capability and playbook, rerun affected verification, and review the meaningful delta.
10. Have the root commit the accepted phase through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), then update phase progress in the local plan.
11. When either the same local failure repeats (its second occurrence) or two fix-review rounds with distinct legitimate findings fail to converge, stop blind retries and choose: reassess the phase approach, dispatch `difficult_debugging` with only the failure evidence and context delta when the pattern suggests a deeper cause, or ask the user when an authority boundary is crossed. Return the diagnosis to the same owner and resume the failed local step, not the whole workflow.
12. After every phase is reviewed, verified, and committed, set the local plan to `completed`.

Frontend visual iteration and browser acceptance use Computer Use with Chrome only when their references require browser interaction. Neither path may invoke, probe, or fall back to Codex's in-app Browser. The frontend owner never accepts its own work; browser acceptance is an independent verifier dispatch and returns `blocked` if Computer Use or Chrome is unavailable.

## Root-owned mechanical operations

Phase commit is not a profile or capability. After review and verification pass, the root invokes `commit_phase.py` directly through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md). PR observation is also direct: the root invokes `pr.py observe` through [orchestra-pr-review](../orchestra-pr-review/SKILL.md), then reuses `independent_review` when PR feedback needs code-review judgment. Accepted PR fixes return to the same implementation owner.

Stop for the user before destructive or irreversible operations, production mutation, data-loss risk, security or privacy policy changes, public-contract changes, new product choices, material external cost, or substantial scope expansion. After all phase commits are complete, route only through [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md). Do not infer delivery policy, merge without separate authority, deploy, release, synchronize, or install.
