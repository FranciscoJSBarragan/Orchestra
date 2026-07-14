# Orchestra Architecture

## Architectural objective

Build a Codex-native orchestration product whose complexity is dominated by
software delivery work, not by its own control plane.

```mermaid
flowchart LR
    U["User"] <--> O["Orchestrator"]
    O --> A["Specialized agents"]
    O --> W["Workflow skills"]
    W --> G["Git / GitHub / project tools"]
    A --> E["Compact evidence and results"]
    G --> E
    E --> O
    V["One validator"] --> W
    V --> A
    H["Thin hooks and CI"] --> V
```

## Target repository shape

```text
Orchestra/
├── README.md
├── VISION.md
├── AGENTS.md
├── docs/
│   ├── WORKFLOW.md
│   ├── ARCHITECTURE.md
│   └── ROADMAP.md              # non-canonical sequencing
├── .githooks/                 # versioned thin wrappers only
└── codex/
    ├── agents/                # specialized role profiles
    ├── skills/                # user-facing workflow entry points
    ├── scripts/               # deterministic mechanical helpers
    └── tests/
```

## Component responsibilities

### Orchestrator

Owns user dialogue, tiering, product clarification, routing, synthesis,
in-scope decisions, blocker resolution, delivery choice, and final judgment.
It holds compact context and delegates repository-wide reading.

### Specialized agents

Each recurring role has its own profile and prompt. Initial roles are:

- `repo_context_explorer`
- `planner`
- `plan_scope_auditor`
- `implementation_worker`
- `reviewer`
- `debugging_investigator`
- `web_researcher`
- `browser_acceptance_tester`
- `phase_committer`

PR polling and triage are the remaining two specialized roles in the PR-review
lane. Eleven profiles are the maximum supported set, not a growth target.
PR-open synthesis and PR-merge verification remain root responsibilities and may
use the configured Sol-high model assignment without adding profiles.

The profile set changes only when a recurring responsibility has a distinct
context, tool set, acceptance standard, and measurable value, while remaining
within the maximum. Profiles are not created speculatively.

Profiles share only minimal conventions: input packet shape, output status,
evidence references, scope boundaries, and stop conditions.

### Workflow skills

Skills describe the behavioral route and call deterministic helpers. Expected
public lanes are:

- orchestration and discovery;
- planned delivery;
- phase commit;
- PR open;
- PR review;
- PR merge;
- local integration;
- repository delivery policy.

They should remain readable and route to deeper references only when needed.

### Mechanical helpers

Scripts perform operations that benefit from deterministic behavior: parsing
Git status, validating structured messages, collecting PR state, publishing a
PR body, resolving review threads, running configured checks, synchronizing
managed resources through direct sync, and validating the suite.

Helpers return compact structured results. They do not make product decisions,
spawn agents, or own parallel approval systems.

## Minimal contracts

Orchestra may persist only contracts with direct consumers:

- repository delivery policy;
- approved plan and phase definition;
- structured commit message;
- compact commit result (`sha` or stable failure reason);
- PR context and PR-review state required to resume external asynchronous work;
- direct-sync manifest consumed by install, update, status, and uninstall.

Do not introduce a global workflow event ledger, authority-bundle chain,
duplicate Git index, commit recovery journal, or general-purpose workflow state
engine unless real usage later demonstrates a requirement Git/GitHub cannot
meet.

## Model and reasoning configuration

The approved target role matrix is documented in `WORKFLOW.md`. Its only
machine-readable configuration, `codex/config/roles.toml`, contains assignments
for currently executable lanes only. Workflow skills pass explicit model and
reasoning overrides from that file when spawning agents. Profile files contain
role behavior, not assignments.

Light tasks dispatch `implementation_worker`, `reviewer`, and `phase_committer`
with Luna max. Standard and critical target the role matrix documented in
`WORKFLOW.md` when those lanes become executable.

## Browser testing constraint

Codex's in-app Browser currently fails when invoked from a subagent. Therefore
`browser_acceptance_tester` must use Computer Use with Chrome:

1. Open a new Chrome tab for the target application.
2. Preserve unrelated existing tabs and sessions.
3. Execute the acceptance scenario through visible interaction.
4. Capture concise evidence and reproducible failure steps.
5. Return findings without editing source code.

The parent orchestrator may use the in-app Browser when appropriate, but the
delegated tester profile must not rely on it until capability evidence changes.

## Lightweight conformance and hooks

The workflow needs drift protection, but enforcement must remain thin.

### Canonical validator

`codex/scripts/validate_suite.py` is the only suite conformance engine. Its
checks should stay deterministic and fast enough for local use. It validates:

- required canonical files and direct-sync boundaries;
- skill links and profile references;
- model matrix/profile consistency;
- concise AGENTS/runtime instructions;
- forbidden distribution paths and historical product narrative;
- representative workflow contract tests.

It does not validate live approvals, replay agent history, or inspect unrelated
consumer repositories.

### Hooks

The Orchestra source repository should install one versioned pre-commit wrapper
that invokes the validator's quick mode. Consumer repositories do not receive
that hook unless their user explicitly opts in. No separate pre-push workflow is
required initially.

Hooks must:

- contain no independent workflow policy;
- avoid network calls and agent launches;
- never mutate files, stage changes, or commit;
- finish quickly and print one actionable failure;
- be installable and removable explicitly.

CI may call the full validator later. Hook, CI, and manual validation must not
implement three competing rule sets.

### Behavioral tests

Tests protect the few important invariants:

- light classification fails closed on ambiguity or risk;
- plan approval permits phase commits but not merge/deploy;
- PR-open authority includes the review/fix/push loop but not implicit merge;
- accepted review findings return to the same implementation owner;
- hooks call the validator without adding policy;
- local integration cleans only safely merged branches and worktrees;
- rejected authority/journal machinery is not introduced.

## Complexity safeguards

Before accepting a persistent artifact, schema, lock, transaction layer,
helper, or agent profile, document:

- its named consumer;
- a demonstrated failure, explicit requirement, or reproducible risk;
- why an existing Git, GitHub, Codex, or project-test primitive is insufficient;
- lifecycle, ownership, and cleanup;
- why its cost is proportional;
- why a smaller direct implementation does not suffice.

Review only the delta after a finding. If a mechanism fails this gate, stop and
simplify it. Graphify can inform repository context; it does not establish
correctness or policy.

The design explicitly rejects a global workflow event ledger, authority-bundle
chain, duplicate Git index, commit recovery journal, general-purpose workflow
state engine, and repeated validation of unchanged authority unless later
evidence passes the same gate.

Warnings about size or complexity may inform review, but arbitrary line-count
limits do not replace engineering judgment. The strongest guard is architectural:
one source of truth, narrow roles, deterministic helpers, and deletion of
unused mechanisms.

## Installation boundary

The source repository is authoritative. V1 installation uses only
repository-driven direct sync. A single sync tool owns explicitly managed Codex
resources, supports dry-run and backup, preserves unrelated user configuration,
and reports what it installed. Installation is never part of ordinary task
execution.
