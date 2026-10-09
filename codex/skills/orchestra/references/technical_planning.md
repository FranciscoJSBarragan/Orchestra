# Technical planning playbook

For direct role use, apply WORKFLOW "Standalone tools": keep the engineering
guidance below, but omit phase-only transport, artifact IDs, and formal plan
bundles. Return inline evidence or an explicitly requested output path.

For a delegated capability assignment, use this playbook with the `orchestra_analyst` profile and the
explicit `technical_planning` capability. A root that authors the plan under
WORKFLOW "Context and planning" step 9 applies the same plan-document rules in
`Contract` without dispatching a role; analyst role limits and dispatch
transport do not apply to it. Use the relevant sections of
[shared engineering guidance](architecture_guidance.md) to identify design
risks, consequential assumptions, and proportionate evidence in either mode.

Technical techniques may also be consulted in the caller's current workflow
under WORKFLOW "Modular engineering". Assignment-specific role limits, phase
artifacts and independent-gate rules apply when that assignment is selected;
reading this reference does not itself dispatch a role or grant authority.

Use [decision evidence](architecture_guidance.md#decision-evidence) to connect
consequential decisions and exceptions to the original scope. Reuse the context
result in `Review context` and assign missing evidence in `Verification`; do not
create a duplicate map artifact.
Use [behavioral verification](architecture_guidance.md#behavioral-verification)
to select proof from expected outcomes and material failure hypotheses. Reconcile
mandatory checks and optional diagnostics, and route material decision review
through WORKFLOW "Engineering guidance and evidence" before dependent implementation.

## Contract

- Read the named repository-context artifacts directly and convert that exact
  evidence into the smallest executable plan; do not ask the root to restate it
  or reopen settled product choices.
- Produce one complete `plan-overview` document and one complete `plan-phase`
  document per phase. Return their exact artifact identifiers as one candidate
  bundle; never make a consumer infer the current bundle from timestamps.
- The overview states objective, intended user-visible result, global
  constraints and acceptance, decisions, exclusions, phase order and
  dependencies, and the overall verification strategy. Carry quoted human
  authority unchanged under WORKFLOW "Local task plan"; the objective remains
  the author's labeled synthesis. State acceptance as observable outcomes.
  Keep user-selected mechanisms and binding contracts in constraints with
  their authority; proposed helpers and algorithms go in Decisions and test
  design in Verification. Corrections and consequence disclosure follow
  WORKFLOW "Autonomy within an approved objective" and "Context and planning".
- Every overview contains a `Review context` section: a bounded index naming
  the exact `repository-context` and `context-delta` artifact identifiers and
  revisions (or stable inline-fallback labels), the canonical source paths
  consulted, and only task-relevant facts. Each fact or coherent group carries
  `Review use` naming the acceptance, risk, invariant, exclusion, or phase
  dependency it informs. Do not copy cited evidence bodies.
- Map every planned test or check to an invariant, an observable acceptance
  journey, or a named regression risk. Avoid redundant or count-driven tests and
  tests coupled to implementation details that are not an approved contract.
- Where existing commands do not establish acceptance, put the missing parts
  of the shared guidance's verification recipe in the existing `Verification`
  section. Identify the evidence needed for applicable regression, stateful,
  or performance risks and assign it under the check-ownership rules below.
  A read-only planning pass distinguishes source-backed recipes from observed
  runs; it never claims execution from the presence of a command.
- Within each phase's existing `Verification` section, distinguish
  `Implementation handoff checks` from the `Independent verification gate`.
  Apply WORKFLOW "Delegated execution presets" when a preset is selected,
  including its terminal-check ownership and dedicated-gate reason. Otherwise
  assign every required local deterministic check to the implementation owner,
  including affected tests, lint, type checks, builds, validation commands,
  and the canonical full suite when one exists. Copy literal `.agent/` hard-gate
  commands into the selected gate. Cite in `Review context` the exact `.agent/`
  hard-gate and convention paths that bear on the change, and name in each
  phase the conventions it consumes, without pasting bodies. Descriptive
  recipe paths may be exact `Context maintenance paths`; normative policy and
  greenfield seeds follow WORKFLOW "Repository conventions", and nothing writes
  `.agent/` before plan approval. Set
  the independent gate to `none` for an ordinary deterministic non-critical
  phase without an execution-preset gate. Otherwise assign a verifier only for
  browser interaction, owned services or
  processes, mutable or stateful data, credentials, network or another external
  environment, explicit repository policy, or any critical phase. A critical
  phase requires the implementer to run its deterministic checks and an
  independent verifier to repeat the applicable gate. After fixes, require only
  affected reruns unless repository policy explicitly requires another full
  gate; configured delivery checks remain a separate final boundary.
- Define the fewest independently reviewable phases: default to one phase for
  ordinary work and two to three for a large task. Every additional phase must
  name one of the review boundaries defined in `docs/WORKFLOW.md` ("Context
  and planning", step 10), which also states what a phase costs and what does
  not count as a boundary; a split without one is format inflation. One
  outcome may group several independent acceptance criteria that share one
  owner capability and risk order; when no listed boundary applies, collapse
  the phases rather than inventing one or returning `blocked`. Each phase
  document is independently executable with a small
  mandatory core — one outcome, exact allowed scope, `Outcome invariants`,
  `State writers`, acceptance criteria, verification, and stop conditions —
  plus the structural declarations below. Other sections appear only when
  they carry material content; never invent content to satisfy a format.
- `Outcome invariants` state what must remain true from every reachable prior
  state, derived from the quoted user outcome, the specification's prior-state
  expectations and binding contracts, never from the chosen mechanism (for
  example: a total never exceeds its source, an operation is idempotent, a
  permission is never widened). An invariant that must hold under failures
  names the failures it covers; "under any failure" without that set is a
  plan-review finding. Each invariant maps
  to an existing or planned check: deterministic, verifier, or preview.
  Acceptance values follow from an invariant and the user's intent; a value
  only the mechanism justifies is not acceptance. Write `none beyond
  acceptance` with a reason when acceptance states the whole outcome. A stop
  condition names a conflict with an invariant or the required outcome.
- Start from the smallest design that meets the complete outcome and keeps
  existing behavior working, and name it in the overview. Add new
  infrastructure (locks, leases, file formats, markers, envelopes, migrations,
  registries or layers) only when that design cannot satisfy an outcome
  invariant, and name the invariant or reachable failure each addition
  serves; a hypothesized dependency misreport or hostile race is not one
  unless the outcome names it.
- `State writers` lists, for each persisted or shared value an outcome
  invariant constrains, the existing operations that write it, including
  other entry points, earlier steps and sequences that reach the changed
  operation. A writer whose resulting state could violate an invariant gets a
  check seeded through that real operation; others are dismissed in one line
  with cited evidence. Excluding an operation from edits never excludes the
  states it produces. Write `none` with a reason when no existing operation
  writes state an invariant depends on.
- Each phase names the exact review-context evidence it consumes and contains
  `Context maintenance paths`. Maintained documentation describes behavior,
  commands and limits, never task evidence such as dates, revisions, hashes
  or test counts. Use `none` unless an exact versioned
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
- The root decides whether the bundle needs independent review under WORKFLOW
  "Context and planning". Name concrete unresolved design risks, and propose an
  authorized experiment when it can settle an empirical question.
  Plan review follows the review order in WORKFLOW "Context and planning"
  step 11.
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
public or high-impact decision remains unresolved, or the work is too large for
one phase yet no WORKFLOW boundary separates it. Being able to fit the work in
one phase is never a blocker.

For reusable feature maps and recipe maintenance, use
[project verification](../../orchestra-project-verification/SKILL.md) and its
WORKFLOW lifecycle. Planning cites affected entries; verifiers execute their
assigned journeys and report stale instructions separately from product defects.
The selected role's source and execution authority remains unchanged.
