# Orchestra Vision

## Mission

Help an individual developer turn an explicitly activated Orchestra request —
from exploration or a candidate specification through an approved plan — into
verified delivery with strong engineering judgment, useful multi-agent
specialization, and a favorable quality-to-cost ratio.

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
- Small teams or personal projects that may choose direct local integration or
  a GitHub PR depending on repository policy and user preference.

Orchestra is not initially optimized for highly regulated enterprises or
organization-wide approval bureaucracy.

## Product principles

### Intelligent orchestration

The orchestrator is not a brainless dispatcher. It reuses the preceding
conversation, obtains a bounded minimum brief, selects an initial tier, and
creates the isolated task resources needed to gather focused repository
evidence. It then closes genuine specification gaps, synthesizes that evidence,
confirms the final scope with the user, revalidates the tier, chooses the next
capability dispatch, handles ordinary blockers, and makes the final technical
judgment from fresh evidence.

The root owns the task plan and composes focused capabilities with four stable
agent responsibilities: analysis, implementation, independent review, and
verification. That separation protects context and independence without
creating a new profile for every domain or removing technical responsibility
from the root.

### Explicit, proportional workflow

Workflow selection belongs to the user. A planning-only host mode never mutates
through Orchestra, and ordinary change, plan, or implementation requests remain
direct work. Only an explicit `$orchestra` invocation or an unequivocal
imperative to use or start Orchestra activates the workflow. Orchestra then
uses standard execution by default and adds critical scrutiny only for actual
high-impact risk.

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

Tests run with ordinary sandboxing unless their packet declares a concrete need
for elevation. Before broadening verification or diagnosing any failed test,
Orchestra repeats that exact command once with elevated permission. A pass
records an environment dependency; a repeated failure is trustworthy failure
evidence; unavailable or unsafe elevation is a blocker.

Current source and Git provide repository context. Project tests, runtime
evidence, and independent review provide the complementary correctness signals;
Orchestra does not maintain a separate repository index or control plane.

### Composable agents

Orchestra keeps four behavior-only base profiles: `analyst`,
`implementation_worker`, `reviewer`, and `verifier`. The root explicitly adds
the capability needed for a dispatch, such as technical planning, frontend
implementation, difficult debugging, or browser acceptance. Applicable internal
playbooks provide domain instructions without becoming public skills or
additional personas; some assignment keys use only base-profile behavior.

The profile boundary follows responsibility and independence, while the
capability boundary follows the work being performed. New recurring knowledge
should normally become a playbook, not a profile.

Repository context is an early, focused conversation aid rather than a late
planning formality. Orchestra never dispatches it without a minimum objective
and bounded factual questions. Additional passes answer only newly discovered
questions through context deltas, and every context analyst closes after its
result is consumed.

The installed assignment remains authoritative. When the external standard
matrix assigns `repository_context` to Composer Fast but the internal subagent
runtime cannot accept that model, only that capability may use Luna high as a
transient fallback. The substitution is remembered only for the live task and
does not create a visible task, alter the installed matrix, or establish a
fallback for any other capability.

Within a phase, Orchestra keeps the implementation owner, independent reviewer,
and one verifier for each used verification capability available for fixes,
reruns, and delta review. One-shot analysis agents close after their result is
consumed. Before the phase commit, the root closes the phase cohort and cleans
only its known temporary processes and browser tabs; those handles remain
transient and never become a registry.

Browser work defaults to Codex's isolated in-app Browser. An explicit route may
select it or Computer Use with Chrome from the start; otherwise Chrome is a
fallback only when the in-app Browser is unavailable or lacks a capability
required by the scenario. A product failure never triggers a browser switch.

### Simple Git, strong delivery

Git remains the transaction and history system. Orchestra adds scope checks,
structured intent, verification, and delivery coordination, but does not build
a second transaction engine around Git.

Each formal task receives its own branch and sibling worktree before repository
analysis. Current source checkouts are never repurposed, cleaned, or mutated
for new tasks. Scoped prior work may be adopted into the dedicated task
worktree while preserving source state and existing commits. Completed task
resources are removed only after exact integration evidence proves cleanup
safe.

## Success criteria

Orchestra succeeds when:

- ordinary tasks finish without workflow repair or manual state cleanup;
- accepted phases leave no active write-capable agent or owned test process;
- phase commits are routine and traceable;
- review effort finds or prevents meaningful defects;
- failures explain the cause and the next useful action;
- local integration leaves the base, task branches, and worktrees clean;
- the PR path can open, review, fix, push, converge, merge when authorized, and
  clean exact task resources without losing intent;
- the root context remains focused and user communication stays clear;
- the user judges the product dependable in real usage.

## Non-goals

- Replacing Git, GitHub, CI, or repository tests.
- Requiring PRs for every project.
- Implementing a generalized enterprise approval platform.
- Persisting every internal thought or agent transition.
- Creating a schema, artifact, or state machine for every workflow step.
- Building a plan CLI, Kanban board, or workflow control plane.
- Re-reviewing cosmetic preferences until a budget is exhausted.
- Porting to Hermes, Devin, or another harness before user-approved Codex
  maturity.
- Building extra profiles for capabilities that compose with the four
  base responsibilities.
