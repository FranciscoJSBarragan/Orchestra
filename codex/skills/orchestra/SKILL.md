---
name: orchestra
description: Use only for an explicit `$orchestra` invocation or an unequivocal imperative to use or start Orchestra; align the specification, create an approved implementation plan using a tier available in the selected mode, coordinate implementation, independent review and verification, commit accepted phases, and hand completed commits to explicit delivery-policy routing.
---

# Orchestra

Keep the root orchestrator responsible for specification alignment, tier recommendation, capability routing, compact synthesis, blocker resolution, ordinary reversible in-scope decisions, the local plan, phase commits, direct PR observation, and final technical judgment. The user chooses the active tier and remains the final authority after receiving a concise recommendation and any applicable warning. Identify the execution host from available tools and never mix spawn protocols. The root has no assignment in the host matrix and is never respawned.
Use `${ORCHESTRA_HOME:-$HOME/.orchestra}` as the shared runtime home. Invoke helpers at `${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/<name>.py`. If that path is missing, use `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/<name>.py`.
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
the internal checkpoint (exploration, candidate specification, candidate plan,
adopted implementation, or resumable Orchestra task), and state concisely what
Orchestra is adopting. Ask only genuine gaps while obtaining a minimum brief
with objective, visible result, approximate repository area, known critical risks, and bounded
factual open questions. If `$orchestra` is invoked without an objective, ask for
it before creating resources. If the user explicitly limits the request to
brainstorming, remain read-only until the user authorizes formal task setup. Do
not persist the brief. A plan created before activation remains a candidate plan
until Orchestra validates it against repository evidence.
An explicit instruction given after the corresponding scope, warning, plan, or
pending action was presented satisfies that checkpoint while material facts
remain unchanged. Do not ask for the same confirmation twice.
An adopted Kanban specification already satisfies final confirmation. After tier
selection and checkout creation, reuse its exact prepared-revision context and
plan. If Git changed, inspect only the delta and reconfirm only when it materially
changes the specification. After reclaim or a transferred resume, recover the
existing checkout and `plan.md`, preserve uncommitted work, skip the previous
host's wait/close contract, spawn fresh workers here, and re-recommend this host's assigned tier. Preserve the approved objective, constraints,
acceptance, and authority unless the user explicitly changes them. Treat a
proposed mechanism or causal explanation as a hypothesis; challenge it against
current evidence and choose the smallest supported approach that preserves the approved result.
## Resolve the installed model configuration
Before recommending a tier or creating resources, identify the host: Codex when
`spawn_agent` and `wait_agent` exist; Cursor when `Task` exists. Read the matching
spawn reference and never mix protocols.

On Codex, read [host_codex](references/host_codex.md) and
`${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml`.

When it contains top-level `modes`, require exactly `native` and `external`,
run `python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/session_model.py"`
once, and require an `ok` result. If that helper path is missing, use
`${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/session_model.py`. Use its `modelconfig` as the immutable lookup
mode for the task and report the selected mode concisely. If the user explicitly
requested the other mode, or the helper blocks because the root model, protocol,
or reasoning effort is incompatible, stop before tier selection, worktree
creation, or capability dispatch and tell the user which model selector entry
is required for a new task. Never change or respawn the root model.

When the installed Codex matrix contains top-level `tiers`, treat it as a legacy
fixed configuration and preserve the existing behavior without running the
session helper. Keep the selected dual mode in root memory before approval and
record it in Decisions when `plan.md` becomes active. A resumed dual task uses
the recorded mode only after the current session helper returns the same mode.
Changing `native` and `external` requires a new task; a tier transition never
changes the selected model configuration.

On Cursor, do not run `session_model.py`. Read
`${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/cursor/roles.toml` and
[hosts/cursor/references/spawn.md](../../../hosts/cursor/references/spawn.md)
(installed copy: `${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/cursor/spawn.md`).
Cursor offers `minimal`, `standard`, and `critical` with no mode split. This
cut assigns `minimal` and `standard`. Recommend `standard`; `minimal` when
cost or speed is the priority. Unassigned Cursor `critical` is `blocked`.
## Recommend and transition tiers

