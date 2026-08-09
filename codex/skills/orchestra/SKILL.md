---
name: orchestra
description: Use only for an explicit `$orchestra` invocation or an unequivocal imperative to use or start Orchestra; align the specification, create an approved standard or critical implementation plan, coordinate implementation, independent review and verification, commit accepted phases, and hand completed commits to explicit delivery-policy routing.
---

# Orchestra

Keep the root orchestrator responsible for specification alignment, tier recommendation, capability routing, compact synthesis, blocker resolution, ordinary reversible in-scope decisions, the local plan, phase commits, direct PR observation, and final technical judgment. The user chooses the active tier and remains the final authority after receiving a concise recommendation and any applicable warning. Use the root's current session configuration selected outside Orchestra; the root has no assignment in `roles.toml` and is never respawned.

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

An explicit instruction given after the corresponding scope, warning, plan, or
pending action was presented satisfies that checkpoint while material facts
remain unchanged. Do not ask for the same confirmation twice.

Preserve the approved objective, constraints, acceptance, and authority unless
the user explicitly changes them. Treat a proposed mechanism or causal
explanation as a hypothesis, challenge it against current source and evidence,
and choose the smallest supported approach that preserves the approved result.

## Resolve the installed model configuration

Before recommending a tier or creating resources, read
`${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml`.

When it contains top-level `modes`, require exactly `native` and `external`,
run `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/session_model.py"`
once, and require an `ok` result. Use its `modelconfig` as the immutable lookup
mode for the task and report the selected mode concisely. If the user explicitly
requested the other mode, or the helper blocks because the root model, protocol,
or reasoning effort is incompatible, stop before tier selection, worktree
creation, or capability dispatch and tell the user which model selector entry
is required for a new task. Never change or respawn the root model.

When the installed matrix contains top-level `tiers`, treat it as a legacy
fixed configuration and preserve the existing behavior without running the
session helper. Keep the selected dual mode in root memory before approval and
record it in Decisions when `plan.md` becomes active. A resumed dual task uses
the recorded mode only after the current session helper returns the same mode.
Changing `native` and `external` requires a new task; a tier transition never
changes the selected model configuration.

## Recommend and transition tiers

Recommend `Tier: standard|critical — <matching condition>: <one-line evidence>`
from the minimum brief before creating formal task resources. When the brief
needs clarification, ask those questions and give the tier recommendation in
the same single message rather than sequential interactions. Explain the
material risk and expected scrutiny or cost in one concise summary, then obtain
the user's explicit tier choice. The user may choose `standard` after a
`critical` recommendation; that choice changes model and workflow intensity but
never waives separate authority gates for production, migrations, data,
security, payments, destructive actions, or other high-impact mutations. After
focused repository evidence and final specification confirmation, recommend any
justified tier change and let the user choose.

Destructive means irreversible loss of unique data or work. An operation whose reversibility is proven by a cheap preflight (for example `git branch --contains` showing the commits exist in the base, or state that is regenerable) is not destructive and does not force critical.

Use `standard` for ordinary planned features and fixes. Select `critical` for security-sensitive work, credentials, payments, migrations, destructive actions, production changes, or comparable high-impact risk.

Tier exemplars: standard covers ordinary planned features and fixes; critical covers schema migrations, auth/payment/credential changes, unrecoverable deletion, and production mutation.

The active tier may change in either direction after explicit user direction.
Recommend reconsideration when a newly discovered risk materially changes the
cost-benefit, the same causal failure repeats, or correction cycles
demonstrably fail to converge. Never change tier unilaterally.

## Select the task checkout and create its branch

After the user chooses the initial tier and before resource creation or any
capability dispatch, resolve the intended base branch and revision and perform a
short read-only Git preflight. Read repository delivery policy and identify the
canonical runtime, dependency setup, services, permissions, credential
categories without reading secrets, verification commands, test-data
provenance, and generated paths relevant to the task.

Read `${CODEX_HOME:-$HOME/.codex}/orchestra/checkout-mode`; accept only
`managed` or `hybrid`, default a missing legacy value to `managed`, and let an
explicit task instruction override it for that task. Record the effective mode
in the approved plan.

