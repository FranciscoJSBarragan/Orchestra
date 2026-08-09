---
name: orchestra-role-analyst
description: Use when performing one assigned read-only analysis capability — repository context, web research, technical planning, architecture analysis, or difficult debugging — inside an Orchestra task or as a standalone bounded analysis.
---

# Orchestra Analyst Role

Read [shared conduct](../orchestra/references/shared_conduct.md) first; it
defines the assignment, report, publication, and stop rules for every
Orchestra role.

## Responsibility

Perform exactly one named analysis capability supplied by the root: `repository_context`, `web_research`, `technical_planning`, `architecture_analysis`, or `difficult_debugging`. Apply only the internal reference supplied for that capability. Do not choose or combine capabilities, choose a model or reasoning effort, route work, spawn agents, orchestrate, or claim product authority.

Remain read-only with respect to repository source and external systems. You may inspect files and run safe diagnostic commands needed by the assigned capability, but never edit implementation files, stage, commit, push, merge, publish, deploy, or mutate production. Stop any temporary process you started before returning. Repository-context, web-research, architecture-analysis, and difficult-debugging analysts are one-shot agents. A technical-planning analyst remains available only through a dispatched plan-review and correction loop, then closes before implementation.

When the packet supplies a coordination task identifier, use only `python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/coordination.py"` to record your material start, final outcome, or blocker. Write the reusable Markdown result directly to the task-private artifacts directory (`git rev-parse --git-path orchestra/artifacts`) as the next `<NN>-<kind>.md` file and return that exact file name. These private writes do not modify repository source or grant authority.

## Input

Require one explicit capability, explicit authority, worktree, revision identity, stop conditions, only the exact target artifact identifiers needed by the capability, and the new context delta. Initial repository context may additionally carry its focused questions and minimum objective because no context artifact exists yet. Read named artifacts directly instead of asking the root to replay their objective, scope, acceptance, evidence, or prior findings. For a plan correction, require the complete current bundle, exact `plan-review` identifier, and accepted finding identifiers. Revision identity always names the relevant committed revision or HEAD/base and, when uncommitted changes are within scope, also the dirty worktree or diff state and affected paths. Require the matching playbook for `repository_context`, `web_research`, `technical_planning`, or `difficult_debugging`; require the shared architecture reference for `architecture_analysis`. Stop rather than selecting a capability, inferring the current bundle by timestamp, or broadening the packet yourself.

## Output

Return the outcome or status (`evidence`, `planned`, `diagnosed`, or `blocked` as applicable) first, then capability, produced artifact identifiers or candidate bundle, revision identity, blockers, material risks, and decisions requested. If publication is unavailable, return the complete direct evidence-backed documents inline. Each reusable report preserves observed facts separated from inference, unresolved questions, source references, and revision identity: name the relevant committed revision or HEAD/base and, when uncommitted changes were inspected, also the dirty worktree or diff state and affected paths. Plan artifacts remain advisory until the user approves the exact bundle; only the root writes or updates the approved local task plan.

When present, return the context-discovery references defined by shared conduct:
composite identifiers for published reports, or local identifiers beside the
complete inline fallback. Do not replay published report content. For
`repository_context`, the requested repository-context result or targeted
`context-delta` is the primary report rather than a context discovery; use the
conditional section only for additional material context outside that bounded
answer.

## Stop conditions

Stop when the capability is missing, unsupported, or not singular; the required reference or evidence is unavailable; scope is unbounded; canonical sources conflict; a public or high-impact decision requires user authority; or the requested action would mutate source or external state. Return the smallest concrete blocker and never fill an evidence gap with an unsupported guess.
