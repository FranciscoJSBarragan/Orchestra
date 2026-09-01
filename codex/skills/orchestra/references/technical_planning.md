# Technical planning playbook

Use this internal playbook only with the `orchestra_analyst` profile and the explicit `technical_planning` capability. Also apply [architecture guidance](architecture_guidance.md) when the packet names architecture or cross-component design.

## Contract

- Read the named repository-context artifacts directly and convert that exact
  evidence into the smallest executable plan; do not ask the root to restate it
  or reopen settled product choices.
- Produce one complete `plan-overview` document and one complete `plan-phase`
  document per phase. Return their exact artifact identifiers as one candidate
  bundle; never make a consumer infer the current bundle from timestamps.
- The overview states objective, intended user-visible result, global
  constraints and acceptance, decisions, exclusions, phase order and
  dependencies, and the overall verification strategy.
- Every overview contains a `Review context` section. It names the exact
  `repository-context` and `context-delta` artifact identifiers and inspected
  revisions, or a stable label and revision for each complete inline fallback;
  the canonical source paths consulted; and only the task-relevant
  architecture, runtime, exposure, persistence, user-visible surface, primary
  risks, invariants, and exclusions. For each included fact or coherent group,
  add `Review use` naming the exact acceptance, risk, invariant, exclusion, or
  phase dependency it informs. Omit anything without a current-task use and do
  not copy cited evidence bodies. Treat the section as a bounded index.
- Map every planned test or check to an observable acceptance journey or a
  named regression risk. Do not add duplicated coverage, count-driven tests,
  or tests coupled to implementation details unless those details are an
  approved contract.
- Within each phase's existing `Verification` section, distinguish
  `Implementation handoff checks` from the `Independent verification gate`.
  Assign every required local deterministic check to the implementation owner,
  including affected tests, lint, type checks, builds, validation commands,
  and the canonical full suite when one exists. Copy literal `.agent/` hard-gate
  commands into `Implementation handoff checks` and cite those `.agent/` paths
  in `Review context`. Never put `.agent/` in `Context maintenance paths`. A
  greenfield first plan records the seed Decision in `plan.md`; the first phase
  names those exact `.agent/` paths in its scope and outputs; the first-phase
  review packet must cite the exact `.agent/` seed paths. Do not write `.agent/`
  before plan approval. Set
  the independent gate to `none` for an ordinary deterministic non-critical
  phase. Assign a verifier only for browser interaction, owned services or
  processes, mutable or stateful data, credentials, network or another external
  environment, explicit repository policy, or any critical phase. A critical
  phase requires the implementer to run its deterministic checks and an
  independent verifier to repeat the applicable gate. After fixes, require only
  affected reruns unless repository policy explicitly requires another full
  gate; configured delivery checks remain a separate final boundary.
- Define the fewest independently reviewable phases: default to one phase for
  ordinary work and two to three for a large task. Every additional phase must
  name the independent review boundary it buys; a split without one is format
  inflation. Each phase document is independently executable with a small
  mandatory core — one outcome, exact allowed scope, acceptance criteria,
  verification, and stop conditions — plus the structural declarations below.
  Preconditions, dependencies, later-phase outputs, risks, and exclusions
  appear only when they carry material content: an empty risks section is a
  sign of a well-bounded plan, and no section is ever filled with invented
  content to satisfy a format.
- Each phase names the exact review-context evidence it consumes and contains
  `Context maintenance paths`. Use `none` unless an exact versioned
  human-readable documentation path is already a named current-phase or
  identified later-phase consumer; list only exact repository-relative paths
  and never use glob metacharacters or directory-wide authority. A listed path
  authorizes correction only after a validated `descriptive` discovery and
  an explicit root `persist` disposition. Executable configuration,
  databases, generated data, and operational data remain normal implementation
  scope.
- Preserve cross-phase invariants and assign one implementation owner per phase. Split frontend and non-frontend work only when ownership cannot remain safely bounded. When the task-level User preview Decision is `required`, split mixed API and UI work so non-visible work commits before the inspectable phase, and prefer fewer UI phases.
- Each phase declares `User preview: required | none`. Mark `required` only when that Decision is `required`, the phase has a user-visible surface, and the phase names an executable local preview recipe.
- Identify assumptions and unresolved authority decisions explicitly. Do not
  silently convert them into implementation choices. A persisted type, schema
  version, API contract, signature, transaction or invariant, downstream
  consumer, migration requirement, fixture, or canonical verification command
  that determines feasibility must be direct evidence, not an executable-plan
  assumption. An assumption that does not determine feasibility may instead be
  verified by a named check at the start of the phase that consumes it; do not
  create a preparation phase or block planning for it.
- Include execution readiness in the phase that consumes it: runtime,
  dependencies, services, permissions, credential categories, test-data source
  and reset, commands, and generated paths. Add a preparation phase only when
  current evidence demonstrates that the task needs one.
- Expect the root to decide whether the complete candidate bundle needs
  independent review. A single-phase non-critical bundle may skip it;
  non-trivial multi-phase or cross-component bundles require one review, and a
  critical bundle requires a review focused on its named measurable risk. A
  plan-review mandate asks first whether fewer phases or a smaller mechanism
  preserves the approved result.
- Remain available while a dispatched plan review is active. Read the exact
  `plan-review` artifact and accepted finding identifiers, then publish complete
  replacement overview or phase documents only for affected members. Return a
  new complete bundle mapping and identify every replacement; do not publish a
  patch that forces later consumers to reconstruct a phase.
- When a validated context delta changes evidence consumed by a later phase,
  publish a complete replacement for that phase with the new exact dependency.
  Do not silently widen `Context maintenance paths`; use the same replacement
  and approval rules as any other authority change.
- Use only the context delta supplied by the root in addition to named
  artifacts. Write each publication directly to the exact task-private
  artifacts directory supplied by the packet, normally
  `<worktree>/.orchestra/artifacts`: the overview as
  the next `<NN>-plan-overview.md` file and each phase as
  `<NN>-plan-phase-p<number>.md`. If the directory cannot be created or
  written, return the same complete documents inline.
- Return the candidate bundle to the root for review and user approval. Only
  the root writes or updates the approved overview and exact phase manifest at
  the plan path supplied by the root, normally `<worktree>/.orchestra/plan.md`.

Return `blocked` when evidence is insufficient, a feasibility-determining fact
is unresolved, scope is materially ambiguous, canonical sources conflict, a
public or high-impact decision remains unresolved, or no proportional phase
boundary can be defended.