Managed mode preserves the isolated flow: resolve the worktree root from
`ORCHESTRA_WORKTREE_ROOT`, the installed
`${CODEX_HOME:-$HOME/.codex}/orchestra/worktree-root` file, or
`$HOME/.orchestra/worktrees`; prove the repository directory writable; choose
the first matching `orchestra/<task-slug>[-N]` branch/path pair; and run direct
`git worktree add` against the captured full base revision.

Hybrid mode uses the current primary checkout or linked worktree. Require a
named starting branch, exact committed HEAD, no staged, unstaged, or untracked
changes, no Git operation in progress, and no conflicting Orchestra plan.
Prove that checkout writable, capture its path, starting branch and revision,
then create the first matching `orchestra/*` branch there with direct
`git switch -c <branch> <captured-head>`. A clean `main` needs no extra prompt
because no work starts until the new branch exists. Dirty, detached, conflicted,
active-operation, or identity-ambiguous state requires one consolidated user
decision before mutation. Never implement on the starting branch or directly
on `main`. A PR-required task also proves the selected base is remotely usable
before branch creation.

If branch or worktree creation fails, inspect the exact identity and Git error
once and block before capability dispatch. Selected dirty paths import only
through `adopt_worktree.py` in managed mode unless the user explicitly
authorizes carrying exact paths in hybrid mode.

Keep checkout mode and path, starting branch and HEAD, task branch, resource
ownership, base branch and revision, and authorized preexisting changes in root
memory. Use that exact task checkout for
every capability, planning, implementation, verification, review, plan, and
commit operation. Immediately attempt an idempotent task registration with
`python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/coordination.py" task
create`. Treat `invalid` or `unavailable` as lost observability: report it
only after a correctly authorized attempt. When the coordination database is
outside the active workspace, make that first attempt with one exact, narrow
Guardian escalation; do not first run the known-protected operation
unprivileged. Report lost observability compactly and continue with inline
packets without retry, reduced authority, or a workflow blocker.

Reuse is limited to the same live preapproval task or to a resumed task whose
approved plan, objective, checkout mode/path, starting identity, task branch,
base, and HEAD all match Git.
A legacy plan with a retired environment field blocks automatic resume unless
the root explicitly verifies that it already identifies the exact Orchestra
task worktree and the user authorizes adoption. Do not migrate an active
checkout from an older sibling location into the configured root. On preapproval
abandonment, never discard unique work; remove only proven-clean resources
created for the live task. A draft may exist only as a clearly labeled private
artifact; no approved `plan.md` is persisted before approval. If adopted
committed work later passes unchanged, allow completion without an artificial
commit.

## Resolve assignments and references

Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root and
`${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml` as the only
machine-readable assignment matrix. For a dual matrix resolve exactly
`modes.<modelconfig>.tiers.<tier>.<capability>` using the immutable mode
selected above. For a legacy matrix resolve exactly
`tiers.<tier>.<capability>`. Require every selected entry to contain only
`profile`, `model`, and `reasoning_effort`. Load
`${CODEX_HOME:-$HOME/.codex}/agents/<profile>.toml`, pass the capability in the
packet, and use the assignment's explicit model and reasoning overrides when
spawning. A profile never selects its capability or assignment.

Role behavior is self-serve: each profile is a minimal stub that reads its
`orchestra-role-*` skill and the shared conduct reference itself at startup.
The packet carries only the assignment — capability, authority, worktree,
exact artifact identifiers, revision, stop conditions, and new context — and
names any capability playbook; it never restates role behavior.

Always attempt the installed assignment first. Only when a
`repository_context` spawn is rejected before execution because the internal
subagent runtime does not support the assigned model, retry that same
`orchestra_analyst` packet internally with Luna and reasoning `high` only for a
legacy matrix or the dual `external` mode. The dual external retry uses the
installed Orchestra V1 Luna alias; legacy mode uses its existing Luna entry.
The dual `native` mode blocks instead of crossing protocol versions. Record the
substitution only in root memory for the live task when it is permitted. Do not
create a visible Codex task, persist fallback state, edit the source or
installed matrix, or use this fallback for another capability. If any other
capability's assigned model is unsupported, return `blocked`.

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

