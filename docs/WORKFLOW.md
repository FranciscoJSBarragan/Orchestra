# Orchestra Workflow

## End-to-end flow

```mermaid
flowchart TD
    U["User describes an implementation"] --> O["Orchestrator frames the problem and selects a tier"]
    O --> L{"Tier"}
    L -->|"Light"| LW["Implementation worker"]
    LW --> LR["Independent reviewer and verifier"]
    L -->|"Standard or critical"| C["Bounded analyst context"]
    C --> S["Orchestrator synthesizes and aligns with user"]
    S --> P["Root writes the local task plan with analyst support"]
    P --> A["User approves implementation"]
    A --> F["Execute the next phase"]
    F --> R["Review and verify"]
    R -->|"Material finding"| F
    R -->|"Accepted"| M["Root commits the phase"]
    M --> N{"More phases?"}
    N -->|"Yes"| F
    N -->|"No"| D["Delivery-ready implementation"]
    LR --> M
    D --> H{"User or prior delivery instruction"}
    H -->|"Hold"| X["Committed branch/worktree ready"]
    H -->|"Local integration"| LI["Verify, integrate, clean worktree and branch"]
    H -->|"PR"| PR["Open PR, review/fix/push until clean"]
    PR --> PM["Merge only when separately authorized"]
```

## Orchestrator behavior

The orchestrator maintains the main objective while adapting safely to facts
found during execution. It does not stop for routine technical choices and does
not blindly follow a stale step when a reversible correction is clearly needed.

It reports meaningful scope or design changes to the user. It asks before
crossing the high-impact boundaries defined in `AGENTS.md`. It owns capability
routing, the local plan, phase commits, direct PR observation, and final
judgment.

## Tier flows and models

The user selects the root's current Sol medium or Sol high session
configuration outside Orchestra. The root has no machine-readable assignment,
and Orchestra never changes its model or reasoning effort.

For every spawned dispatch, the root selects the explicit capability, base
profile, model, and reasoning effort below. Profiles contain behavior only;
public skill names remain unchanged. `general_implementation` and
`independent_review` are assignment keys whose behavior remains in the base
`implementation_worker` and `reviewer` prompts; neither has an internal
playbook.

The only internal playbooks are `repository_context`, `web_research`,
`technical_planning`, `difficult_debugging`, `frontend_implementation`,
`browser_acceptance`, and `runtime_verification`. `architecture_analysis` uses
the shared architecture guidance reference also used with `technical_planning`
or `independent_review` when architecture is named; it has no dedicated
playbook.

| Tier | Capability | Base profile | Model | Reasoning |
| --- | --- | --- | --- | --- |
| Light | `general_implementation` | `implementation_worker` | `gpt-5.6-luna` | `max` |
| Light | `independent_review` | `reviewer` | `gpt-5.6-luna` | `max` |
| Light | `runtime_verification` | `verifier` | `gpt-5.6-luna` | `max` |
| Standard | `repository_context` | `analyst` | `gpt-5.6-luna` | `xhigh` |
| Standard | `web_research` | `analyst` | `gpt-5.6-luna` | `xhigh` |
| Standard | `technical_planning` | `analyst` | `gpt-5.6-sol` | `high` |
| Standard | `architecture_analysis` | `analyst` | `gpt-5.6-sol` | `high` |
| Standard | `difficult_debugging` | `analyst` | `gpt-5.6-sol` | `high` |
| Standard | `general_implementation` | `implementation_worker` | `gpt-5.6-luna` | `max` |
| Standard | `frontend_implementation` | `implementation_worker` | `gpt-5.6-sol` | `medium` |
| Standard | `independent_review` | `reviewer` | `gpt-5.6-sol` | `medium` |
| Standard | `browser_acceptance` | `verifier` | `gpt-5.6-luna` | `xhigh` |
| Standard | `runtime_verification` | `verifier` | `gpt-5.6-luna` | `max` |
| Critical | `repository_context` | `analyst` | `gpt-5.6-sol` | `medium` |
| Critical | `web_research` | `analyst` | `gpt-5.6-sol` | `medium` |
| Critical | `technical_planning` | `analyst` | `gpt-5.6-sol` | `high` |
| Critical | `architecture_analysis` | `analyst` | `gpt-5.6-sol` | `high` |
| Critical | `difficult_debugging` | `analyst` | `gpt-5.6-sol` | `high` |
| Critical | `general_implementation` | `implementation_worker` | `gpt-5.6-sol` | `high` |
| Critical | `frontend_implementation` | `implementation_worker` | `gpt-5.6-sol` | `high` |
| Critical | `independent_review` | `reviewer` | `gpt-5.6-sol` | `high` |
| Critical | `browser_acceptance` | `verifier` | `gpt-5.6-sol` | `medium` |
| Critical | `runtime_verification` | `verifier` | `gpt-5.6-sol` | `medium` |

