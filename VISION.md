# Orchestra Vision

## Mission

Help an individual developer turn an idea or explicitly activated Orchestra
request — from a new-project foundation, exploration, or a candidate
specification through an approved plan — into verified delivery with strong
engineering judgment, useful multi-agent specialization, and a favorable
quality-to-cost ratio.

## Vision

Orchestra should make it practical to hand a well-defined implementation to a
Codex, Cursor, or Grok Build orchestrator and trust it to reach a correct, reviewed, and
committed result. The user remains the product owner and final authority; the
orchestrator acts as the technical lead responsible for execution. Codex,
Cursor, and Grok Build are first-class execution hosts; they share one product, skills, helpers,
and Git workflow, and each host supplies only spawn, models, conversation
identity, permissions, and browser routing.

The desired experience is not maximum process. Direct implementation and any
planning-only host mode remain available outside Orchestra. When the user
explicitly invokes Orchestra, it supplies the smallest dependable process that
puts intelligence where it has leverage: confirming the specification, planning
the work, implementing carefully, finding real bugs, and verifying behavior.

## Primary users

- Individual developers.
- Vibe coders who need high-level explanations and reliable execution.
- People starting from an idea who need a proportional, runnable project
  foundation before formal software delivery.
- Small teams or personal projects that may choose direct local integration or
  a GitHub PR depending on repository policy and user preference.

Orchestra is not initially optimized for highly regulated enterprises or
organization-wide approval bureaucracy.

## Product principles

### Intelligent orchestration

The orchestrator is not a brainless dispatcher. It reuses the preceding
conversation, obtains a bounded minimum brief, recommends an initial tier with
its material risk and cost-benefit, and performs a short read-only preflight
before selecting the configured managed or hybrid checkout path. The user chooses the active tier.
Orchestra then gathers focused repository evidence, closes genuine
specification gaps, synthesizes that evidence, confirms the final scope with
the user, recommends any justified tier change, chooses the next capability
dispatch, handles ordinary blockers, and makes the final technical judgment
from fresh evidence.

The approved objective, constraints, acceptance, and authority remain fixed
unless the user explicitly changes them. A proposed mechanism or causal
explanation is a hypothesis rather than part of the desired outcome: the root
challenges weak assumptions against current evidence and chooses the smallest
supported mechanism that preserves the approved user-visible result.

The root owns the task plan and composes focused capabilities with four stable
agent responsibilities: analysis, implementation, independent review, and
verification. That separation protects context and independence without
creating a new profile for every domain or removing technical responsibility
from the root.

User-facing explanations stay concise and distinguish verified facts,
supported inference, and uncertainty. When the host provides a visualization
capability, the root uses it only when a complex sequence, hierarchy,
comparison, or mapping becomes materially easier to understand. Simple
explanations remain prose, a missing visualization capability never blocks the
workflow, and phase agents do not create user-facing visualizations.

The active tier controls assignment intensity, not user authority. Tiers are
host-specific lookups. Codex native tasks offer standard and critical; Codex
external tasks may additionally use Luna as a cost-focused opt-in when the user
explicitly prioritizes cost for ordinary, bounded work. Cursor tasks offer
minimal, standard, and critical, with no native/external mode: minimal is the
equivalent of Codex Luna. Codex still defaults to standard; Cursor
recommends standard, and `minimal` when the user prioritizes cost or speed.
Cursor `critical` remains unassigned. Grok Build tasks offer standard and
critical on grok-4.6; there is no cheaper assigned tier, and `minimal` is
blocked.
Material risk still calls for standard or critical where those matrices exist.
A user may choose an available assigned tier or direct a safe transition within
the selected Codex mode after a concise recommendation. Independent authority
boundaries for production, security, payments, destructive actions, and
delivery remain in force.

### Explicit, proportional workflow