These seven files are the complete playbook inventory: `repository_context`, `web_research`, `technical_planning`, `difficult_debugging`, `frontend_implementation`, `browser_acceptance`, and `runtime_verification`. Architecture guidance is one shared reference, not an eighth playbook. Do not create a playbook for `general_implementation`, `independent_review`, or `architecture_analysis`.

Standard and critical may use all ten capabilities. Do not dispatch a capability absent from the selected tier and never create root, commit, polling, PR-triage, or delivery assignments.

## Keep compact context

Keep one compact in-memory packet with: task identifier when coordination is
available; explicit capability and authority; worktree; exact target artifact
identifiers and their roles; revision identity; accepted finding identifiers;
material context-discovery identifiers and their dispositions when present;
new context delta; and stop conditions. Initial repository context may also
carry its minimum objective and focused factual questions because no context
artifact exists yet. Do not replay objective, scope, acceptance, verification,
plan details, findings, or evidence already present in a named artifact. When
applicable, include `browser_route: auto | in_app | chrome`, runtime-only test
data or elevation facts not represented in the approved phase, ownership of
exact generated paths, temporary processes, or task tabs, and explicit
phase-reuse authorization for any resource allowed to survive a handoff. Reuse still-valid
evidence and send only changed context deltas after the first pass. Do not fork
full conversation history unless a demonstrated context dependency requires
it. Keep agent and resource handles only in root memory. The coordination store
may retain task snapshots and material start/final/blocker activities, but
never packets, resource handles, previous clean PR heads, authority bundles,
or workflow logs.

Consume `cleanup` and `retained_resources` with every stable handoff. A
`cleanup: pass` result with no retained resources causes no follow-up. An
authorized retained resource remains in root memory until phase teardown. A
`partial` result is non-blocking only for a source-read-only task tab or window
and is retried once at phase teardown. A `blocked` cleanup prevents downstream
dispatch and receives one cleanup-only follow-up to the same owner; if that
follow-up does not clear the blocker, block the phase instead of retry-looping
or taking over an ambiguously owned resource.

For every coordination write, keep machine-facing `tier`, `stage`, `status`,
activity `capability`, and activity `state` labels in English. Write
user-visible task `summary`, `blocker`, `next_action`, and activity `summary`
in the user-facing language selected by applicable instructions; when no
language is configured, use the language of the user's conversation. Preserve
literal errors, commands, paths, and identifiers verbatim inside localized
prose. Keep `plan.md`, semantic artifacts, code, and technical logs in English;
do not add or infer a persisted locale.

Use `coordination.py activity set` only for material start, final, or blocker
updates; there are no heartbeats. Request outcome-first, lossless structured returns
and never impose a token, line, file, finding, test, or explanation cap.
Every agent-produced semantic handoff is a complete revision-identified
Markdown artifact written directly to the task-private directory resolved by
`git rev-parse --git-path orchestra/artifacts`, named
`<NN>-<kind>[-p<phase>].md` with a zero-padded creation ordinal; the file name
is the artifact identifier. If that Git-private path is outside the active
workspace, use one exact, narrow Guardian escalation on the first write attempt;
do not probe it with an unprivileged write first. Use the conventional kinds
`repository-context`,
`context-delta`, `plan-overview`, `plan-phase`, `plan-review`,
`implementation-report`, `verification-report`, `implementation-review`,
`debugging-report`, and `pr-review` only when PR analysis has a downstream
semantic consumer. Do not create artifacts for start, final, commit, push,
check, or merge facts already represented by snapshots, Git, or GitHub.
Corrected overview or phase documents are immutable full replacements, never
patches that force a consumer to reconstruct the current plan. The current
bundle is selected only by exact identifiers in the packet or approved
manifest, never by timestamp or list order.

