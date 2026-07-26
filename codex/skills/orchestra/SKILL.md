---
name: orchestra
description: Use only for an explicit `$orchestra` invocation or an unequivocal imperative to use or start Orchestra; align the specification, create an approved standard or critical implementation plan, coordinate implementation, independent review and verification, commit accepted phases, and hand completed commits to explicit delivery-policy routing.
---

# Orchestra

Keep the root orchestrator responsible for specification alignment, tier selection, capability routing, compact synthesis, blocker resolution, ordinary reversible in-scope decisions, the local plan, phase commits, direct PR observation, and final technical judgment. Use the root's current session configuration selected outside Orchestra; the root has no assignment in `roles.toml` and is never respawned.

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

In an execution-capable mode, reuse the preceding conversation, inspect Git
state, classify the internal checkpoint (exploration, candidate specification,
candidate plan, adopted implementation, or resumable Orchestra task), and state
concisely what Orchestra is adopting. Ask only genuine gaps while obtaining a
minimum brief with objective,
visible result, approximate repository area, known critical risks, and bounded
factual open questions. If `$orchestra` is invoked without an objective, ask for
it before creating resources. If the user explicitly limits the request to
brainstorming, remain read-only until the user authorizes formal task setup. Do
not persist the brief. A plan created before activation remains a candidate plan
until Orchestra validates it against repository evidence.

## Classify initially and revalidate after context

Declare `Tier: standard|critical — <matching condition>: <one-line evidence>`
from the minimum brief before creating the formal task resources. This is the
initial tier used for the first repository-context assignment. After focused
repository evidence and final specification confirmation, revalidate the tier.
If the cited condition is disproven or a critical risk is discovered,
reclassify before any later dispatch and request only the context delta tied to
that risk.

Destructive means irreversible loss of unique data or work. An operation whose reversibility is proven by a cheap preflight (for example `git branch --contains` showing the commits exist in the base, or state that is regenerable) is not destructive and does not force critical.

Use `standard` for ordinary planned features and fixes. Select `critical` for security-sensitive work, credentials, payments, migrations, destructive actions, production changes, or comparable high-impact risk.

Tier exemplars: standard covers ordinary planned features and fixes; critical covers schema migrations, auth/payment/credential changes, unrecoverable deletion, and production mutation.

## Isolate every new formal task

After initial tiering and before any capability dispatch, resolve the intended base
worktree, base branch, and committed base revision without inheriting the
current task's branch. Use Git directly to choose the first available
`orchestra/<task-slug>[-N]` branch and sibling worktree path, then create a new
dedicated worktree with `git worktree add`. Never adopt the current worktree for a new task, even when it is clean or already linked. Never switch, clean,
stash, commit, or otherwise mutate the source checkout for a new task.

Fresh work starts at the captured base revision. Prior committed work creates
the task branch and sibling worktree at the adopted source HEAD while recording
the intended integration base. Scoped dirty paths import through
`adopt_worktree.py`; imported changes may remain unstaged. Preserve existing
commits without rewriting. If dirty-path ownership is ambiguous, pause for
exact path selection rather than inferring hunk splits.

Verify that task and base paths and branches differ. Pass that exact worktree,
branch, base, adopted revision when applicable, and revision identity to every
capability packet and run every planning, implementation, verification, review,
plan, and commit operation there. Formal planning remains read-only against the
source checkout. Block instead of falling back to the current checkout.

Reuse is limited to the same live pre-approval task or to a resumed task whose
approved local plan, objective, task branch, base, and worktree all match Git.
If planning is rejected, canceled, or abandoned before approval, remove only a
clean worktree whose branch still equals the captured base or adopted revision
and has no unique work; otherwise preserve and report the resources. No plan is
persisted before approval. If adopted committed work later passes unchanged,
allow completion without an artificial commit.

## Resolve assignments and references

Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root. Read `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml` as the only machine-readable assignment matrix. Resolve exactly `tiers.<tier>.<capability>` and require that entry to contain only `profile`, `model`, and `reasoning_effort`. Load `${CODEX_HOME:-$HOME/.codex}/agents/<profile>.toml`, pass the capability in the packet, and use the assignment's explicit model and reasoning overrides when spawning. A profile never selects its capability or assignment.