Recommend `Tier: <available-tier> — <matching condition>: <one-line evidence>`
from the minimum brief before creating formal task resources. Codex native mode
offers `standard` and `critical`. Codex external mode additionally offers `luna`, but
recommend it only when the user explicitly prioritizes cost for ordinary,
bounded work; otherwise `standard` remains the default. Cursor offers `minimal`,
`standard`, and `critical` with no mode split; recommend `standard`, `minimal`
when cost or speed is the priority, and treat unassigned Cursor `critical` as `blocked`. When the brief needs
clarification, ask those questions and give the tier recommendation in the same
single message rather than sequential interactions. Explain the material risk
and expected scrutiny or cost in one concise summary, then obtain the user's
explicit tier choice. Material risk calls for `standard` or `critical` where
those matrices exist. The
user may still choose `luna`, `minimal`, or `standard` after a higher recommendation; that
choice changes model and workflow intensity but never waives separate authority
gates for production, migrations, data, security, payments, destructive
actions, or other high-impact mutations. After focused repository evidence and
final specification confirmation, recommend any justified tier change and let
the user choose.

Destructive means irreversible loss of unique data or work. An operation whose reversibility is proven by a cheap preflight (for example `git branch --contains` showing the commits exist in the base, or state that is regenerable) is not destructive and does not force critical.

Use `standard` for ordinary planned features and fixes. In Codex external mode, use
`luna` only as the user's explicit cost-focused choice for ordinary, bounded
work. On Cursor, `minimal` is that cheap tier. Select `critical` for security-sensitive work, credentials, payments,
migrations, destructive actions, production changes, or comparable high-impact
risk.

Tier exemplars: Luna or Cursor minimal covers cost-prioritized bounded ordinary work;
standard covers ordinary planned features and fixes; critical covers
schema migrations, auth/payment/credential changes, unrecoverable deletion,
and production mutation.

The active tier may change among those assigned in the selected Codex mode or
Cursor host matrix after
explicit user direction.
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

For a fresh task on the repository's canonical base branch, resolve its configured upstream and fetch only its remote branch before fixing the base revision. A configured upstream whose fetch fails blocks task setup. With no remote or upstream, proceed locally only after identifying the base as not remotely verified. Preserve an explicitly selected noncanonical base at its captured commit for stacked work. Never run `git pull`, create an implicit merge, or rebase during setup.

Read `${ORCHESTRA_HOME:-$HOME/.orchestra}/checkout-mode`, falling back to `${CODEX_HOME:-$HOME/.codex}/orchestra/checkout-mode`; accept only
`managed` or `hybrid`, default a missing legacy value to `managed`, and let an
explicit task instruction override it for that task. Record the effective mode
in the approved plan.

Managed mode preserves the isolated flow: resolve the worktree root from `ORCHESTRA_WORKTREE_ROOT`, the installed `${ORCHESTRA_HOME:-$HOME/.orchestra}/worktree-root` file, `${CODEX_HOME:-$HOME/.codex}/orchestra/worktree-root`, or `$HOME/.orchestra/worktrees`; prove the repository directory writable; choose the first matching `orchestra/<task-slug>[-N]` branch/path pair; and run direct `git worktree add` against the fetched upstream's verified full commit without updating the base checkout, or the unverified local base when no upstream exists.

Hybrid mode uses the current primary checkout or linked worktree. Require a named starting branch, exact committed HEAD, clean status, no Git operation in progress, and no conflicting Orchestra plan. Prove that checkout writable. For a clean canonical base, proceed when equal to its fetched upstream, fast-forward when strictly behind with `git merge --ff-only <upstream>`, and block for one user decision when ahead or diverged. Capture its path, branch, and revision, then create `orchestra/*` with direct `git switch -c <branch> <captured-head>`. Equal or strictly behind needs no extra prompt because work starts only on the new branch. Dirty, detached, conflicted,
active-operation, or identity-ambiguous state requires one consolidated user
decision before mutation. Never implement on the starting branch or directly
on `main`. A PR-required task also proves the selected base is remotely usable
before branch creation.