When available, an agent returns status, produced artifact identifiers,
revision, blockers, material risks, and decisions requested without replay. If
publication or lookup is `invalid` or `unavailable`, return the complete report
inline, use an exact private path already carried by the approved manifest, or
inspect current source as appropriate. Coordination failure never blocks a tier
change, implementation, verification, review, commit, or delivery.

Every role may include a conditional `Context discoveries` section in the
semantic report it already produces. Entries use report-local stable IDs such
as `CTX-001` and return composite references such as
`<artifact-identifier>#CTX-001`; they carry evidence and locator, inspected
revision, evidence classification, material impact, and a named downstream
consumer when known. If publication is unavailable, return the complete inline
report with its report-local ID and keep both together in every dependent
packet. Omit the section and return field when there is no new material context.
A discovery is neither a new artifact kind nor authority, and no agent edits an
earlier artifact or claims that the candidate is canonical. Only
`repository_context` may publish a `context-delta`; every other capability keeps
a discovery inside its existing report kind.

At a stable handoff, never while an implementation owner is actively mutating
the worktree, give each returned material discovery one explicit disposition:
`route` its exact report and composite ID to a named current-task consumer when
the evidence is sufficient, keeping any inline fallback and local ID together;
`validate` a consequential, uncertain, or disputed claim through one bounded
`repository_context` dispatch that publishes a targeted `context-delta`;
`replan` by creating a complete replacement for an affected phase under the
existing approval rules; `persist` through the responsible implementation owner
only when an approved phase already
authorizes the canonical versioned documentation path, using `replan` first
when that in-authority phase is missing; `defer` an out-of-scope but useful
follow-up; or `discard` a duplicate, immaterial, disproven, or unsupported
candidate. When a later phase depends on the result, capture that dependency in
its complete replacement phase. These dispositions create no registry, plan
field, coordination state, global context file, or cross-task memory. Before
phase teardown, every material discovery has a disposition; `defer` and
`discard` are valid non-blocking outcomes.

## Maintain the local task plan

Before approval, keep the formal candidate as one complete `plan-overview`
artifact and one complete `plan-phase` artifact per phase. A phase document
contains its outcome, relationship to the overview, preconditions and
dependencies, exact allowed scope, required behavior, acceptance, verification,
outputs consumed later, risks, exclusions, and stop conditions. The candidate
bundle explicitly maps overview and phase numbers to artifact identifiers; no
consumer infers the candidate from the newest artifacts.

After approval, the root resolves `git rev-parse --git-path orchestra/plan.md`
in the task worktree and writes it directly as `active`. If the resolved path
is protected, the first write uses one exact, narrow Guardian escalation rather
than an unprivileged probe. It contains
task and Git identity, active tier, user and root decisions, authorized
preexisting changes, the immutable dual model configuration when applicable,
the approved overview verbatim, and an exact phase
manifest with each artifact identifier, private path, revision, phase status,
accepted commit, blocker, and next action. It does not duplicate detailed phase
documents. The private paths permit resume when SQLite is unavailable. When
adoption applies, also record adopted source revision, imported paths, existing
commit range, and remaining phases. Hybrid plans additionally record the
starting branch/revision and checkout, branch, and private-artifact ownership.

Use only these statuses:

- `active`: explicit user approval received and approved execution is underway;
- `blocked`: stopped at a named blocker with the next action recorded;
- `completed`: all phases reviewed, verified, and committed; delivery authority remains separate.

Only the root writes the plan. A replacement phase artifact may update the
manifest without new user approval only for a reversible clarification within
the approved objective and authority; a material scope, public-contract, or
user-visible behavior change requires new approval. On resume, resolve the Git
path again and require exact agreement between the plan and Git for checkout
mode/path, starting identity, current task branch, base, HEAD, relevant commits, and user
authority, then resolve the exact artifact identifiers or recorded private
paths. Git is authoritative for code and history; the plan carries approved
intent, the exact current bundle, and progress only. A missing or unreadable
plan blocks automatic continuation until the root reconstructs it and realigns
with the user. Remove it only with guarded task-worktree cleanup. Do not turn
the coordination snapshot into an authoritative plan CLI, Kanban board, event
log, or workflow state engine.
The coordination snapshot never substitutes for `plan.md`, supplies missing
authority, or validates plan transitions.