Light has no context, research, planning, architecture, difficult-debugging,
frontend, or browser-acceptance dispatch. Frontend implementation or named
browser acceptance makes a task at least standard. A second critical review
reuses `independent_review` with Sol high only for a named measurable risk and
independently detectable defect class. No Orchestra assignment uses Sol xhigh.

Frontend implementation composes `implementation_worker`; browser acceptance
composes `verifier`. They remain independent and never run as one combined
role.

## Context and planning

For standard and critical work:

1. The root performs a read-only Graphify configuration and freshness check. A
   fresh usable graph may focus discovery. One bootstrap phase is added for
   missing CLI or artifact configuration, or safely repairable hooks in an
   eligible non-linked worktree. Linked hook automation is `partial`, but graph
   freshness still depends on Git delta, pending evidence, and query smoke;
   stale, pending, or failed graph use falls back to source without bootstrap.
2. An `analyst` with `repository_context` inspects only the domains needed for
   the request.
3. The orchestrator merges evidence into a compact problem statement.
4. The orchestrator and user settle objective, constraints, acceptance, and
   relevant product choices.
5. The root writes the formal plan, using an `analyst` with
   `technical_planning` or `architecture_analysis` when useful.
   When required CLI or artifact configuration is absent, or eligible
   non-linked hooks are safely repairable, this first standard or critical plan
   contains one explicit bootstrap phase; detection alone never mutates the
   repository.
6. A critical plan audit is an independent `reviewer` dispatch only when its
   packet names a measurable risk, supporting evidence and affected area, and
   an independently detectable defect class. Complexity alone is insufficient.
7. The orchestrator summarizes the plan at the user's altitude and requests
   implementation approval.

Standard and critical implementation does not begin until the user explicitly
approves the aligned plan. That approval covers implementation and successful
commits at the approved phase boundaries; it does not authorize merge, release,
deployment, production mutation, or another delivery action.

### Local task plan

The root maintains exactly one local plan per standard or critical worktree at
`git rev-parse --git-path orchestra/plan.md`. It is never versioned and is an
intent and resume aid for the root, not a workflow database. It records the
objective, tier, branch, base revision, decisions, phase contracts,
verification, current phase, blocker, next action, and uncommitted-work note.

Its statuses are:

- `draft`: alignment is incomplete and implementation is not authorized;
- `active`: the root is executing after explicit user approval;
- `blocked`: execution stopped at a named blocker and next action;
- `completed`: phases are reviewed, verified, and committed, while delivery
  authority remains separate.

Explicit user approval moves `draft` directly to `active`; approval is not a
persisted status. The normal lifecycle is `draft` to `active` to `completed`,
with `active` to `blocked` to `active` when needed. The root owns every update;
plan state never grants authority beyond the user's instruction.

On resume, the root resolves the path again and reconciles the plan with
`git status`, branch, HEAD, merge base, and relevant commits. Git is
authoritative for code, worktree state, and history; the plan is authoritative
only for approved intent and recorded progress. The root corrects stale
progress, revalidates affected evidence, and never infers missing approval. A
missing or unreadable plan prevents automatic continuation until it is
reconstructed and realigned with the user. Worktree cleanup removes the plan;
there is no global index, plan CLI, Kanban board, event log, or state engine.