Workflow selection belongs to the user. A planning-only host mode never mutates
through Orchestra, and ordinary change, plan, or implementation requests remain
direct work. Preparing a `$orchestra-task` card remains inert. Only an explicit
`$orchestra` invocation, adoption of a prepared task from a native host chat,
or an unequivocal imperative to use or start Orchestra activates the workflow.
On Codex, Orchestra recommends standard execution by default and critical
scrutiny for actual high-impact risk; external Luna is considered only when the
user explicitly prioritizes cost for ordinary, bounded work. On Cursor it recommends `standard`, and `minimal` when the user prioritizes
cost or speed; unassigned Cursor `critical` remains blocked. On Grok Build it
recommends `standard` and offers `critical` for matching high-impact risk;
unassigned Grok `minimal` remains blocked. The
user makes the final tier choice among assigned tiers.

### Prepared-task Kanban and native-chat continuity

Any chat or harness may capture and prepare a concise software task in a private
local Kanban. Each new card receives an immutable human ID (`A1` through `A99`,
then `B1`, continuing after `Z99` with `AA1`) plus a technical UUID. Preparation
includes focused repository context and an explicitly confirmed specification,
but never starts an execution host, chooses a tier, creates a branch or
worktree, or grants implementation authority.

Only Task Control allocates those human IDs. A chat, Coordinator, checkout,
branch, or client never derives, increments, reserves, or defaults one. A task
started directly without adopting a card has no `A#` identity and is displayed
with repository plus human title. This keeps simultaneous direct tasks distinct
without introducing another allocator.

The user starts a ready card from a native Codex, Cursor, or Grok Build chat by asking that chat to
adopt its human ID with Orchestra. The chat becomes the visible conversational
owner, inherits its current permissions, and follows the normal Orchestra
checkout and approval flow. Revision-bound prepared context is reused when
current and receives only a focused delta when Git changed. Coordinator uses
the same UUID after checkout creation, so the Hub can join prepared and active
state without inventing another identity. Transfer to another native chat is
explicit and allowed only at a stable checkpoint. When that owning chat cannot
release the card, an explicit user resume in a different native host chat
reclaims ownership and resumes the same worktree and plan. Archiving never
deletes Git, documents, plans, worktrees, or chat history.

One card remains the normal unit and Orchestra's phases absorb ordinary
complexity. A confirmed minimal initiative exists only for real independent
execution, acceptance, repository, or delivery boundaries. Its cards keep
self-contained specifications and immutable `blocked_by` ordering; absence of
a dependency path exposes safe parallelism. `completed` dependencies wait for
reviewed terminal completion, while `delivered` dependencies wait for verified
integration or merge evidence and, in the same Git repository, a checkout that
contains the delivered base revision. The Kanban never schedules, starts,
pulls, or assigns worktrees.

### Quality per token

Tokens and time should be concentrated on:

- understanding requirements and repository context;
- implementation and root-cause debugging;
- tests and behavioral verification;
- high-signal reviews that prevent bugs and regressions;
- resolving actionable PR feedback.

They should not be consumed by repeated validation of unchanged authority,
duplicate state stores, whole-run restarts, or ceremonial agents for mechanical
Git operations.

Quality per token includes the complete cost of a mechanism: root and delegated
agent context, tool calls, wall time, and workflow repair when the mechanism
fails. More checks are not automatically safer. A helper or gate is an
improvement only when it reduces expected total cost while protecting a
demonstrated requirement or realistic risk. The root's engineering judgment is
part of that control surface, not a gap that must be replaced with machinery.

Every planned or added test maps to an observable acceptance journey or a named
regression risk. Duplicated coverage, tests added only to increase counts, and
brittle coupling to implementation details consume cost without adding useful
evidence unless those details are themselves an approved contract.

### Bounded autonomy

Within an approved objective and scope, the orchestrator may make reversible
technical decisions, adapt implementation details, reorder safe steps, add
necessary tests, and resolve ordinary failures.

It stops for user direction when a decision could cause data loss, mutate
production, alter an unagreed product behavior, change a public contract,
affect security or privacy policy, create material external cost, expand scope
substantially, or be difficult to reverse.

### Evidence before claims

Completion means the relevant verification actually ran and its result was
read. Review and test evidence should be fresh for the revision being delivered
without recomputing unrelated evidence that has not changed.

