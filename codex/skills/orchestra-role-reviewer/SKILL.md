---
name: orchestra-role-reviewer
description: Use for one independent bounded plan, architecture, implementation, or PR review inside Orchestra or as a standalone task.
---

# Orchestra Reviewer Role

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Read [shared conduct](../orchestra/references/shared_conduct.md) first. It
defines the common packet, authority, cleanup, evidence, report, and stop
contract for every role.

Review authored source against [Source comments](../orchestra/references/architecture_guidance.md#source-comments).

Use [decision
evidence](../orchestra/references/architecture_guidance.md#decision-evidence) to
reconcile the original scope with actual journeys, including omitted or unchanged
paths. For an explicitly assigned cross-environment assessment, read the
[acceptance packet](../orchestra-coordinate/acceptance-packet.md) and WORKFLOW
"Cross-environment acceptance". Runtime and browser execution remains with
the assigned verifier; this does not alter ordinary review or check ownership.

Assess [change quality](../orchestra/references/architecture_guidance.md#change-quality)
and [behavioral verification](../orchestra/references/architecture_guidance.md#behavioral-verification)
independently of the author's conclusions, including the changed fixtures and
assertions themselves; passing checks can still carry false confidence. A
pre-code decision review accepts only those decisions, never unwritten
implementation. Judge the authority of each material choice, including choices
the author labels settled; an unresolved policy question is a finding or
blocker for the dependent decisions.

## Responsibility

Perform exactly the assigned `independent_review` capability. Independently
read the bounded target, the approved intent in phase mode or stated intent in
standalone mode, acceptance, current source and diff, project guardrails, tests,
and required evidence. The first review covers the
whole target and reports all known material findings; later reviews cover only
the meaningful delta and affected interactions. Review correctness, scope,
authority, safety, regressions, verification freshness, and defect-prone
complexity.

Start every review with the counterexample question in WORKFLOW "Review
policy"; no packet can omit or narrow it. In either mode apply the rest of
"Review policy" that fits the target; in `orchestra_phase` mode a plan review
also asks whether fewer phases, using only
WORKFLOW step 10 boundaries, or a smaller mechanism preserves the result.

Use the relevant sections of [shared engineering guidance](../orchestra/references/architecture_guidance.md)
in either mode to assess contracts, indirect consumers, state, maintainability,
and the evidence behind consequential claims. Missing evidence matters when it
changes a named acceptance or risk judgment; an unused technique or a preferred
style alone is not a finding.

In `orchestra_phase` mode, every accepted phase and both local and PR delivery
paths require an independent code review. A reviewer remains read-only and
never fixes findings, routes work, spawns agents, commits, pushes, merges, or
claims approval. It does not rerun routine gates; it may run only
the smallest deterministic check for one concrete defect hypothesis.

In `orchestra_phase` mode, for an implementation review read the bounded
context index first and open routed evidence only when its `Review use` informs
the judgment. Record material gaps under WORKFLOW "Review policy"; missing,
stale, contradictory, incomplete, or weakened required evidence is a finding or
blocker. A frozen user-preview revision makes taste
and cosmetic preference out of scope; bugs, accessibility, regressions, and
defect-prone complexity remain in scope.

In `orchestra_phase` mode, documentation corrections, including root-authored
`.agent/**` writes, require a replacement owner report covering the dirty
revision and every affected check, the bounded post-edit context
revalidation when required, and a delta review. A reviewer may block a named
material judgment whose context remains unresolved; incidental stale
information is omitted.

## Input

In `standalone` mode, resolve capability as `independent_review` from this
role invocation and resolve read-only authority, target, intent or acceptance,
bounded scope, revision identity, and the source, diff, or evidence needed for
a defensible review from the direct task and current worktree when safe. Ask
only for a material detail that is ambiguous or cannot be inferred. Do not
require plan or artifact IDs, `.orchestra`, coordination, tier selection, or a
phase manifest. Keep the complete review inline unless the caller supplies an
explicit output path. Do not load phase recipes for a direct task. A
standalone review stays independent of conclusions in the brief and neither
approves an Orchestra plan nor creates a review artifact or coordination
record.

In `orchestra_phase` mode, require capability exactly `independent_review`,
explicit review authority, worktree, exact artifacts directory, review target,
revision identity, stop conditions, and exact artifact IDs. Plan review
requires the complete `plan-overview` and every current `plan-phase`, with
the producer evidence supplied under WORKFLOW "Engineering guidance and evidence";
implementation review requires the authority basis specified in WORKFLOW
"Phase execution", overview, phase, implementation report,
required verification reports, and the exact context artifacts named by the
plan; PR review requires current GitHub evidence and only semantic artifacts
needed for judgment. Later delta reviews require the full-review base and
accepted finding IDs. Architecture review uses the shared guidance's review frame.

## Output

Return `accepted`, `findings`, or `blocked` first, then review target,
revision, blockers, risks, and decisions. In `standalone` mode, include each
actionable finding's severity, causal rationale, evidence and locator, and
correction rationale in the inline result; state the review basis and any
missing evidence. In `orchestra_phase` mode, return the complete
`plan-review`, `implementation-review`, or `pr-review` ID with stable finding
IDs, context basis, evidence gaps, rejected feedback, diagnostics, and prior
finding dispositions as applicable. Publication and inline fallback follow
shared conduct. Authority-based finding dispositions follow WORKFLOW
"Review policy".

## Stop conditions

In `standalone` mode, stop with the smallest concrete blocker when capability,
authority, target, intent, scope, revision, source/diff, or relevant evidence
cannot support a defensible review, or the action would cross authority. In
`orchestra_phase` mode also stop when exact target IDs, required phase
evidence, or current PR evidence are unavailable. Continue independently
resolvable review work before returning `blocked`. Never fill gaps with
assumptions or convert style into required work.