If branch or worktree creation fails, inspect the exact identity and Git error
once and block before capability dispatch. Selected dirty paths import only
through `adopt_worktree.py` in managed mode unless the user explicitly
authorizes carrying exact paths in hybrid mode.

If fetching changes an adopted prepared task revision, request only a focused `repository_context` delta and reopen specification confirmation only for a material change.

Keep checkout mode and path, starting branch and HEAD, task branch, resource
ownership, base branch and revision, and authorized preexisting changes in root
memory. Use that exact task checkout for
every capability, planning, implementation, verification, review, plan, and
commit operation. Immediately run `python3
"${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/task_state.py" init --worktree
<task-worktree>` once. Keep its exact `state`, `plan`, and `artifacts` paths in
root memory and pass the artifacts path to every producing agent. This
workspace-local initialization must leave Git status unchanged and blocks
before dispatch when the reserved path is tracked, ambiguous, or unsafe. An
existing legacy result remains on its legacy paths for that task without
copying or dual-writing it. Then attempt an idempotent task registration with
`python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/coordination.py" task
create`. When adopting a prepared Kanban task, pass its exact technical UUID
as `--task-id`; otherwise let the helper allocate one. Treat `invalid` or
`unavailable` as lost observability: report it
only after a correctly authorized attempt. When the coordination database is
outside the active workspace, make that first attempt with one exact, narrow
Guardian escalation; do not first run the known-protected operation
unprivileged. Report lost observability compactly, omit the coordination task
identifier from every later agent packet, and continue without another
coordination attempt, reduced authority, or a workflow blocker.

Reuse is limited to the same live preapproval task or to a resumed task whose
approved plan, objective, checkout mode/path, starting identity, task branch,
base, and HEAD all match Git.
A legacy plan with a retired environment field blocks automatic resume unless
the root explicitly verifies that it already identifies the exact Orchestra
task worktree and the user authorizes adoption. Do not migrate an active
checkout from an older sibling location into the configured root. On preapproval
abandonment, never discard unique work; remove only proven-clean resources
created for the live task, using `task_state.py cleanup` before removing a
managed worktree or restoring a hybrid checkout. A draft may exist only as a clearly labeled private
artifact; no approved `plan.md` is persisted before approval. If adopted
committed work later passes unchanged, allow completion without an artificial
commit.
## Resolve assignments and references

Follow the host spawn reference selected above. On Codex, [host_codex](references/host_codex.md)
owns spawn, wait, close, Guardian, and the Codex matrix. On Cursor,
`${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/cursor/spawn.md` owns Task dispatch
and the Cursor matrix. A profile never selects its capability or assignment.

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

These seven files are the complete playbook inventory: `repository_context`, `web_research`, `technical_planning`, `difficult_debugging`, `frontend_implementation`, `browser_acceptance`, and `runtime_verification`. Architecture guidance is one shared reference, not an eighth playbook. Do not create a playbook for `general_implementation`, `independent_review`, or `architecture_analysis`.

Every defined tier uses all ten capabilities. Do not dispatch a capability
absent from the selected tier and never create root, commit, polling,
PR-triage, or delivery assignments.
## Keep compact context

Keep one compact in-memory packet with: task identifier when coordination is
available; explicit capability and authority; worktree; exact target artifact
identifiers and their roles; revision identity; accepted finding identifiers;
material context-discovery identifiers and their dispositions when present;
new context delta; and stop conditions. Initial repository context may also
carry its minimum objective and focused factual questions because no context
artifact exists yet. Do not replay objective, scope, acceptance, verification,
plan details, findings, or evidence already present in a named artifact. When
applicable, an implementation-review packet includes every exact
`repository-context` and `context-delta` required by the approved overview and
current phase, or each complete inline fallback with its stable label and
revision. Also include `browser_route: auto | in_app | chrome`, runtime-only test
data or elevation facts not represented in the approved phase, ownership of
exact generated paths, temporary processes, or task tabs, and explicit
phase-reuse authorization for any non-browser resource allowed to survive a
handoff. Browser task tabs are never eligible for phase reuse. Reuse still-valid
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