### Graphify lifecycle

Graphify is default-on for standard and critical planned repositories and is
always advisory. The root is its sole lifecycle owner; Graphify adds no agent
profile, capability, playbook, helper, wrapper, schema, policy gate, or plan
status. `inactive`, `active`, `stale`, and `pending` describe observed tool and
repository conditions only; Orchestra does not persist them as workflow state.

Light work may query an already useful graph when the root deliberately chooses
to, but it never installs, repairs, upgrades, or bootstraps Graphify
automatically.

#### Read-only configuration and freshness detection

Before planning standard or critical work, the root first checks configuration:

- the `graphify` command is available;
- `git ls-files graphify-out` contains exactly `graphify-out/graph.json`,
  `graphify-out/graph.html`, and `graphify-out/GRAPH_REPORT.md`;
- repository ignore rules ignore `graphify-out/manifest.json`,
  `graphify-out/cost.json`, and every other generated Graphify path while
  allowing exactly those three tracked outputs.

Only a missing command, an incorrect required tracked/ignored artifact boundary,
or reliably absent required native hooks may make configuration inactive.
Before any hook-status call, the root resolves and canonicalizes both
`git rev-parse --git-dir` and `git rev-parse --git-common-dir`. When they
differ, the repository is a linked worktree and native Graphify hook refresh is
unsupported there: record hook automation as `partial`, preserve existing
common hooks, and do not call hook status, install, reinstall, or uninstall
hooks, add a wrapper or alternate hook, or add bootstrap solely for hooks. This
does not invalidate the graph. When the command exists, continue read-only to
the relevant Git delta, pending evidence, and query smoke; if they prove the
tracked graph fresh at HEAD, it remains usable advisory context and the root
tells `repository_context` so, otherwise use source. When the command is
missing, add the one approved bootstrap and use source because query cannot run.
An incorrect artifact boundary may also add that bootstrap; its hook step is
skipped for the linked worktree.

Only when the command is available and the canonical Git directories are equal
does each detection pass execute `graphify hook status` exactly once and
interpret that one result:

- a valid result reporting both required hooks installed passes hook
  configuration;
- a valid result reporting either required hook absent adds one bounded
  bootstrap phase only when the resolved hooks destination passes the safety
  check below; an unsafe destination is `partial` with source fallback;
- command failure or uninterpretable output is `partial` with source fallback
  and never triggers bootstrap.

Before deciding that absent hooks are repairable, the root resolves Git's
actual hooks destination, including `core.hooksPath`, and applies the safety
check below.

After eligible hook configuration passes, or after linked hook operations are
skipped, and before treating the graph as usable, the root inspects the relevant
Git delta and Graphify pending-update evidence. Only then does it run the
representative read-only `graphify query` smoke check; it does not run hook
status again. Pending or stale evidence, or any query or hook execution failure, is
`partial` with immediate source fallback; it never adds another bootstrap
phase. These labels are transient root conclusions and are never persisted.
All detection is read-only. No package install, hook install, build, ignore
edit, generated file, or Git mutation occurs before plan approval.

#### Approved bootstrap phase

Plan approval authorizes one complete initial Graphify bootstrap as part of the
approved implementation:

1. run `uv tool install --upgrade graphifyy`;
2. run one complete initial `graphify .` build;
3. update repository ignore rules and version exactly `graph.json`,
   `graph.html`, and `GRAPH_REPORT.md` under `graphify-out/`, leaving
   `manifest.json`, `cost.json`, and all other generated data ignored;
4. review, verify, and commit that initial bootstrap snapshot through the
   ordinary root phase-commit path;
5. only after the bootstrap commit succeeds, resolve and canonicalize
   `git rev-parse --git-dir` and `git rev-parse --git-common-dir` again;
6. when those directories differ, preserve existing common hooks, skip hook
   status and every hook mutation, and record hook automation as `partial`;
   otherwise resolve Git's actual hooks destination without mutation: honor
   `git config --path --get core.hooksPath` when configured, otherwise use
   `git rev-parse --git-path hooks`, then canonicalize the resulting path;
