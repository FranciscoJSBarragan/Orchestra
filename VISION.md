# Orchestra Vision

## Mission

Help an individual developer turn an idea or explicitly activated Orchestra
request — from a new-project foundation, exploration, or a candidate
specification through an approved plan — into verified delivery with strong
engineering judgment, useful multi-agent specialization, and a favorable
quality-to-cost ratio.

## Vision

Orchestra should make it practical to hand a well-defined implementation to a
task root running inside T3 Code and trust it to reach a correct, reviewed, and
committed result. The user remains the product owner and final authority; the
root acts as the technical lead responsible for execution. T3 Code is the one
execution host: it supplies threads, worktrees, delegation, the browser and pull
request watching, while each provider it runs (Claude Code, Codex, Cursor and
others) is an executor the flow assigns per capability. Supporting another
provider is a row of data and a role check, not a host adapter.

The desired experience is not maximum process. Direct implementation and any
planning-only host mode remain available outside Orchestra. When the user
explicitly invokes Orchestra, it supplies the smallest dependable process that
puts intelligence where it has leverage: confirming the specification, planning
the work, implementing carefully, finding real bugs, and verifying behavior.

Reusable engineering and project-verification skills also support ordinary and
custom workflows, with proportional evidence and no implicit full activation.
An explicitly requested initiative can coordinate independent task roots across
concurrent tasks in one repository or several projects and repositories while
preserving local review and shared acceptance. Its parent handles global decisions without importing every child
transcript. A persistent Markdown register and context links support continuation
without becoming a task engine. The same
parent/task-root/role design runs on T3 threads, on the local machine or a
remote T3 environment. Inside T3 a Hermes thread may act as the dispatcher
parent: it works out a request with the user, recommends, launches and follows
task roots, and never implements.

The analysis, implementation, review, verification, and commit skills are
plain Markdown usable in any harness without the full planned workflow. Inside
T3 there is one flow: Orchestra ships a default provider and model for each
capability, and the user overrides them outside the package without forking
the flow.

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
conversation, obtains a bounded minimum brief, and performs a short read-only
preflight before selecting the configured managed or hybrid checkout path.
Orchestra then gathers focused repository evidence, closes genuine
specification gaps, synthesizes that evidence, confirms the final scope with
the user, chooses the next capability
dispatch, handles ordinary blockers, and makes the final technical judgment
from fresh evidence.

The approved objective, constraints, acceptance, and authority remain fixed
unless the user explicitly changes them. A proposed mechanism or causal
explanation is a hypothesis rather than part of the desired outcome: the root
challenges weak assumptions against current evidence and chooses the smallest
supported mechanism that preserves the approved user-visible result. Users
often describe where they want to arrive rather than the first step; the root
keeps that end state as the horizon and delivers it in cases the user can try,
the first one soon, so a misread or an unneeded part surfaces at the first try.

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

There is one flow, not a ladder of tiers. What a change touches decides its
extra scrutiny: a dedicated verifier for stateful data, credentials or external
environments, and a decision review for authorization, compatibility or data
integrity choices. Independent authority boundaries for production, security, payments,
destructive actions, and delivery remain in force.

### Explicit, proportional workflow

Workflow selection belongs to the user. A planning-only host mode never mutates
through Orchestra, and ordinary change, plan, or implementation requests remain
direct work. Only an explicit `$orchestra` invocation or an unequivocal
imperative to use or start Orchestra activates the workflow.

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
fails. Token savings, additional agents, more rules or passing structural
checks alone do not establish better task results. A helper or gate is an
improvement when its demonstrated quality or reliability benefit justifies its
total cost while protecting a demonstrated requirement or realistic risk.
The root's engineering judgment is part of that control surface, not a gap
that must be replaced with machinery.

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

When the approved work has a user-visible surface whose look or operable feel
the user should judge, Orchestra may pause after that phase's implementation
handoff for an optional user preview. Preview is not a tier, profile, or plan
status. Taste belongs there, not in independent review.

### Evidence before claims

Completion means the relevant verification actually ran and its result was
read. Review and test evidence should be fresh for the revision being delivered
without recomputing unrelated evidence that has not changed.

Orchestra observes T3's runtime mode and each provider's permission choice and
never writes permission configuration; the complete permission rules live in
`docs/WORKFLOW.md`. Deterministic product, assertion,
compilation, or CLI-usage failures remain real failures.