On Codex, Orchestra synchronizes Guardian (`:workspace`, `on-request`, and
Auto-review) as the default. Cursor and Grok observe the host permission choice and
never write Codex, Cursor, or Grok permission configuration. The active permission
choice for the task, host, or launcher remains authoritative; the complete
permission rules live in `docs/WORKFLOW.md`. Deterministic product, assertion,
compilation, or CLI-usage failures remain real failures.

Current source and Git remain authoritative for repository state. Project tests,
runtime evidence, and independent review provide complementary correctness
signals. A lightweight local coordination projection may retain task snapshots
and task-private evidence artifacts so later agents can navigate prior work
without root-authored replay. That projection never authorizes, validates, or
blocks Git, tier, phase, commit, or delivery operations.
New tasks keep their plan and semantic artifacts in one self-ignored
`.orchestra/` directory inside the selected worktree. This state remains
writable under normal workspace permissions, is removed only by guarded task
cleanup, and never depends on protected Git-metadata writes. Legacy tasks may
finish on their original private paths without dual writes.

Semantic handoffs are document-first across the whole workflow. Context,
planning, implementation, verification, debugging, and review agents publish
complete revision-identified Markdown results. The root routes exact artifact
identifiers, explicit authority, revision, accepted finding identifiers, and
only new deltas; it does not repeatedly summarize content already available to
the next agent.

Material context discovered after planning remains in the producing agent's
existing semantic report with evidence, revision, impact, and a stable local
identifier. The root decides whether to route that report to a current-task
consumer, validate the claim through a targeted repository-context delta,
replace an affected plan member, persist durable knowledge in authorized
versioned source documentation, or explicitly defer or discard it. Discovery
does not grant authority, make the claim canonical, or permit an agent to edit
an earlier artifact. Task-private reports support the current task; knowledge
that must survive task cleanup becomes durable only through an authorized
source change. This uses the existing report kinds and creates no shared
mutable context document, artifact kind, registry, or memory system.

The approved overview exposes a bounded, provenance-preserving `Review context`,
and each phase identifies both the exact context evidence its review consumes
and exact versioned documentation under `Context maintenance paths` when
conditionally authorized for maintenance. Independent implementation review
consumes that evidence directly, records `Context basis`, and remains read-only. When review
finds stale project information, the root validates the claim independently;
only a confirmed descriptive fact may return to the same implementation owner
for an authorized documentation correction. The corrected source receives a
fresh repository-context revalidation delta, affected verification, and delta
review before commit.
Normative sources express intent or constraints and never follow current code
automatically merely because the two conflict.

Waiting is passive coordination, not a status interrogation. The root uses
ten-minute wait windows that return immediately on completion, treats timeout
as continued work, and never interrupts merely to request progress. Thirty
minutes prompts at most one evidence-based blocker assessment.

Implementation ownership is also a stable observation boundary. While the
owner is active, the root does not inspect or exercise the evolving
implementation. At each owner handoff, it may perform one bounded identity,
scope, and evidence check, then completes any root-originated investigation
before returning one consolidated, confirmed finding packet. Once verification
starts against a stable revision, speculative root review stops; required
verification finishes before independent review begins.

### Composable agents

Orchestra keeps four namespaced behavior-only base profiles:
`orchestra_analyst`, `orchestra_implementation_worker`,
`orchestra_reviewer`, and `orchestra_verifier`. The root explicitly adds the
capability needed for a dispatch, such as technical planning, frontend
implementation, difficult debugging, or browser acceptance. Applicable
internal playbooks provide domain instructions without becoming public skills
or additional personas; some assignment keys use only base-profile behavior.

The profile boundary follows responsibility and independence, while the
capability boundary follows the work being performed. New recurring knowledge
should normally become a playbook, not a profile.

Repository context is an early, focused conversation aid rather than a late
planning formality. Orchestra never dispatches it without a minimum objective
and bounded factual questions. Additional passes answer only newly discovered
questions through context deltas. Each pass may publish a revision-identified
evidence artifact for direct downstream consumption, and every context analyst
closes after its result or fallback inline report is consumed.

