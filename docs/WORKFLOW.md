# Orchestra Workflow

## End-to-end flow

```mermaid
flowchart TD
    U["User describes an implementation"] --> O["Orchestrator frames the problem and selects a tier"]
    O --> L{"Tier"}
    L -->|"Light"| LW["Implementation worker"]
    LW --> RV["Root runs the direct targeted verification"]
    RV --> LR["Independent reviewer"]
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
frontend, browser-acceptance, or verifier dispatch. The root itself runs the
single direct targeted verification that qualified the task as light and records
the observed command and exit status; if verification needs more than the direct
targeted check, the task is not light — escalate to standard. Named browser
acceptance makes a task at least standard. A frontend change may be light only
when every light condition holds, including one direct targeted verification;
otherwise it is standard. A second critical review reuses `independent_review`
with Sol high only for a named measurable risk and independently detectable
defect class. No Orchestra assignment uses Sol xhigh.

Frontend implementation composes `implementation_worker`; browser acceptance
composes `verifier`. They remain independent and never run as one combined
role.

## Context and planning

For standard and critical work:

1. An `analyst` with `repository_context` inspects only the domains needed for
   the request. The root may skip or reduce this dispatch only when it cites the
   specific prior evidence it reuses (artifact and HEAD, same session);
   otherwise dispatch. A reduced dispatch requests only the targeted context
   delta.
2. The orchestrator merges evidence into a compact problem statement.
3. The orchestrator and user settle objective, constraints, acceptance, and
   relevant product choices.
4. The root writes the formal plan, dispatching `technical_planning` (or
   `architecture_analysis` for a bounded named architecture question) when
   useful; for a small single-phase standard task the root may write the
   compact plan directly. A single-phase standard plan is explicitly compact:
   objective, one phase contract, verification, nothing else.
5. A critical plan audit is an independent `reviewer` dispatch only when its
   packet names a measurable risk, supporting evidence and affected area, and
   an independently detectable defect class. Complexity alone is insufficient.
6. The orchestrator summarizes the plan at the user's altitude and requests
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

## Phase execution

Each phase has one outcome, allowed scope, acceptance criteria, and verification
set. A phase-specific subplan is created only when the phase cannot be safely
delegated from the main plan.

The loop is:

1. The root selects one `implementation_worker` with `general_implementation`
   or `frontend_implementation`.
2. A `verifier` runs applicable checks and reports their observed results. If
   verification returns `failed`, return findings to the same implementation
   owner and re-verify before dispatching `independent_review`. If it returns
   `blocked`, the root decides whether review proceeds on source alone and,
   when it does, records the blocked reason in the review evidence.
3. One independent `reviewer` checks specification, correctness, regressions,
   safety, and materially defect-prone design.
4. Accepted findings return to the same owner.
5. Re-run affected verification and review the meaningful delta.
6. The root commits directly or through the narrow commit helper when the phase
   passes.

When either the same failure repeats (its second occurrence) or two fix-review
rounds with distinct legitimate findings fail to converge, stop blind retries
and choose: reassess the phase approach, dispatch `difficult_debugging` when
the pattern suggests a deeper cause, or ask the user when an authority boundary
is crossed.

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
   in memory; a push or head change resets it. The second observation on an
   unchanged head is a lightweight but complete re-poll of checks and review
   threads; it does not re-read the diff.

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
