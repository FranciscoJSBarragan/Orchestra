---
name: orchestra
description: Use only for an explicit `$orchestra` invocation or an unequivocal imperative to use or start Orchestra; align the specification, create an approved implementation plan using a tier available in the selected mode, coordinate implementation, independent review and verification, commit accepted phases, and hand completed commits to explicit delivery-policy routing.
---

# Orchestra

The root orchestrator owns specification alignment, tier recommendation,
capability routing, compact synthesis, blocker resolution, ordinary reversible
in-scope decisions, the local plan, phase commits, direct PR observation, and
final technical judgment. The user chooses the active tier and remains the
final authority after a concise recommendation. The root has no assignment in
the host matrix and is never respawned.

`WORKFLOW.md` is the single canonical home for workflow policy. Read it from
`${ORCHESTRA_HOME:-$HOME/.orchestra}/WORKFLOW.md` (source repository:
`docs/WORKFLOW.md`). This skill holds only activation, host resolution,
capability dispatch, and section pointers; when any behavior rule is needed,
open the named WORKFLOW section instead of inferring it. Use
`${ORCHESTRA_HOME:-$HOME/.orchestra}` as the shared runtime home and invoke
helpers at `${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/<name>.py`, falling
back to `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/<name>.py`.

## Activate explicitly and align the specification

Orchestra activates only through an explicit `$orchestra` invocation or an
unequivocal imperative to use or start Orchestra. Ordinary requests to create a
plan, descriptive mentions of Orchestra, and direct change, fix, or
implementation work do not activate it.

If Orchestra is explicitly invoked in a planning-only host mode (any harness or
session mode intended for planning that prohibits or postpones implementation
mutations), reuse the preceding conversation, identify the latest candidate
checkpoint, and pause before formal task setup. Do not create a branch or
worktree, persist a plan, dispatch implementation, commit, or cross another
mutation boundary. Ask the user to switch to an execution-capable mode. When
the host becomes execution-capable, continue from the adopted context without
requiring another `$orchestra` invocation or recreating the analysis or plan.
Orchestra observes the host mode and never changes the host into a
planning-only mode.

In an execution-capable mode, reuse the preceding conversation, including
confirmed revision-bound `$orchestra-task` context. Inspect Git state, classify
the internal checkpoint, and state concisely what Orchestra is adopting.
Ask only genuine gaps while obtaining the minimum brief (objective, visible
result, repository area, critical risks, bounded open questions). A plan
created before activation remains a candidate plan until validated against
repository evidence. Brainstorming-only requests stay read-only until the user
authorizes task setup. An explicit instruction given after the corresponding
scope, warning, plan, or pending action satisfies that checkpoint; do not ask
for the same confirmation twice. Adoption, reclaim, and resume semantics:
WORKFLOW "Activation and specification gate".

## Resolve the installed model configuration

Before recommending a tier or creating resources, identify the host: Codex when
`spawn_agent` and `wait_agent` exist; otherwise Grok Build when `spawn_subagent`
exists; otherwise Cursor when `Task` exists. Read the matching spawn reference
and never mix protocols.

On Codex, read [host_codex](references/host_codex.md) and
`${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml`. When it contains top-level
`modes`, require exactly `native` and `external`, run
`python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/session_model.py"` once,
and require an `ok` result. Use its `modelconfig` as the immutable lookup mode
for the task and report the selected mode concisely. If the user explicitly
requested the other mode, or the helper blocks on an incompatible root model,
stop before tier selection and tell the user which model selector entry a new
task requires. Never change or respawn the root model. A top-level `tiers`
matrix is a legacy fixed configuration: preserve existing behavior without the
session helper. Record the selected mode in Decisions when `plan.md` becomes
active; a resumed dual task requires the helper to return the same mode.
Changing `native` and `external` requires a new task; a tier transition never
changes the selected model configuration.

On Cursor or Grok Build, do not run `session_model.py`. Read
`${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/cursor/roles.toml` or
`${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/grok/roles.toml` and
[hosts/cursor/references/spawn.md](../../../hosts/cursor/references/spawn.md)
or [hosts/grok/references/spawn.md](../../../hosts/grok/references/spawn.md)
(installed copies: `${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/<host>/spawn.md`).

## Recommend and transition tiers

Recommend one available tier, naming its matching condition and one line of
evidence from the minimum brief, batched with any clarifying questions and the
user-preview offer when the WORKFLOW detection rule matches, then obtain the
user's explicit tier choice. Codex native mode offers `standard` and
`critical`. Codex external mode additionally offers `luna`, recommended only
when the user explicitly prioritizes cost for ordinary bounded work; otherwise
`standard` remains the default. Cursor offers `minimal`, `standard`, and
`critical`; `minimal` is the cost/speed choice. Grok offers `standard` and `critical` and treats unassigned `minimal` as
`blocked`. Tier conditions, the destructive-action definition, preview
semantics, and the transition procedure: WORKFLOW "Tier flows and models",
"User preview", and "Tier transition". A cheaper user-selected tier never
waives the hard authority gates. Never change tier unilaterally.

## Select the task checkout and create its branch

After the tier choice, perform the read-only Git and execution-readiness
preflight. Immediately after specification confirmation, create the fresh
collision-free `orchestra/*` task branch per WORKFLOW "Task checkout and
branch" (managed worktree or opt-in hybrid, canonical-base upstream sync,
blocked dirty/diverged states, no pull/merge/rebase). Never implement on the
starting branch or `main`.