Formal planning produces one overview and one self-contained document per
phase. The approved local plan preserves that overview and the exact phase
manifest rather than duplicating every phase. An implementation owner receives
the overview, its exact phase, and only explicitly required prior outputs.
The overview's review-context index points to exact repository evidence rather
than replacing it; each phase uses exact, non-glob documentation-maintenance
paths or explicitly states that none are authorized.

The implementation owner is the first deterministic quality gate. It runs and
autocorrects every required local deterministic check, including the canonical
full suite when one exists. The independent reviewer judges intent, source,
diff, tests, and evidence without routinely repeating those gates; it may run
only a minimal diagnostic check for a concrete defect hypothesis. A separate
verifier is reserved for browser interaction, owned services or processes,
mutable data, credentials, network or external environments, explicit
repository policy, and all critical phases. Critical work keeps double
evidence: the owner verifies first and a verifier repeats the applicable gate
independently.

The installed assignment remains authoritative. On Codex, a dual installation
uses the root session's model and multi-agent version to select its native V2
or external V1 matrix before task setup; that model configuration is immutable
for the task, while tier transitions remain available within it. Legacy Codex
installations retain their fixed native or external matrix. When the external
standard matrix assigns `repository_context` to its configured external model
but the internal subagent runtime cannot accept that model, only that
capability may use its compatible Luna-high entry as a transient fallback. The
substitution is remembered only for the live task and does not create a visible
task, alter the installed matrix, or establish a fallback for any other
capability. Cursor does not run session detection or native/external modes; it
reads one host matrix and currently assigns `minimal` and `standard`.

Within a phase, Orchestra keeps the implementation owner, independent reviewer,
and, only when the independent gate requires one, a verifier for each used
verification capability available for fixes, reruns, and delta review.
Analysis agents are one-shot except that a technical planner remains open
through a dispatched plan-review correction loop. Before each handoff, every
agent closes its own temporary processes, terminal sessions, and task tabs;
only a non-browser resource category explicitly authorized by the packet may
survive for phase reuse. Before the phase commit, the root
follows up only on authorized retained resources or incomplete cleanup, stops
its own shared processes, and retires the phase cohort with the lifecycle
evidence available to the active multi-agent protocol. Resource handles remain
transient and never become a registry.

Browser work uses a host-mapped `browser_route` in a fresh task-owned tab. On
Codex, `auto` falls back to the isolated in-app Browser only when Chrome is
technically unavailable or lacks a capability that the in-app Browser can
provide. On Cursor, `auto` maps to Playwright and `in_app` is blocked. An
explicit `chrome` or, on Codex, `in_app` route remains fixed, is attempted even
as a tool canary, and is never vetoed or substituted.
Each browser run closes its exact task tab before any handoff and a rerun opens
a new one; Orchestra never claims a user's existing tab or closes the Chrome
application, a shared window, or unrelated browser state. A product failure
never triggers a browser switch.

### Idea-to-project continuity

When a request clearly starts from an idea, an empty directory, or a new
project, an implicitly available project-start skill helps define observable
behavior, choose a proportional stack, prepare a runnable vertical foundation,
and verify it after explicit mutation confirmation. It does not silently
activate Orchestra. The user may explicitly continue into Orchestra, which
reuses the established brief and evidence.

### Simple Git, strong delivery

Git remains the transaction and history system. Orchestra adds scope checks,
structured intent, verification, and delivery coordination, but does not build
a second transaction engine around Git.