Write each visible `summary` as one concise localized milestone. After approval, use the manifest for `Phase X/Y`: implementation active; each numbered reviewer
evaluation; root-accepted finding count while corrections run; reviews approved;
and phase complete only after commit. Restart review numbering per phase, omit
rejected findings and routine review-to-owner returns, and distinguish
implementation complete, hold, PR open/clean/merged, and verified local
integration. Hide checkout mode unless it explains a blocker. Add no progress
ledger, locale field, or inferred state machine.
Use `coordination.py activity set` only for material start, final, or blocker
updates; there are no heartbeats. Request outcome-first, lossless structured returns
and never impose a token, line, file, finding, test, or explanation cap.
Every agent-produced semantic handoff is a complete revision-identified
Markdown artifact written directly to the exact task-private artifacts path
returned by `task_state.py init`, normally
`<task-worktree>/.orchestra/artifacts`, named
`<NN>-<kind>[-p<phase>].md` with a zero-padded creation ordinal; the file name
is the artifact identifier. New tasks never request protected-write escalation
for semantic artifacts. A resumed legacy task continues using the exact legacy
path returned by the initializer. Use the conventional kinds
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
revision, evidence classification, material impact, mandatory `Affected
judgment`, and a named current-phase or identified later-phase consumer. They
also classify the individual claim as `descriptive` current state,
`normative` intended behavior or constraint, or `uncertain`. If publication
is unavailable, return the complete inline
report with its report-local ID and keep both together in every dependent
packet. Omit incidental context without both a material judgment and named
current-task consumer. A discovery is neither a new artifact kind nor
authority, and no agent edits an earlier artifact or claims that the candidate
is canonical. Only `repository_context` may publish a `context-delta`; every
other capability keeps a discovery inside its existing report kind.

At a stable handoff, never while an implementation owner is actively mutating
the worktree, give each returned material discovery one explicit disposition:
`route` its exact report and composite ID to a named current-task consumer when
the evidence is sufficient, keeping any inline fallback and local ID together;
`validate` a claim only when at least one possible result can change
current-task acceptance, a finding disposition, replanning, or `persist` for
its named consumer, using one bounded `repository_context` dispatch;
`replan` by creating a complete replacement for an affected phase under the
existing approval rules; `persist` through the responsible implementation owner
only for a validated `descriptive` claim when an approved phase already lists
the exact versioned human-readable documentation path under `Context
maintenance paths`, using `replan` first when that in-authority phase is
missing; `defer` an out-of-scope but useful
follow-up; or `discard` a duplicate, immaterial, disproven, or unsupported
candidate. When a later phase depends on the result, capture that dependency in
its complete replacement phase. These dispositions create no registry, plan
manifest or `plan.md` state field, coordination state, global context file, or
cross-task memory. A `normative` or `uncertain` conflict never becomes a
documentation rewrite merely because current code differs; executable
configuration, databases, generated data, and operational data remain normal
implementation scope. Before
phase teardown, every material discovery has a disposition; discard without
validation any entry missing its affected judgment or named consumer.

When stale context names the exact material review judgment it makes
unreliable, do not accept or commit until it is resolved; incidental stale
information is omitted and never blocks. For an authorized descriptive
correction, return its discovery ID, `persist`, validating delta, and exact
maintenance path to the same owner. After the edit, always obtain targeted
repository-context revalidation for the changed paths and dirty revision,
rerun affected verification, and send only new or replaced evidence to the
same reviewer. This post-edit proof bypasses the earlier relevance pruning.
An unresolved named material context basis blocks phase commit.
## Maintain the local task plan

Before approval, keep the formal candidate as one complete `plan-overview`
artifact and one complete `plan-phase` artifact per phase. A phase document
contains its outcome, relationship to the overview, preconditions and
dependencies, exact allowed scope, required behavior, acceptance, verification,
outputs consumed later, risks, exclusions, and stop conditions. The candidate
bundle explicitly maps overview and phase numbers to artifact identifiers; no
consumer infers the candidate from the newest artifacts.