Immediately run `python3
"${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/task_state.py" init --worktree
<task-worktree>` once and keep its exact `state`, `plan`, and `artifacts`
paths in root memory. Then attempt idempotent registration with `python3
"${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/coordination.py" task create`,
passing an adopted card's exact UUID as `--task-id`. Coordination is fail-soft
observability: report a correctly authorized `invalid`/`unavailable` result
compactly and continue with full authority. Adopted-card stop, reclaim, and
`task get` cadence: WORKFLOW "Prepared task adoption and Task Control".

## Resolve assignments and references

Follow the host spawn reference selected above; it owns spawn, wait, close,
and the host matrix. A profile never selects its capability or assignment.
Role behavior is self-serve: each profile is a minimal stub that reads its
`orchestra-role-*` skill and the shared conduct reference itself at startup.
The packet carries only the assignment — capability, authority, worktree,
exact artifact identifiers, revision, stop conditions, and new context — and
names any capability playbook; it never restates role behavior.

Compose assignments as follows:

| Capability | Profile | Internal reference |
| --- | --- | --- |
| `repository_context` | `orchestra_analyst` | [repository context](references/repository_context.md) |
| `web_research` | `orchestra_analyst` | [web research](references/web_research.md) |
| `technical_planning` | `orchestra_analyst` | [technical planning](references/technical_planning.md), plus [architecture guidance](references/architecture_guidance.md) when architecture is named |
| `architecture_analysis` | `orchestra_analyst` | [architecture guidance](references/architecture_guidance.md); no playbook |
| `difficult_debugging` | `orchestra_analyst` | [difficult debugging](references/difficult_debugging.md) |
| `general_implementation` | `orchestra_implementation_worker` | none; behavior lives only in the base profile |
| `frontend_implementation` | `orchestra_implementation_worker` | [frontend implementation](references/frontend_implementation.md) |
| `independent_review` | `orchestra_reviewer` | none; behavior lives only in the base profile, plus [architecture guidance](references/architecture_guidance.md) when architecture is named |
| `browser_acceptance` | `orchestra_verifier` | [browser acceptance](references/browser_acceptance.md) |
| `runtime_verification` | `orchestra_verifier` | [runtime verification](references/runtime_verification.md) |

These seven files are the complete playbook inventory: `repository_context`,
`web_research`, `technical_planning`, `difficult_debugging`,
`frontend_implementation`, `browser_acceptance`, and `runtime_verification`.
Architecture guidance is one shared reference, not an eighth playbook. Do not
create a playbook for `general_implementation`, `independent_review`, or
`architecture_analysis`. Every defined tier uses all ten capabilities; never
create root, commit, polling, PR-triage, or delivery assignments.

## Run the planned workflow

Execute the stages below by their WORKFLOW sections; this list is a router,
not a restatement.

1. **Initial context and specification** — WORKFLOW "Context and planning".
   Answer the brief's bounded questions from the read-only preflight when the
   remaining evidence is small; dispatch `repository_context` when it is not
   (the criterion is evidence volume, not familiarity). Then confirm the
   specification: Objective, User-visible behavior, Constraints, Acceptance,
   Exclusions, Decisions, Open questions. Final specification confirmation
   authorizes plan drafting, not implementation; a single-phase non-critical
   task may combine specification and candidate plan in one message per the
   WORKFLOW rule, and checkout creation follows the confirmation immediately.
2. **Formal planning** — WORKFLOW "Context and planning" and the
   [technical planning](references/technical_planning.md) playbook. The root
   authors directly whatever fits one phase; dispatch `technical_planning`
   only for multi-phase, cross-component, or critical work. Produce
   one complete `plan-overview` plus one complete `plan-phase` per phase with
   the proportional format, then apply the conditional plan-review policy and
   adjudicate findings by stable identifier.
3. **Approval and the local plan** — present the exact accepted bundle and
   request explicit approval; stop before implementation, and
   no approved `plan.md` is persisted before approval. On approval write
   `plan.md` at the path returned by `task_state.py init` with the
   approved overview verbatim and the exact phase manifest; only `active`,
   `blocked`, and `completed` are valid statuses. Details: WORKFLOW "Local
   task plan".
4. **Phase execution** — WORKFLOW "Phase execution", "Review policy", and
   "Material context discovery". One implementation owner per phase; owner
   runs every required deterministic handoff check; conditional independent
   verification gate; one independent review with accepted findings returned
   to the same owner; user-preview pause when the phase requires it.
5. **Waiting and progress** — WORKFLOW "Agent waiting" and "User-facing
   progress" (ten-minute non-interruptive waits, `timeout_ms: 600000`; a
   normal timeout is not a user-visible transition). Browser work carries
   `browser_route` per WORKFLOW "Test permissions and browser routing";
   Orchestra observes the active permission choice and never changes it.
6. **Phase teardown and commit** — WORKFLOW "Phase teardown" (proportional:
   an edit-only phase with no declared retention or incomplete cleanup goes
   straight to commit). Retire the cohort, then commit through
   [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) and update the
   manifest. Escalate repeated non-converging failures per WORKFLOW
   ("difficult_debugging", tier change, or a user authority boundary).
7. **Completion and delivery** — after every phase is committed, set `plan.md`
   to `completed` (completion freezes approved intent) and route only through
   [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md). PR
   observation uses `pr.py observe` through
   [orchestra-pr-review](../orchestra-pr-review/SKILL.md). Never merge,
   deploy, release, or install without separate explicit authority.

Stop for the user only at the hard gates named in WORKFLOW "Autonomy within an
approved objective"; never ask the user to make a reversible technical choice,
and batch genuinely required checks into one consolidated request.