Always attempt the installed assignment first. Only when a
`repository_context` spawn is rejected before execution because the internal
subagent runtime does not support the assigned model, retry that same `analyst`
packet internally with Luna and reasoning `high`. Record the
substitution only in root memory for the live task. Do not create a visible
Codex task, persist fallback state, edit the source or installed matrix, or use
this fallback for another capability. If any other capability's assigned model
is unsupported, return `blocked`.

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

Standard and critical may use all ten capabilities. Do not dispatch a capability absent from the selected tier and never create root, commit, polling, PR-triage, or delivery assignments.

## Keep compact context

Keep one compact in-memory packet with: explicit capability; objective; known decisions and context delta; allowed paths or interactions; acceptance; verification; exclusions; stop conditions; relevant references and revision identity. When applicable, include `browser_route: auto | in_app | chrome`, test elevation requirements, and ownership of exact temporary processes or task tabs. Reuse still-valid evidence and send only changed context deltas after the first pass. Keep agent and resource handles only in root memory. Do not persist packets, agent transitions, resource registries, previous clean PR heads, authority bundles, or workflow logs.

Request outcome-first, lossless structured returns: omit packet and routine process replay, preserve material evidence appropriate to the capability, and never impose a token, line, file, finding, test, or explanation cap.

## Maintain the local task plan

Before approval, keep the formal-plan draft in conversation or system temporary storage. After approval, the root resolves `git rev-parse --git-path orchestra/plan.md` in the task worktree and writes the exact approved plan directly as `active`. Record objective, tier, branch, base revision, decisions, phase contracts, verification, current phase, blocker, next action, and uncommitted-work note. When adoption applies, also record the adopted source revision, imported paths, existing commit range, and remaining phases.

Use only these statuses:

- `active`: explicit user approval received and approved execution is underway;
- `blocked`: stopped at a named blocker with the next action recorded;
- `completed`: all phases reviewed, verified, and committed; delivery authority remains separate.

Only the root writes the plan. On resume, resolve the Git path again and reconcile the plan with current status, branch, HEAD, merge base, relevant commits, and user authority. Git is authoritative for code and history; the plan carries approved intent and progress only. A missing or unreadable plan blocks automatic continuation until the root reconstructs it and realigns with the user. Remove it only with safe task-worktree cleanup. Do not add a plan CLI, global index, Kanban board, event log, or state engine.

## Route standard and critical work