## Route standard and critical work

Every dispatch starts from a clean context: under multi-agent V2 pass
`fork_turns: none` explicitly on every spawn; under V1 never set
`fork_context: true`. The packet and named artifacts carry the assignment.

1. Complete the mandatory read-only execution preflight and user confirmation from the minimum brief, establish the exact selected checkout, and attempt the fail-soft task registration. Then dispatch `repository_context` to an `orchestra_analyst` with bounded factual questions there. The analyst publishes each result as a revision-identified context artifact when available and otherwise returns the complete inline report. The root may skip or reduce this dispatch only when it cites the specific prior evidence it reuses (artifact and revision); otherwise dispatch. Consume the one-shot result and close that agent and its descendants before continuing.
2. Continue the specification dialogue using the repository evidence. Dispatch additional `repository_context` only for a newly material factual question, request only the targeted context delta, and close each one-shot analyst and its descendants after consuming its result. Add `web_research` only for necessary time-sensitive external evidence. Then present and confirm the complete specification containing Objective, User-visible behavior, Constraints, Acceptance, Exclusions, Decisions, and Open questions. Propose one to three observable user journeys, including the main path and any material failure behavior, in non-technical language. Recommend any justified tier change; the user chooses whether to adopt it. Request only the context delta related to the newly discovered risk.
3. Final specification confirmation is the checkpoint to draft the plan; do not require a second literal request to make a plan. Dispatch `technical_planning` unless the root is handling a genuinely trivial single-phase standard task directly. The planner reads exact context artifacts and publishes one `plan-overview` plus one `plan-phase` per phase, returning their exact candidate bundle. Keep a dispatched planner open through any plan-review corrections. For a trivial direct plan, the root still produces the same overview-plus-phase shape.
4. After the complete formal bundle exists, the root reads its overview, phase index, named risks, and any detail necessary for judgment, then decides whether independent plan review is proportionate. A trivial single-phase standard plan may skip review. A non-trivial multi-phase or cross-component plan receives one review. A critical plan receives a focused review whose packet names its measurable risk, supporting evidence, affected area, and independently detectable defect class. Complexity alone is insufficient.
5. A plan reviewer reads the exact candidate overview and every current phase artifact and publishes `plan-review` with stable finding identifiers. Return accepted identifiers and that review artifact to the same planner. The planner publishes full replacement documents only for affected members and returns a new complete bundle. Additional review covers the changed members and interactions. The root observes convergence after a second material review; before a third correction, or immediately for marginal, contradictory, or out-of-scope findings, it reads the exact bundle and reviews, accepts or rejects findings by identifier, and corrects direction. This is an intelligent checkpoint, not a persisted counter or mechanical limit. Close planner and plan reviewer after the bundle is accepted.
6. Have the root present the exact accepted bundle at the user's altitude and request explicit user approval. Stop before implementation. Specification confirmation authorizes plan drafting, not implementation. On approval, write `plan.md` as the approved overview and exact phase manifest.
7. For each approved phase, best-effort update the task stage, then select exactly one implementation capability and owner. Pass explicit edit authority, worktree, plan-manifest path, exact overview identifier, exact current phase identifier, revision, stop conditions, accepted finding identifiers, and only new context. Use `general_implementation` normally or `frontend_implementation` for a primarily frontend phase; never dispatch both as parallel owners of the same phase. Keep this implementation agent open and send accepted fixes back to it throughout the phase. The worker reads objective, scope, acceptance, verification, and dependencies from the approved artifacts, reads only prior outputs explicitly required by that phase, records material activity, and publishes a complete `implementation-report` for each stable handoff. While the implementation owner is active and has not returned an outcome or blocker, treat the implementation state as mutable: wait without reading the evolving diff, running speculative canaries against it, or sending design corrections. Continue only user dialogue, agent/resource coordination, and root-owned setup that does not inspect or exercise the evolving implementation. Intervene only for an owner-reported blocker, a material user scope change, or indispensable external evidence that invalidates the assignment.
8. At each implementation-owner handoff, consume the implementation artifact or inline fallback and perform at most one bounded check of exact Git identity, status, allowed-path scope, `git diff --check`, and the declared evidence inventory. If the root directly investigates a possible correctness defect, complete and confirm that investigation against the exact current source and diff before contacting the owner or pausing the phase cohort. Send one consolidated finding packet with evidence, impact, and acceptance; never send provisional or superseding directions.
   Dispose any returned context-discovery identifiers before routing a dependent consumer.
