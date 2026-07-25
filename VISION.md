# Orchestra Vision

## Mission

Help an individual developer turn an explicitly requested implementation plan
into verified delivery with strong engineering judgment, useful multi-agent
specialization, and a favorable quality-to-cost ratio.

## Vision

Orchestra should make it practical to hand a well-defined implementation to a
Codex orchestrator and trust it to reach a correct, reviewed, and committed
result. The user remains the product owner and final authority; the
orchestrator acts as the technical lead responsible for execution.

The desired experience is not maximum process. Direct implementation and native
Codex Plan Mode remain available outside Orchestra. When the user explicitly
requests a formal plan in normal chat, Orchestra supplies the smallest
dependable process that puts intelligence where it has leverage: confirming the
specification, planning the work, implementing carefully, finding real bugs,
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

The orchestrator is not a brainless dispatcher. It reuses the preceding
conversation, closes genuine specification gaps, synthesizes evidence, confirms
scope with the user, selects the tier, chooses
the next capability dispatch, handles ordinary blockers, and makes the final
technical judgment from fresh evidence.

The root owns the task plan and composes focused capabilities with four stable
agent responsibilities: analysis, implementation, independent review, and
verification. That separation protects context and independence without
creating a new profile for every domain or removing technical responsibility
from the root.

### Explicit, proportional workflow

Workflow selection belongs to the user. Native Plan Mode never invokes
Orchestra, and ordinary change or implementation requests remain direct work.
In normal chat, explicit planning intent starts Orchestra. Orchestra then uses
standard execution by default and adds critical scrutiny only for actual
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

### Simple Git, strong delivery

Git remains the transaction and history system. Orchestra adds scope checks,
structured intent, verification, and delivery coordination, but does not build
a second transaction engine around Git.

Each formal task receives its own branch and worktree before repository
analysis. Current worktrees are never repurposed for new tasks, and completed
task resources are removed only after exact integration evidence proves cleanup
safe.

## Success criteria

Orchestra succeeds when:

- ordinary tasks finish without workflow repair or manual state cleanup;
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