Every overview contains `Review context` with exact context artifact IDs and
revisions or labeled inline fallbacks, canonical source paths, and only the
material architecture, runtime, exposure, persistence, user-visible surface,
risks, invariants, and exclusions. Each fact or group states `Review use`,
naming the exact acceptance, risk, invariant, exclusion, or phase dependency it
informs; omit unused facts and cited evidence bodies. Every phase names exact
context dependencies and uses `Context maintenance paths: none` unless an
exact versioned documentation path is already a named current-task consumer.
Never use globs. These sections add no `plan.md` manifest or workflow-state field.

After approval, the root writes `active` directly to the exact `plan` path
returned by `task_state.py init`, normally
`<task-worktree>/.orchestra/plan.md`. It contains
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
user-visible behavior change requires new approval. On resume, resolve the
task-state path again and require exact agreement between the plan and Git for checkout
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

Setting `completed` freezes the approved objective, acceptance, and artifact selection. An accepted PR fix may advance the affected phase's terminal commit only when it remains within that intent and completes the same verification, review, and phase-commit path; update the manifest before push. New scope or user-visible behavior after `completed` or `hold` requires a new task and plan. Before PR or local delivery, read the terminal manifest commit and require the effective task head to match it exactly; an unexplained mismatch blocks use of the completed plan.

For an adopted `$orchestra-task`, also record the exact terminal SHA with
`task finish` from the owning native chat. A reviewed PR correction may update
it before delivery. Register delivery with `task record-delivery` only when the
authorized local-integration or PR-merge helper returns
`delivery_verified: true` and an exact `delivery_revision`; opening a PR,
holding, or an unverified post-state never satisfies a Kanban dependency.
## Route tiered work

Every dispatch starts from a clean context using the host wait and close
contract. The packet and named artifacts carry the assignment.

1. Complete the mandatory read-only execution preflight and user confirmation from the minimum brief, establish the exact selected checkout, and attempt the fail-soft task registration. Then dispatch `repository_context` to an `orchestra_analyst` with bounded factual questions there. The analyst publishes each result as a revision-identified context artifact when available and otherwise returns the complete inline report. The root may skip or reduce this dispatch only when it cites the specific prior evidence it reuses (artifact and revision); otherwise dispatch. Consume the one-shot result and close that agent and its descendants before continuing.
2. Continue the specification dialogue using the repository evidence. Dispatch additional `repository_context` only for a newly material factual question, request only the targeted context delta, and close each one-shot analyst and its descendants after consuming its result. Add `web_research` only for necessary time-sensitive external evidence. Then present and confirm the complete specification containing Objective, User-visible behavior, Constraints, Acceptance, Exclusions, Decisions, and Open questions. Propose one to three observable user journeys, including the main path and any material failure behavior, in non-technical language. Recommend any justified tier change; the user chooses whether to adopt it. Request only the context delta related to the newly discovered risk.
3. Final specification confirmation is the checkpoint to draft the plan; do not require a second literal request to make a plan. Dispatch `technical_planning` unless the root is handling a genuinely trivial single-phase `luna` or `standard` task directly. The planner reads exact context artifacts and publishes one `plan-overview` plus one `plan-phase` per phase, returning their exact candidate bundle. Keep a dispatched planner open through any plan-review corrections. For a trivial direct plan, the root still produces the same overview-plus-phase shape.
   Require `Review context` in the overview and exact context dependencies plus
   `Context maintenance paths` in every phase, including when the root authors
   the trivial plan directly. In each phase's existing `Verification` section, distinguish targeted `Implementation handoff checks` from the `Independent verification gate`; assign any canonical full suite only to the latter.