7. for the non-linked branch, when that destination is outside the tracked
   worktree and installation will
   not modify a tracked hook, run `graphify hook install` for the native
   `post-commit` and `post-checkout` hooks;
8. only for an eligible non-linked worktree with the command available,
   interpret exactly one hook-status result;
9. for either branch, inspect the relevant Git delta and pending evidence before
   query smoke and graph-use decisions. A fresh tracked graph at HEAD remains
   usable even when linked hook automation is `partial`.

Installing hooks after the bootstrap commit prevents that commit from
immediately triggering a redundant structural rebuild.

If the resolved hooks destination is inside the tracked worktree, or native
installation would modify a tracked hook, preserve it unchanged, skip hook
installation, report `partial`, and continue from source. Do not create a
wrapper, alternate hooks path, or replacement hook. The same read-only safety
result prevents later plans from repeatedly adding bootstrap for that absence.

This authority does not cover external API credentials or material external
cost. If the complete build requires either, the root asks for separate user
authority; without it, bootstrap is `partial` and functional work continues
from source. Orchestra never runs `graphify codex install` and never writes a
Graphify-specific Codex instruction block.

#### Freshness during later phases

Safely installed native hooks own structural refresh after commits and checkout
awareness only in eligible non-linked worktrees; they do not establish semantic
freshness or correctness. Before using the graph for later context, each
detection pass first canonicalizes Git and common directories. A linked
worktree skips hook status and mutation and records hook automation as
`partial`. Otherwise, when the command is available, it interprets exactly one
hook-status result. Both branches then check the relevant Git delta and
pending-update evidence before query smoke/use. A fresh graph at HEAD may narrow
source inspection; stale or pending evidence, an unsafe hooks destination, or a
failed query or hook execution falls back immediately to source and is
`partial`. None triggers bootstrap or blocks implementation, tests, review,
commit, or delivery.

Do not run repeated semantic updates between functional phases. After every
functional phase is reviewed, verified, and committed, but before changing the
local plan to `completed`, the root runs semantic `graphify . --update` at most
once. If the three tracked outputs change, the root reviews them and creates one
separate graph-only commit containing only the changed versioned Graphify
outputs. If none changes, the result is `nothing_to_commit`. A failed final
update remains `partial`; source, Git, project tests, runtime evidence, and
independent review still determine functional completion.

#### Installation lifecycle and cleanup

The three tracked outputs travel with Git; the Graphify executable and native
hook installation do not. Every new clone repeats read-only configuration and
freshness detection. Install or reinstall hooks only when canonical Git and
common directories are equal and after resolving the actual Git hooks
destination and passing the tracked-worktree/tracked-hook safety check. When
that destination is safely untracked and installation-local, use
`graphify hook install` after cloning or hook removal and
`graphify hook uninstall` for deliberate cleanup. Linked worktrees preserve
existing common hooks and perform neither operation. A shared or worktree-local
`core.hooksPath` must not be described as clone-local or unversioned without
that proof. Ignored caches, `manifest.json`, and `cost.json` end with clone
cleanup or may be removed as disposable generated data. Removing the three
tracked outputs or repository ignore policy is a separate product change, not
routine cleanup.

## Phase execution

Each phase has one outcome, allowed scope, acceptance criteria, and verification
set. A phase-specific subplan is created only when the phase cannot be safely
delegated from the main plan.

The loop is:

1. The root selects one `implementation_worker` with `general_implementation`
   or `frontend_implementation`.
2. A `verifier` runs applicable checks and reports their observed results.
3. One independent `reviewer` checks specification, correctness, regressions,
   safety, and materially defect-prone design.
4. Accepted findings return to the same owner.
5. Re-run affected verification and review the meaningful delta.
6. The root commits directly or through the narrow commit helper when the phase
   passes.

If the same failure repeats, stop blind retries. The root may dispatch an
`analyst` with `difficult_debugging`, change the approach, or ask the user when
the decision crosses an authority boundary.

