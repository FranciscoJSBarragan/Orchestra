# Orchestra Vision

## Mission

Help an individual developer take a software change from idea to verified
delivery with strong engineering judgment, useful multi-agent specialization,
and a favorable quality-to-cost ratio.

## Vision

Orchestra should make it practical to hand a well-defined implementation to a
Codex orchestrator and trust it to reach a correct, reviewed, and committed
result. The user remains the product owner and final authority; the
orchestrator acts as the technical lead responsible for execution.

The desired experience is not maximum process. It is the smallest dependable
process that puts intelligence where it has leverage: understanding the
problem, planning non-trivial work, implementing carefully, finding real bugs,
and verifying behavior.

## Primary users

- Individual developers.
- Vibe coders who need high-level explanations and reliable execution.
- Small teams or personal projects that may choose direct local integration or
  a GitHub PR depending on repository policy and user preference.

Orchestra is not initially optimized for highly regulated enterprises or
organization-wide approval bureaucracy.

## Product principles

### Intelligent orchestration

The orchestrator is not a brainless dispatcher. It frames the problem,
synthesizes evidence, negotiates scope with the user, selects the tier, chooses
the next specialist, handles ordinary blockers, and makes the final technical
judgment from fresh evidence.

Detailed plans belong to planning specialists for non-trivial work, and code
belongs to implementation workers. That separation protects context and
independence; it does not remove thought or responsibility from the root.

### Proportional workflow

The workflow expands only when risk or complexity warrants it. Light work uses
two focused subagents. Standard work adds bounded context and planning.
Critical work adds the extra scrutiny justified by actual risk.

Unknown scope is never classified as light merely to save cost.

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

### Specialized agents

Recurring responsibilities should have focused profiles and prompts. A planner,
reviewer, debugger, browser tester, and phase committer do not share one generic
persona. Specialization is added when it creates a distinct, recurring contract
with measurable value—not merely to increase the number of roles.

### Simple Git, strong delivery

Git remains the transaction and history system. Orchestra adds scope checks,
structured intent, verification, and delivery coordination, but does not build
a second transaction engine around Git.

## Success criteria

Orchestra succeeds when:

- ordinary tasks finish without workflow repair or manual state cleanup;
- phase commits are routine and traceable;
- review effort finds or prevents meaningful defects;
- failures explain the cause and the next useful action;
- local integration leaves `main`, branches, and worktrees clean;
- the PR path can open, review, fix, push, and converge without losing intent;
- the root context remains focused and user communication stays clear;
- the user judges the product dependable in real usage.

## Non-goals

- Replacing Git, GitHub, CI, or repository tests.
- Requiring PRs for every project.
- Implementing a generalized enterprise approval platform.
- Persisting every internal thought or agent transition.
- Creating a schema, artifact, or state machine for every workflow step.
- Re-reviewing cosmetic preferences until a budget is exhausted.
- Porting to Hermes, Devin, or another harness before user-approved Codex
  maturity.
- Building speculative specialist profiles before a real recurring need exists.