1. Complete the mandatory new-task worktree isolation gate from the minimum brief, then dispatch `repository_context` to an `analyst` with bounded factual questions from that exact worktree. The root may skip or reduce this dispatch only when it cites the specific prior evidence it reuses (artifact and HEAD, same session); otherwise dispatch. Consume the one-shot result and close that agent and its descendants before continuing.
2. Continue the specification dialogue using the repository evidence. Dispatch additional `repository_context` only for a newly material factual question, request only the targeted context delta, and close each one-shot analyst and its descendants after consuming its result. Add `web_research` only for necessary time-sensitive external evidence. Then present and confirm the complete specification containing Objective, User-visible behavior, Constraints, Acceptance, Exclusions, Decisions, and Open questions. Revalidate the tier; if it changes, use the new tier for every later assignment and request only the context delta related to the newly discovered risk.
3. Final specification confirmation is the checkpoint to draft the plan in conversation or system temporary storage; do not require a second literal request to make a plan. Dispatch `technical_planning` (or `architecture_analysis` for a bounded named architecture question) when useful; for a small single-phase standard task the root may write the compact plan directly. A single-phase standard plan is explicitly compact: objective, one phase contract, verification, nothing else.
4. For a critical plan audit, dispatch `independent_review` only when the packet names a measurable risk, supporting evidence, affected area, and an independently detectable defect class. Complexity alone is insufficient. Consume the one-shot audit result and close that reviewer and its descendants.
5. Have the root review and summarize the plan and request explicit user approval. Stop before implementation. Specification confirmation authorizes plan drafting, not implementation. On approval, write the exact approved plan directly as `active`.
6. For each approved phase, select exactly one implementation capability and owner. Use `general_implementation` normally or `frontend_implementation` for a primarily frontend phase; never dispatch both as parallel owners of the same phase. Keep this implementation agent open and send accepted fixes back to it throughout the phase.
7. Dispatch `runtime_verification` for applicable checks and `browser_acceptance` only for a named browser scenario. Create at most one verifier per used verification capability and reuse that verifier for affected reruns. If verification returns `failed`, return findings to the same implementation owner and re-verify before dispatching `independent_review`. If it returns `blocked`, the root decides whether review proceeds on source alone and, when it does, records the blocked reason in the review evidence. Then dispatch one `independent_review` agent against the exact revision and evidence and keep it open for meaningful delta review.
8. For a second critical review, reuse `independent_review` with the critical assignment only for a named measurable risk and independently detectable defect class.
9. Return accepted findings to the same implementation owner, preserve its original implementation capability and playbook, rerun affected verification with the same capability verifier, and send the meaningful delta to the same phase reviewer.
10. After final evidence is consumed, ask each phase resource owner to stop only its exact owned temporary processes and close only its task tabs. Stop root-owned shared test processes. Consume the cleanup results, then call `close_agent` on the implementation owner, reviewer, and every verifier so their descendants close as well. A known live agent or owned process with worktree write access blocks commit; an unclosed source-read-only task tab is partial cleanup and does not invalidate accepted evidence. Never scan for or kill unrelated processes or close unrelated browser state.
11. Have the root commit the accepted phase through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), then update phase progress in the local plan. Phase teardown is complete before this commit skill starts and never becomes part of its Git path.
12. When either the same local failure repeats (its second occurrence) or two fix-review rounds with distinct legitimate findings fail to converge, stop blind retries and choose: reassess the phase approach, dispatch `difficult_debugging` with only the failure evidence and context delta when the pattern suggests a deeper cause, or ask the user when an authority boundary is crossed. Consume a debugging result, close that one-shot agent and its descendants, return the diagnosis to the same implementation owner, and resume the failed local step, not the whole workflow.
13. After every phase is reviewed, verified, torn down, and committed, set the local plan to `completed`.

Frontend visual iteration and browser acceptance use `browser_route: auto | in_app | chrome`. Explicit user selection, whether relayed by the root or supplied in the agent conversation, remains fixed unless fallback is also authorized. `auto` explicitly selects Codex's in-app Browser first and may use Computer Use with Chrome only for a technical availability or capability gap. A functional failure, application timeout, or selector problem never triggers fallback. On an allowed fallback, close the in-app task tab and repeat the complete scenario in a separate Chrome task tab. Frontend and independent acceptance tabs and evidence remain separate; browser acceptance is an independent verifier dispatch. The frontend owner never accepts its own work.

Tests run sandboxed unless the packet declares a concrete elevated need. Before broader verification or diagnosis of any failed test, rerun the exact command, arguments, and working directory once with elevated permission. Record a sandbox dependency when the elevated retry passes, treat a repeated failure as trustworthy evidence, and return `blocked` when elevation is unavailable or unsafe.

## Root-owned mechanical operations

Phase commit and phase teardown are not profiles or capabilities. After review and verification pass, the root performs teardown with the runtime's existing agent-close primitive and exact resource handles, then uses direct Git by default through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) and may invoke `commit_phase.py` when exact-path staging is useful. An isolated teardown or mechanical Git failure stays root-local. PR observation is also direct: the root invokes `pr.py observe` through [orchestra-pr-review](../orchestra-pr-review/SKILL.md), then reuses `independent_review` when PR feedback needs code-review judgment. Accepted PR fixes return to the same implementation owner.

Stop for the user before destructive or irreversible operations, production mutation, data-loss risk, security or privacy policy changes, public-contract changes, new product choices, material external cost, or substantial scope expansion. After all phase commits are complete, route only through [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md). Do not infer delivery policy, merge without separate authority, deploy, release, synchronize, or install.