## Review policy

Automatically fix findings that demonstrate:

- incorrect behavior or unmet acceptance criteria;
- security, privacy, or data-integrity risk;
- likely regression;
- unsafe error handling or concurrency;
- a maintainability defect likely to cause future incorrect behavior;
- missing verification for important behavior.

Do not cycle on:

- personal style preference already covered by formatter/linter;
- speculative architecture without a concrete failure mode;
- unrelated cleanup;
- scope expansion disguised as review;
- repeated restatements of an already rejected suggestion.

## Worktrees and branches

New implementations normally start in a task branch and dedicated worktree so
multiple tasks can proceed independently. The task records its base branch and
worktree path without creating a global workflow database.

After authorized integration:

1. verify the exact task revision;
2. integrate using the selected local or PR path;
3. confirm the target branch contains the expected commit;
4. remove the task worktree and its local plan;
5. delete the merged task branch when safe.

Unmerged or dirty worktrees are never removed automatically.

## Commit path

Plan approval covers commits at successful phase boundaries. Commit execution
is a root responsibility, not an agent profile or capability. The root uses Git
directly or the narrow deterministic commit helper; it does not rediscover the
repository or reopen product decisions.

The commit implementation should preserve the useful `commitbot` behavior:

- inspect scope and relevant diff;
- use a structured message that captures why, acceptance, invariants,
  validation, and risks;
- stage only intended paths;
- use `git commit -F`;
- verify the stored commit message and resulting SHA;
- return success or a stable failure reason.

Git provides atomic commit and reflog behavior. Local commits do not require an
isolated index, crash journal, authority bundle, or repeated subprocess
validation.

## Delivery policy

A consumer repository stores an explicit delivery policy. When it is missing,
Orchestra asks the user once and recommends `hybrid`. It does not infer
permission from existing PRs, CI workflows, or branch history.

`orchestra.toml` contains only the delivery mode and ordered verification checks
as argument arrays. PR merge and local integration share that check runner;
commands never pass through a shell.

Supported policy modes:

- `pr-required`: final integration goes through a PR.
- `hybrid`: the user chooses local integration or PR per task.
- `local-direct`: local integration is permitted when explicitly requested.

## PR path

The unchanged public PR skills preserve the proven behavioral chain:

1. PR-open reads the complete branch commit range and diff.
2. The root synthesizes and publishes a compact `PR-CONTEXT` capsule.
3. The root calls the narrow PR helper directly to observe GitHub/CI and
   review-thread state.
4. The root evaluates actionable feedback against intent, current code, and
   scope, using an independent `reviewer` when code-review judgment is useful.
5. The implementation owner applies accepted fixes, verifies them, commits, and
   pushes.
6. The loop continues until two complete clean observations occur on the same
   head. The root passes the first clean head directly to the second observation
   in memory; a push or head change resets it.

GitHub remains the external truth. PR-CONTEXT lives only as one upserted capsule
in the PR body. The helper reports current checks and review-thread evidence; it
does not interpret feedback, fix code, route work, or persist state. The root
evaluates only unresolved, non-outdated feedback and returns accepted findings
to the same implementation owner.

`Open a PR` authorizes opening, review processing, fixes, commits, and pushes
needed to make that PR clean. It does not authorize merge unless the user said
`merge when clean` or separately requests merge later.

## Local integration path

Local integration is a direct alternative, not a degraded PR path. It requires:

- policy permission;
- explicit task-level user direction;
- clean task scope and fresh verification;
- integration into the intended base without rewriting unrelated history;
- confirmation of the result;
- worktree and merged-branch cleanup.

The mechanical path runs configured checks in the clean task worktree, permits
only conservative fast-forward integration, verifies that the base contains the
captured task SHA, and removes only a still-clean integrated worktree and fully
merged task branch. Divergence returns to the root for resolution.

It does not authorize release, deployment, or production mutation.

## Maturity

Automated checks and representative canaries provide evidence. The user decides
when Codex Orchestra is sufficiently mature to port to another harness.