9. Dispatch `runtime_verification` for applicable checks and `browser_acceptance` only for a named browser scenario. Pass exact overview, phase, and implementation-report identifiers plus explicit verification authority and revision. Create at most one verifier per used capability and reuse it for affected reruns. Each verifier publishes a complete `verification-report` for its capability and evaluated revision. Once a stable revision packet is under verification, stop speculative root source review. Interrupt only when the revision changed or a confirmed finding invalidates the packet. If verification returns `failed`, return its exact report identifier and accepted finding identifiers to the same implementation owner and re-verify. If it returns `blocked`, the root decides whether review proceeds on source alone and records the reason in review evidence. Dispose any verifier context discoveries before downstream use. Dispatch `independent_review` only after every required verifier has passed or its blocker is explicitly accepted.
10. Then dispatch one `independent_review` agent with exact overview, phase, implementation, and verification artifact identifiers. Keep it open for meaningful delta review. The reviewer independently inspects source and diff, publishes a complete initial `implementation-review`, and on later passes publishes a meaningful delta that names its full-review base and prior finding dispositions. Context discoveries remain read-only report entries and receive root disposition rather than silent fixes. For a second critical review, reuse `independent_review` only for a named measurable risk and independently detectable defect class.
11. Return the review artifact and only accepted stable finding identifiers to the same implementation owner; do not restate the findings. Preserve its original capability, rerun affected verification with the same verifier, and send exact replacement reports plus the meaningful delta to the same reviewer.
12. After final evidence is consumed and every material context discovery has an explicit disposition, inspect each phase agent's latest `cleanup` and `retained_resources` declarations. Do not contact an agent that reported `cleanup: pass` with `retained_resources: none`. Send one parallel cleanup-only follow-up, with no new implementation or verification work, only to owners that reported authorized retained resources, `partial`, or `blocked`; stop root-owned shared test processes at the same boundary. Consume those cleanup results. Under V1, call `close_agent` on every phase agent after owner cleanup so descendants close as well. Under V2, where no true close operation is exposed, require every phase agent to be `completed` with no active descendant or retained resource. A known live agent or owned process with worktree write access blocks commit; an unclosed source-read-only task tab is partial cleanup and does not invalidate accepted evidence. The root may stop directly only a root-owned resource or an exact safely addressable handle reported by its owner. Never scan for or kill unrelated processes or close unrelated browser state.
13. Have the root commit the accepted phase through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), then update that phase's status and commit in the manifest. Git is the commit authority; do not create a commit artifact.
14. When the same causal failure repeats, correction cycles fail to converge, scope expands, or evidence indicates a deeper shared cause, stop blind retries and choose: reassess, recommend a tier change, dispatch `difficult_debugging`, or ask the user at an authority boundary. The debugger publishes `debugging-report`; return its exact identifier to the same owner without root-authored diagnosis replay. Distinct legitimate findings alone are not an escalation trigger.
15. After every phase is reviewed, verified, torn down, and committed, set `plan.md` to `completed` and best-effort mirror that descriptive state. Failure to update coordination never changes the commit or plan result.

Wait for live agents with `wait_agent` in non-interruptive ten-minute windows
using `timeout_ms: 600000`. The wait returns as soon as an agent reaches a final
state; `timed_out` means only that the agent is still working. After a timeout,
wait again without `send_input`, a status request, restart, or
`interrupt: true`. After 30 accumulated minutes without a final result, assess
once for concrete blocker evidence; elapsed time alone is not a failure. Interrupt only
for cancellation, a material scope change, or indispensable information that
invalidates the current assignment.