4. After the complete formal bundle exists, the root reads its overview, phase index, named risks, and any detail necessary for judgment, then decides whether independent plan review is proportionate. A trivial single-phase `luna` or `standard` plan may skip review. A non-trivial multi-phase or cross-component plan receives one review. A critical plan receives a focused review whose packet names its measurable risk, supporting evidence, affected area, and independently detectable defect class. Complexity alone is insufficient.
5. A plan reviewer reads the exact candidate overview and every current phase artifact and publishes `plan-review` with stable finding identifiers. Return accepted identifiers and that review artifact to the same planner. The planner publishes full replacement documents only for affected members and returns a new complete bundle. Additional review covers the changed members and interactions. The root observes convergence after a second material review; before a third correction, or immediately for marginal, contradictory, or out-of-scope findings, it reads the exact bundle and reviews, accepts or rejects findings by identifier, and corrects direction. This is an intelligent checkpoint, not a persisted counter or mechanical limit. Close planner and plan reviewer after the bundle is accepted.
6. Have the root present the exact accepted bundle at the user's altitude and request explicit user approval. Stop before implementation. Specification confirmation authorizes plan drafting, not implementation. On approval, write `plan.md` as the approved overview and exact phase manifest.
7. For each approved phase, best-effort update the task stage, then select exactly one implementation capability and owner. Pass explicit edit authority, worktree, plan-manifest path, exact overview identifier, exact current phase identifier, revision, stop conditions, accepted finding identifiers, and only new context. A context-maintenance fix additionally carries the exact discovery identifier, root `persist` disposition, validating context delta, and exact phase-listed maintenance path. Use `general_implementation` normally or `frontend_implementation` for a primarily frontend phase; never dispatch both as parallel owners of the same phase. Keep this implementation agent open and send accepted fixes back to it throughout the phase. The worker reads objective, scope, acceptance, verification, and dependencies from the approved artifacts, reads only prior outputs explicitly required by that phase, records material activity, and publishes a complete `implementation-report` for each stable handoff. While the implementation owner is active and has not returned an outcome or blocker, treat the implementation state as mutable: wait without reading the evolving diff, running speculative canaries against it, or sending design corrections. Continue only user dialogue, agent/resource coordination, and root-owned setup that does not inspect or exercise the evolving implementation. Intervene only for an owner-reported blocker, a material user scope change, or indispensable external evidence that invalidates the assignment.
8. At each implementation-owner handoff, consume the implementation artifact or inline fallback and perform at most one bounded check of exact Git identity, status, allowed-path scope, `git diff --check`, and the declared evidence inventory. If the root directly investigates a possible correctness defect, complete and confirm that investigation against the exact current source and diff before contacting the owner or pausing the phase cohort. Send one consolidated finding packet with evidence, impact, and acceptance; never send provisional or superseding directions.
   Dispose any returned context-discovery identifiers before routing a dependent consumer.
9. Dispatch `runtime_verification` for applicable checks and `browser_acceptance` only for a named browser scenario. Pass exact overview, phase, and implementation-report identifiers plus explicit verification authority and revision. Create at most one verifier per used capability and reuse it for affected reruns. Each verifier publishes a complete `verification-report` for its capability and evaluated revision. Once a stable revision packet is under verification, stop speculative root source review. Interrupt only when the revision changed or a confirmed finding invalidates the packet. If verification returns `failed`, return its exact report identifier and accepted finding identifiers to the same implementation owner and re-verify. If it returns `blocked`, the root decides whether review proceeds on source alone and records the reason in review evidence. Dispose any verifier context discoveries before downstream use. Dispatch `independent_review` only after every required verifier has passed or its blocker is explicitly accepted.
10. Then dispatch one `independent_review` agent with exact overview, phase, implementation, verification, and required context identifiers or labeled inline fallbacks. Keep it open for meaningful delta review. It judges approved intent before project guardrails, source, diff, and verification; publishes an initial `implementation-review` whose `Context basis` names only evidence actually consulted; and later receives only new or replaced evidence while naming the full-review base. It opens context only for a named `Review use`. A context discovery requires an exact `Affected judgment` and current-task consumer; incidental context is omitted, and only a named material judgment can block. For a second critical review, reuse `independent_review` only for a named measurable risk and independently detectable defect class.
11. Return the review artifact and accepted finding IDs to the same owner; do not restate the findings. Validate stale context only when at least one result can change acceptance, a finding disposition, replanning, or required `persist`; otherwise discard it without dispatch. Send a confirmed descriptive correction to the same owner only with `persist`, its validating delta, and an exact authorized path. After correction, rerun affected verification and always obtain a post-edit context delta for the changed paths and dirty revision. Send only replacement reports, fresh context evidence, and the meaningful delta to the same reviewer. Never accept or commit while a named material context judgment remains unresolved.
12. After final evidence is consumed and every material context discovery has an explicit disposition, inspect each phase agent's latest `cleanup` and `retained_resources` declarations. Do not contact an agent that reported `cleanup: pass` with `retained_resources: none`. Send one parallel cleanup-only follow-up, with no new implementation or verification work, only to owners that reported authorized retained resources, `partial`, or `blocked`; stop root-owned shared test processes at the same boundary. Consume those cleanup results. Follow the host close contract. Under V1 call `close_agent` so descendants close as well. Under V2, where no true close operation is exposed, and on Cursor, require every phase agent to be `completed` with no active descendant or retained resource. A known live agent or owned process with worktree write access blocks commit; an unclosed source-read-only task tab is partial cleanup and does not invalidate accepted evidence. The root may stop directly only a root-owned resource or an exact safely addressable handle reported by its owner. Never scan for or kill unrelated processes or close unrelated browser state.
13. Have the root commit the accepted phase through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), then update that phase's status and commit in the manifest. Git is the commit authority; do not create a commit artifact.
14. When the same causal failure repeats, correction cycles fail to converge, scope expands, or evidence indicates a deeper shared cause, stop blind retries and choose: reassess, recommend a tier change, dispatch `difficult_debugging`, or ask the user at an authority boundary. The debugger publishes `debugging-report`; return its exact identifier to the same owner without root-authored diagnosis replay. Distinct legitimate findings alone are not an escalation trigger.
15. After every phase is reviewed, verified, torn down, and committed, set `plan.md` to `completed` and best-effort mirror that descriptive state. Failure to update coordination never changes the commit or plan result.

