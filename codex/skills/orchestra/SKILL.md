---
name: orchestra
description: Use only for an explicit `$orchestra` invocation or an unequivocal imperative to use or start Orchestra; route the task through the canonical workflow, approved plan, independent review, verification, commit, and authorized delivery.
---

# Orchestra

Read [runtime resources](runtime.md) before resolving workflow files or helpers.

The root orchestrator owns specification alignment, tier recommendation,
capability routing, the approved local plan, blocker resolution, phase commits,
delivery observation, and final technical judgment. The user chooses the tier
and remains the product and authority owner. Role skills and internal
playbooks carry delegated behavior; this skill only routes the work.

`docs/WORKFLOW.md` (installed as
`${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/WORKFLOW.md`) is the canonical policy.
Do not load the whole document by default. Read only the sections needed for
the current checkpoint:

| Need | Read these WORKFLOW sections |
| --- | --- |
| Activation and user authority | `Orchestrator behavior`, `Host adapters`, `Autonomy within an approved objective` |
| Host, tier, and assignment | `Tier flows and models`, `Installed matrices are the assignment truth`, and the selected host adapter |
| Direct tools, CLI executor, or execution preset | `Standalone tools`, `CLI delegation`, `Delegated execution presets`, and [orchestra-delegate](../orchestra-delegate/SKILL.md) |
| Context, specification, and plan | `Context and planning`, `Local task plan`, and the named analysis playbook |
| Phase work and preview | `Phase execution`, `User preview`, `Material context discovery and promotion` |
| Waiting and teardown | `Agent waiting`, `Phase teardown`, `Test permissions and browser routing` |
| Review and commit | `Review policy`, `Commit path`, and [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) |
| Delivery | `Delivery policy`, `PR path`, `Local integration path`, and [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md) |
| Completion and handoff | `Durable knowledge checkpoint`, `User-facing progress and handoff` |

Use `${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/scripts/<name>.py` with the
selected runtime; see runtime resources for direct-sync compatibility paths.

## Activation and host routing

Activate only for an explicit `$orchestra` invocation, adoption of a ready
`$orchestra-task` card from the current native host chat, or an unequivocal
instruction to use or start Orchestra. Ordinary plans, descriptions, task
capture, and direct implementation remain outside this route. In a
planning-only host, read `Orchestrator behavior`, pause before task setup, and
continue in the same conversation once the host becomes execution-capable.

Identify the execution host from its available adapter and use its native
spawn protocol. Explicit CLI delegation follows its separate executor contract.
Codex uses [host_codex](references/host_codex.md),
`spawn_agent`, and `wait_agent`; Cursor uses its Task adapter; Grok Build uses
its `spawn_subagent` adapter; Devin uses its `run_subagent` adapter. Resolve
the selected host's matrix through that adapter. Each host reads its native
matrix directly. When the user selects an
execution preset, resolve capability overrides through
[orchestra-delegate](../orchestra-delegate/SKILL.md) before native assignment
lookup. Apply WORKFLOW "Tier flows and models" before resuming a task from the
retired external integration.

Before resources exist, read `Tier flows and models`, recommend one assigned
tier with concise risk and cost evidence, and obtain the user's choice. The
matrix supplies native defaults and the explicitly selected preset supplies
its overrides; a cheaper tier never waives authority, review, verification, or delivery gates.

## Capability router

Compose one behavior-only profile with one capability. Load
[shared conduct](references/shared_conduct.md) and the role skill when first
needed; reuse them for later dispatches unless changed. The packet carries the explicit capability, authority, worktree,
revision, exact artifact IDs, new context, accepted finding IDs, and stop
conditions; it does not replay the workflow.

