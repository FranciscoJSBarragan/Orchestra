# Orchestra Vision

## Mission

Help an individual developer turn an idea or explicitly activated Orchestra
request — from a new-project foundation, exploration, or a candidate
specification through an approved plan — into verified delivery with strong
engineering judgment, useful multi-agent specialization, and a favorable
quality-to-cost ratio.

## Vision

Orchestra should make it practical to hand a well-defined implementation to a
Codex orchestrator and trust it to reach a correct, reviewed, and committed
result. The user remains the product owner and final authority; the
orchestrator acts as the technical lead responsible for execution.

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

The root owns the task plan and composes focused capabilities with four stable
agent responsibilities: analysis, implementation, independent review, and
verification. That separation protects context and independence without
creating a new profile for every domain or removing technical responsibility
from the root.

The active tier controls assignment intensity, not user authority. A user may
choose either tier or direct a safe transition between them after a concise
recommendation. Independent authority boundaries for production, security,
payments, destructive actions, and delivery remain in force.

### Explicit, proportional workflow

Workflow selection belongs to the user. A planning-only host mode never mutates
through Orchestra, and ordinary change, plan, or implementation requests remain
direct work. Only an explicit `$orchestra` invocation or an unequivocal
imperative to use or start Orchestra activates the workflow. Orchestra then
recommends standard execution by default and critical scrutiny for actual
high-impact risk; the user makes the final tier choice.

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

Orchestra synchronizes Guardian (`:workspace`, `on-request`, and Auto-review)
as the default while the active permission choice for the task, host, or
launcher remains authoritative; the complete permission rules live in
`docs/WORKFLOW.md`. Deterministic product, assertion, compilation, or
CLI-usage failures remain real failures.

Current source and Git remain authoritative for repository state. Project tests,
runtime evidence, and independent review provide complementary correctness
signals. A lightweight local coordination projection may retain task snapshots
and task-private evidence artifacts so later agents can navigate prior work
without root-authored replay. That projection never authorizes, validates, or
blocks Git, tier, phase, commit, or delivery operations.

Semantic handoffs are document-first across the whole workflow. Context,
planning, implementation, verification, debugging, and review agents publish
complete revision-identified Markdown results. The root routes exact artifact
identifiers, explicit authority, revision, accepted finding identifiers, and
only new deltas; it does not repeatedly summarize content already available to
the next agent.

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

The installed assignment remains authoritative. A dual installation uses the
root session's model and multi-agent version to select its native V2 or external
V1 matrix before task setup; that model configuration is immutable for the
task, while tier transitions remain available within it. Legacy installations
retain their fixed native or external matrix. When the external standard matrix
assigns `repository_context` to its configured OpenCode model but the internal
subagent runtime cannot accept that model, only that capability may use its compatible Luna-high
entry as a transient fallback. The substitution is remembered only for the live
task and does not create a visible task, alter the installed matrix, or
establish a fallback for any other capability.

Within a phase, Orchestra keeps the implementation owner, independent reviewer,
and one verifier for each used verification capability available for fixes,
reruns, and delta review. Analysis agents are one-shot except that a technical
planner remains open through a dispatched plan-review correction loop. Before
the phase commit, the root closes the phase cohort and cleans
only its known temporary processes and browser tabs; those handles remain
transient and never become a registry.

Browser work defaults to Codex's isolated in-app Browser. An explicit route may
select it or Computer Use with Chrome from the start; otherwise Chrome is a
fallback only when the in-app Browser is unavailable or lacks a capability
required by the scenario. A user-selected route is attempted even as a tool
canary and is never vetoed or substituted. A product failure never triggers a
browser switch.

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
Direct synchronization records both the effective absolute root and checkout mode and
requires Codex 0.146.0 or later. By default it selects the built-in
`:workspace` permission profile, keeps `approval_policy = "on-request"`, and
routes eligible boundary requests through
`approvals_reviewer = "auto_review"`. An explicit permission choice for the
current task, host, or launcher remains authoritative at runtime. Sync installs
no custom permission profile, writable-root list, command rule, or Git bridge.
After a real write canary passes in the task's repository directory, the root
creates the exact branch and, in managed mode, its worktree with direct Git; under Guardian,
protected shared Git metadata receives one exact automatically reviewed
escalation. Hybrid mode never implements on the starting branch, including
`main`; dirty or ambiguous state requires an explicit decision. Existing work
is never cleaned, stashed, or rewritten implicitly.
Completed resources are removed only when exact Git and integration evidence
make that cleanup safe.

## Success criteria

Orchestra succeeds when:

- ordinary tasks finish without workflow repair or manual state cleanup;
- accepted phases leave no active write-capable agent or owned test process;
- phase commits are routine and traceable;
- review effort finds or prevents meaningful defects;
- failures explain the cause and the next useful action;
- local integration removes only exact, safely merged task resources;
- the PR path can open, review, fix, push, converge, merge when authorized, and
  clean exact task resources without losing intent;
- concurrent tasks and their material activity can be queried without opening
  every agent conversation;
- downstream agents consume exact producer-authored documents without
  root-authored summary chains;
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
- Porting to Hermes, Devin, or another harness before user-approved Codex
  maturity.
- Building extra profiles for capabilities that compose with the four
  base responsibilities.