Apply that contract at steps 7, 10, 11, 13, 15, and delivery respectively.

Wait for live agents with the host wait contract in non-interruptive ten-minute windows (`timeout_ms: 600000` on Codex; Cursor uses the background Task completion analogue).
Completion wakes the root immediately; timeout means only that the agent is still working. After a timeout,
wait again without a status request, restart, or interrupt. After 30 accumulated minutes without a final result, assess
once for concrete blocker evidence; elapsed time alone is not a failure. Interrupt only
for cancellation, a material scope change, or indispensable information that
invalidates the current assignment. A normal timeout is not a user-visible transition and produces no progress update unless the user asks; report the 30-minute assessment only when it establishes a material blocker or transition.

Frontend visual iteration and browser acceptance use `browser_route: auto | in_app | chrome`. Explicit user selection, whether relayed by the root or supplied in the agent conversation, must be attempted even when the scenario is a canary for a previously failing tool and remains fixed without fallback. A profile may report that route's technical blocker but may not veto or substitute it. Follow the host spawn reference for `auto` / `in_app` / `chrome`. Computer Use and standalone browser automation are not route substitutes except Cursor `auto` mapping to Playwright. A functional failure, application timeout, or selector problem never triggers fallback. Every run creates a fresh task-owned tab, never claims or reuses a user or prior-run tab, and closes its exact tab and supporting processes before every successful, failed, or blocked handoff. Browser-work handoffs retain nothing and report `retained_resources: none`; browser control ends with the task tab rather than by closing the Chrome application or a shared window. Preserve unrelated tabs, sessions, windows, and browser state. Frontend and independent acceptance tabs and evidence remain separate; browser acceptance is an independent verifier dispatch. The frontend owner never accepts its own work.

On Codex, Orchestra synchronizes Guardian (`:workspace`, `on-request`, and Auto-review)
as the default. Cursor observes the host permission choice and never writes permission configuration. The active permission choice for the task, host, or launcher
remains authoritative: Orchestra never changes it or blocks execution solely
because it differs. When Codex Guardian is active, commands inside the workspace run
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

Phase commit and phase teardown are not profiles or capabilities. Agents clean their owned resources before each handoff; after review and verification pass, the root performs only the fallback cleanup described above, then retires the cohort with the host close contract. It uses direct Git by default through [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) and may invoke `commit_phase.py` when exact-path staging is useful. An isolated teardown or mechanical Git failure stays root-local. PR observation is also direct: the root invokes `pr.py observe` through [orchestra-pr-review](../orchestra-pr-review/SKILL.md), then reuses `independent_review` when PR feedback needs code-review judgment. Accepted PR fixes return to the same implementation owner.

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