Current source and Git remain authoritative for repository state. Project tests,
runtime evidence, and independent review provide complementary correctness
signals. Task-private evidence artifacts let later agents navigate prior work without
root-authored replay.
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
existing semantic report; the root assigns its explicit disposition, discovery
never grants authority or creates a registry, and knowledge that must survive
task cleanup becomes durable only through an authorized versioned source
change, including tracked `.agent/` convention files when that store is in
use. Normative sources express intent or constraints and never follow current
code automatically merely because the two conflict. Before a task completes,
the root judges once whether it learned something about the repository worth
keeping and uses the existing canonical repository knowledge path; Orchestra owns no memory
store of its own. The disposition, persistence, and checkpoint mechanics live
in `docs/WORKFLOW.md`.

Waiting is passive coordination, not a status interrogation, and
implementation ownership is a stable observation boundary: while the owner is
active the root does not inspect or exercise the evolving implementation, and
a required user preview pause keeps only the task-owned resources needed to
show the approved result. The exact waiting, handoff, preview, and
verification-ordering rules live in `docs/WORKFLOW.md`.

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

The default implementation owner is the first deterministic quality gate. It
runs and autocorrects every required local deterministic check, including the canonical
full suite when one exists. The independent reviewer judges intent, source,
diff, tests, and evidence without routinely repeating those gates; it may run
only a minimal diagnostic check for a concrete defect hypothesis. Parent-side reproduction follows WORKFLOW "Cross-environment acceptance" only
when a named risk or evidence gap requires it; ordinary child check ownership
does not change. A separate
verifier is reserved for browser interaction, owned services or processes,
mutable data, credentials, network or external environments, or explicit
repository policy.

The flow's assignment, its defaults plus the user's overrides, remains
authoritative. T3 delegation carries every role to its provider; model-provider
bridges belong to separate products. An unavailable assignment requires an
explicit supported choice rather than a hidden fallback.

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

Browser work uses T3's browser or the configured `browser_route` in a fresh
task-owned tab; an explicit user route is never vetoed or substituted, and
Orchestra never claims user tabs or closes shared browser state. The routes and
tab lifecycle
live in `docs/WORKFLOW.md` ("Test permissions and browser routing").

### Idea-to-project continuity

When a request clearly starts from an idea, an empty directory, or a new
project, an implicitly available project-start skill helps define observable
behavior, choose a proportional stack, prepare a runnable vertical foundation,
and verify it after explicit mutation confirmation. It does not silently
activate Orchestra. The user may explicitly continue into Orchestra, which
reuses the established brief and evidence.

An existing repository has the mirror-image need: its conventions already
exist in code and habit but not in a form workers can cite. An explicit
repo-readiness skill verifies them from evidence, asks the user only what
evidence cannot settle, and writes the tracked `.agent/` store once, so later
tasks inherit that knowledge instead of rediscovering it.

### Simple Git, strong delivery

Git remains the transaction and history system. Orchestra adds scope checks,
structured intent, verification, and delivery coordination, but does not build
a second transaction engine around Git.

Each formal task creates one collision-free `orchestra/*` task branch
immediately after specification confirmation, in a managed Orchestra-owned
worktree or the opt-in hybrid clean primary checkout. Orchestra never pulls, implicitly merges, or
rebases setup work; existing work is never cleaned, stashed, or rewritten
implicitly; and completed resources are removed only when exact Git and
integration evidence make cleanup safe. The complete checkout mechanics live in `docs/WORKFLOW.md` ("Task checkout and
branch"), provider and permission mechanics in "Host adapters", and the installation boundary in `docs/ARCHITECTURE.md`.

Completion freezes the approved objective, acceptance, and artifact selection.
The terminal phase commit may advance for the reviewed corrections before delivery
specified in WORKFLOW, including PR fixes, joint acceptance and base refresh
within approved intent; new scope starts a new task. PR and local delivery
must match the effective task head to that terminal manifest commit before any
external or integration mutation.

## Success criteria

Orchestra succeeds when:

- delivered software meets the accepted behavior with correct code, coherent
  maintainable architecture and meaningful verification of its material risks;
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
  workflow transitions, approvals, commits, or delivery.
- Building an event-sourced ledger, mandatory heartbeat system, or remote
  coordination service before a demonstrated consumer requires one.
- Selecting an approved artifact by recency, or duplicating Git/GitHub facts as
  semantic reports without a downstream consumer.
- Re-reviewing cosmetic preferences until a budget is exhausted.
- Host adapters outside T3 Code. Other harnesses use the standalone skills;
  a provider runs Orchestra roles only through T3.
- Building extra profiles for capabilities that compose with the four
  base responsibilities.

## Distribution

Orchestra can be distributed as a self-contained plugin generated from its
canonical source. Skills and helpers remain one product; packaging does not
introduce another workflow runtime. A provider that acts as a task root needs
only the entry skill discoverable; roles read their skills by path. T3 and the
provider retain permissions and execution authority.

Public marketplace publication is separate work.