Frontend visual iteration and browser acceptance use `browser_route: auto | in_app | chrome`. Explicit user selection, whether relayed by the root or supplied in the agent conversation, must be attempted even when the scenario is a canary for a previously failing tool and remains fixed unless fallback is also authorized. A profile may report that route's technical blocker but may not veto or substitute it. `auto` explicitly selects Codex's in-app Browser first and may use Computer Use with Chrome only for a technical availability or capability gap. A functional failure, application timeout, or selector problem never triggers fallback. On an allowed fallback, close the in-app task tab and repeat the complete scenario in a separate Chrome task tab. Frontend and independent acceptance tabs and evidence remain separate; browser acceptance is an independent verifier dispatch. The frontend owner never accepts its own work.

Orchestra synchronizes Guardian (`:workspace`, `on-request`, and Auto-review)
as the default. The active permission choice for the task, host, or launcher
remains authoritative: Orchestra never changes it or blocks execution solely
because it differs. When Guardian is active, commands inside the workspace run
directly and one exact command that crosses a protected boundary requests one
narrow escalation for automatic review. With manual approvals, that escalation
may prompt the user; with Full Access, it runs without the workspace sandbox
boundary. Never retry a denial through a workaround or broaden permissions.
Deterministic syntax, type, compile, lint, import, assertion,
validation-contract, or CLI-usage failures remain real failures. A missing
external service, credential, or dependency may still return `blocked`, but
never broadens task authority.

At a user-directed tier change, wait for the current tool call to settle,
collect the exact revision and dirty diff, evidence, progress, pending work, and
any explicitly retained resources, then request cleanup only from their owners
and retire only live phase agents whose assignment changes. Do not revert,
restart, or create a transition commit.
Update the active tier and Decisions in the plan, then create replacements only
when needed with a compact continuation packet. The replacement worker owns the
remaining phase. Preserve evidence for the unchanged revision and conditions;
request only targeted context and reverification for a new risk. Mirror the new
tier best-effort; coordination failure never delays or reverses the transition.

## Root-owned mechanical operations

Phase commit and phase teardown are not profiles or capabilities. Agents clean their owned resources before each handoff; after review and verification pass, the root performs only the fallback cleanup described above, then retires the cohort with V1 `close_agent` or V2 completed-state evidence. It uses direct Git by default through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) and may invoke `commit_phase.py` when exact-path staging is useful. An isolated teardown or mechanical Git failure stays root-local. PR observation is also direct: the root invokes `pr.py observe` through [orchestra-pr-review](../orchestra-pr-review/SKILL.md), then reuses `independent_review` when PR feedback needs code-review judgment. Accepted PR fixes return to the same implementation owner.

Report only material phase transitions, findings or decisions, blockers, fresh
verification results, and authority requests. Each update states current state,
user-visible result or evidence, and next action without routine model/profile
plumbing. Progress updates are informational, never implicit permission
requests: continue plan-approved work without waiting for acknowledgment.
Follow the autonomy policy in `docs/WORKFLOW.md` ("Autonomy within an approved
objective"): never ask the user to make a reversible technical choice, and
batch genuinely required user checks into one consolidated request with
expected results. At completion, distinguish implementation-complete from
delivered and
state the result location, how to run or demonstrate it, fresh verification,
safe test data, limitations, exact delivery state, and next authority.

When explaining the work to the user, distinguish verified facts, supported
inference, and uncertainty. Use an available visualization capability only when
a complex sequence, hierarchy, comparison, or mapping becomes materially
easier to understand. Keep simple explanations in concise prose. A missing
visualization capability never blocks progress, and only the root creates
user-facing visualizations; delegated agents return evidence for the root to
synthesize.

Stop for the user before destructive or irreversible operations, production mutation, data-loss risk, security or privacy policy changes, public-contract changes, new product choices, material external cost, or substantial scope expansion. After all phase commits are complete, route only through [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md). Delivery cleanup removes only the exact clean Orchestra task worktree and safe task branches; incomplete intended cleanup is `partial`. Do not infer delivery policy, merge without separate authority, deploy, release, synchronize, or install.