Each formal task creates one collision-free `orchestra/*` task branch before
repository analysis. Managed mode creates an Orchestra-owned worktree under
`${ORCHESTRA_WORKTREE_ROOT:-$HOME/.orchestra/worktrees}`; opt-in hybrid mode
creates the branch in the current clean primary checkout or linked worktree.
Shared runtime helpers, checkout mode, and worktree root install under
`${ORCHESTRA_HOME:-$HOME/.orchestra}`. Codex-only sync also records those
values under `$CODEX_HOME/orchestra/` for one compatibility window, requires
Codex 0.146.0 or later, and by default selects the built-in `:workspace`
permission profile, keeps `approval_policy = "on-request"`, and routes eligible
boundary requests through `approvals_reviewer = "auto_review"`. Cursor and Grok
sync never write Codex, Cursor, or Grok permission configuration. An explicit permission
choice for the current task, host, or launcher remains authoritative at
runtime. Sync installs no custom permission profile, writable-root list,
command rule, or Git bridge.
After a real write canary passes in the task's repository directory, the root
resolves and fetches the configured upstream for a fresh canonical-base task.
Managed mode creates the exact branch and worktree directly from the verified
remote commit without updating the base checkout. Hybrid mode fast-forwards a
strictly behind clean canonical base, while an ahead or diverged base blocks for
a user decision. A failed configured-upstream fetch blocks; a repository with
no remote/upstream may proceed only with its local base explicitly identified
as not remotely verified. Explicit noncanonical bases remain unchanged for
stacked work. Orchestra never pulls, implicitly merges, or rebases setup work.
Under Guardian,
protected shared Git metadata receives one exact automatically reviewed
escalation. Hybrid mode never implements on the starting branch, including
`main`; dirty or ambiguous state requires an explicit decision. Existing work
is never cleaned, stashed, or rewritten implicitly.
After branch/worktree creation, a deterministic helper initializes the ignored
worktree-local task state without changing Git status or requiring escalation.
Completed resources are removed only when exact Git and integration evidence
make that cleanup safe.

Completion freezes the approved objective, acceptance, and artifact selection.
The terminal phase commit may advance only for a reviewed PR fix that stays
inside that approved intent; new scope starts a new task. PR and local delivery
must match the effective task head to that terminal manifest commit before any
external or integration mutation.

## Success criteria

Orchestra succeeds when:

- a task can be prepared durably without starting Orchestra, then adopted in a
  visible native Codex, Cursor, or Grok Build chat without losing its origin, human ID, or
  UUID;
- ordinary tasks finish without workflow repair or manual state cleanup;
- accepted phases leave no active write-capable agent or owned test process;
- phase commits are routine and traceable;
- review effort finds or prevents meaningful defects;
- failures explain the cause and the next useful action;
- local integration removes only exact, safely merged task resources;
- delivery rejects a task head that is not the terminal manifest commit;
- the PR path can open, review, fix, push, converge, merge when authorized, and
  clean exact task resources without losing intent;
- concurrent tasks and their material activity can be queried without opening
  every agent conversation;
- downstream agents consume exact producer-authored documents without
  root-authored summary chains;
- material context discoveries reach a named current-task consumer or receive
  an explicit root disposition, while cross-task knowledge is preserved only
  through authorized versioned source;
- independent phase review consumes exact project-context evidence, blocks on
  material stale or conflicting context, and re-reviews validated documentation
  corrections made by the same implementation owner;
- the root opens complete documents mainly for approval, risk, authority, or
  convergence judgment;
- the root context remains focused and user communication stays clear;
- the user judges the product dependable in real usage.

## Non-goals

- Replacing Git, GitHub, CI, or repository tests.
- Requiring PRs for every project.
- Implementing a generalized enterprise approval platform.
- Persisting every internal thought or agent transition.
- Creating a schema, artifact, or state machine for every workflow step.
- Making coordination metadata, a dashboard, or a CLI authoritative for
  workflow transitions, approvals, commits, tiers, or delivery.
- Building an event-sourced ledger, mandatory heartbeat system, or remote
  coordination service before a demonstrated consumer requires one.
- Selecting an approved artifact by recency, or duplicating Git/GitHub facts as
  semantic reports without a downstream consumer.
- Re-reviewing cosmetic preferences until a budget is exhausted.
- Porting to Hermes, Devin, or any harness beyond the approved Codex and
  Cursor hosts.
- Building extra profiles for capabilities that compose with the four
  base responsibilities.