| Capability | Profile | Read |
| --- | --- | --- |
| `repository_context` | `orchestra_analyst` | [repository context](references/repository_context.md) |
| `web_research` | `orchestra_analyst` | [web research](references/web_research.md) |
| `technical_planning` | `orchestra_analyst` | [technical planning](references/technical_planning.md) and applicable [shared engineering guidance](references/architecture_guidance.md) |
| `architecture_analysis` | `orchestra_analyst` | review frame in [shared engineering guidance](references/architecture_guidance.md) |
| `difficult_debugging` | `orchestra_analyst` | [difficult debugging](references/difficult_debugging.md) |
| `general_implementation` | `orchestra_implementation_worker` | role skill and applicable shared engineering guidance |
| `frontend_implementation` | `orchestra_implementation_worker` | [frontend implementation](references/frontend_implementation.md) |
| `independent_review` | `orchestra_reviewer` | role skill and applicable [shared engineering guidance](references/architecture_guidance.md) |
| `browser_acceptance` | `orchestra_verifier` | [browser acceptance](references/browser_acceptance.md) |
| `runtime_verification` | `orchestra_verifier` | [runtime verification](references/runtime_verification.md) |

The seven playbooks are `repository_context`, `web_research`,
`technical_planning`, `difficult_debugging`, `frontend_implementation`,
`browser_acceptance`, and `runtime_verification`. General implementation,
independent review, and architecture analysis use base-role behavior or the
shared engineering reference; they do not gain new playbooks or personas.
Roles and playbooks link the relevant sections, including verification recipes.
WORKFLOW "Engineering guidance and evidence" owns applicability and evidence
placement; a reference does not add dispatches or gates.

## Route the task

Follow the named WORKFLOW sections rather than reproducing their rules here:

1. Read `Orchestrator behavior` and `Autonomy within an approved objective`,
   then collect the minimum brief and confirm the activation checkpoint.
2. Read `Tier flows and models` and `Installed matrices are the assignment
   truth`; inspect the selected host adapter, recommend a tier, and obtain the
   user's explicit choice.
3. Read `Context and planning`; perform the read-only preflight, resolve the
   checkout, run `task_state.py init`, and register `coordination.py` when
   applicable. Confirm the specification and candidate plan according to its
   phase rule, then obtain plan approval.
4. For each phase, read `Phase execution`, `Review policy`, and
   `Material context discovery and promotion`. Check ownership follows
   the selected execution preset, or the implementation owner by default.
   Every accepted phase requires a
   fresh independent code review; a verifier is added only for the phase's
   named independent gate. Accepted findings return to the same logical owner.
5. Read `User preview` when the phase declares it. The current owning chat may
   show and iterate the approved scope with a task-owned local preview process;
   the owner and exact approved artifacts are preserved, and cleanup occurs on
   final or cancelled work. Freeze the preview before dispatching final
   verification and review.
6. Read `Phase teardown`, `Durable knowledge checkpoint`, and `Commit path`.
   Run the durable knowledge judgment before final-phase teardown so the live
   owners can complete any authorized correction; retire resources only after
   review and required checks, then commit the accepted phase.
7. Read `Delivery policy`, `Local integration path`, or `PR path`. Both local
   and PR delivery require fresh configured checks and independent code review
   before the delivery mutation or clean result. Use
   [orchestra-pr-review](../orchestra-pr-review/SKILL.md) for PR observation;
   it resolves assignments through the selected host adapter.

When an owner or reviewer is closed, preserve the logical assignment and the
exact approved artifact IDs. Resume the same agent when it is available. Spawn
a replacement only after the prior agent is confirmed unavailable or the
selected preset authorizes an evidence-backed recovery transition; a replaced
reviewer is always a fresh independent reviewer. Read the host-specific
recovery rules in `Phase execution` and `PR path`.

Stop only at the hard gates in `Autonomy within an approved objective` or a
named WORKFLOW authority boundary. Never use standalone legacy helpers as
Orchestra dependencies: `commitbot`, `prbot`, `openprbot`, and `prmerge` are
separate legacy tools. Never merge, release, deploy, install, or mutate
production without the corresponding explicit authority.
