# Technical planning playbook

An `orchestra_analyst` given the `technical_planning` capability uses this
playbook, and so does a root that writes the plan itself; analyst role limits
and dispatch transport do not apply to the root. Use
[decision evidence](architecture_guidance.md#decision-evidence) for
consequential decisions and exceptions and
[behavioral verification](architecture_guidance.md#behavioral-verification) to
choose proof from expected outcomes and material failure hypotheses.

## Size the plan to the outcome

- Read the named context artifacts directly and write the smallest executable
  plan that meets the complete confirmed outcome and keeps existing behavior
  working. Do not reopen settled product choices or ask the root to restate
  evidence.
- Name that smallest design in the overview and check it against
  [design from the consumer](architecture_guidance.md#design-from-the-consumer),
  including its rule against a second way, owner or hand-synced list. Add
  infrastructure (locks, leases, file formats, markers, manifests, envelopes,
  migrations, registries, process supervision or layers) only when it cannot
  satisfy an outcome invariant, and name the invariant or reachable failure
  each addition serves.
  A hypothesized dependency misreport or hostile race is not one unless the
  outcome names it.
- Every requirement cites its origin next to it: the quoted user words, a
  confirmed acceptance point, a binding contract, existing behavior
  (`file:line`) the change must keep, or security, privacy or data integrity.
  An invariant, behavior-constraining decision, acceptance value or check
  without one is not a requirement: drop it. A value only the chosen mechanism
  justifies is not acceptance.
- Default to one phase; a large task may need two or three. Each extra phase is
  a full serial cycle (fresh owner, handoff checks, any verifier, one review,
  teardown, commit) and names the boundary it buys: later work depends on a
  reviewed commit; one owner cannot safely cover the whole; required preview
  needs a reviewed commit before inspectable work; or risk order differs
  materially (a migration versus its UI). Distinct areas, files, cleaner
  commits or separate reviewability are not boundaries; the limit is a diff
  reviewable in one pass, and separately shippable changes are separate
  tasks. Without a boundary, collapse the phases.
- Write each fact once, where its consumer reads it. Mandatory sections are
  listed below; any other section appears only with material content. Never
  invent content to fill a format or copy cited evidence bodies.

## Documents

Return one complete `plan-overview` and one complete `plan-phase` per phase as
one bundle of exact artifact identifiers; a consumer never infers the bundle
from timestamps.

The overview states the objective (your labeled synthesis), the quoted human
authority you received, unchanged, the intended user-visible result,
constraints (user-selected mechanisms and binding contracts with their
authority), acceptance as observable outcomes, decisions (proposed helpers and
algorithms), exclusions, the smallest design, phase order and dependencies, the
verification strategy and risks. Its `Review context` indexes the exact
`repository-context` and `context-delta` identifiers and revisions (or inline
labels), the canonical source paths and the exact `.agent/` hard-gate and
convention paths that bear on the change, and only task-relevant facts, each
with the `Review use` (acceptance, risk, invariant, exclusion or phase
dependency) it informs.

Each phase is independently executable and contains:

- one outcome and the exact allowed scope, including any versioned document
  that describes runtime, exposure, supported environments, commands or
  user-visible behavior the phase changes;
- context dependencies: the exact review-context evidence and `.agent/`
  conventions it consumes;
- `Outcome invariants`: what must remain true from every reachable prior state,
  derived from the outcome, the specification's prior-state expectations and
  binding contracts, never from the chosen mechanism (a total never exceeds its
  source; an operation is idempotent; a permission is never widened). Each
  cites its origin and maps to an existing or planned deterministic, verifier
  or preview check; one that must hold under failures names those failures.
  Write `none beyond acceptance` with a reason when acceptance states the
  whole outcome;
- `State writers`: for each persisted or shared value an invariant constrains,
  the existing operations that write it, including other entry points, earlier
  steps and sequences reaching the changed operation, not state your design
  introduces. A writer whose result could violate an invariant gets a check
  seeded through that real operation; dismiss the others in one line with
  cited evidence. Excluding an operation from edits never excludes the states
  it produces. Write `none` with a reason when no existing operation writes such
  state;
- acceptance criteria; execution readiness when material (runtime,
  dependencies, services, permissions, credential categories, test-data source
  and reset, commands, generated paths);
- `Verification`, split as below;
- `Context maintenance paths`: `none` unless an exact versioned human-readable
  documentation path is a named consumer of this or an identified later
  phase; exact repository-relative paths, never globs or directories;
- `User preview: required | none`: `required` only when the task-level
  Decision is `required`, the phase has a user-visible surface and it names an
  executable local preview recipe;
- stop conditions, each naming a conflict with an invariant or the required
  outcome.

## Verification

- Map every test or check to an invariant, an observable acceptance journey or
  a named regression risk. No redundant or count-driven tests, and none
  coupled to implementation details that are not an approved contract.
- Where existing commands do not establish acceptance, add the missing recipe
  parts and the evidence for applicable regression, stateful or performance
  risks. Reconcile mandatory checks with optional diagnostics. A read-only
  planning pass distinguishes source-backed recipes from observed runs.
- Split `Implementation handoff checks` from the `Independent verification
  gate`. With a selected execution preset, apply its terminal-check ownership
  and dedicated-gate reason (WORKFLOW "Delegated execution presets").
  Otherwise the implementation owner runs every required local deterministic
  check: affected tests, lint, type checks, builds, validation commands and the
  canonical full suite when one exists. Copy literal `.agent/` hard-gate
  commands into the selected gate.
- The independent gate is `none` for an ordinary deterministic non-critical
  phase. Assign a verifier only for browser interaction, owned services or
  processes, mutable or stateful data, credentials, network or another
  external environment, explicit repository policy, or a critical phase, where
  the implementer runs its deterministic checks and the verifier repeats the
  applicable gate. After fixes, require only affected reruns unless repository
  policy requires another full gate; configured delivery checks stay a
  separate final boundary.

## Ownership, documentation and assumptions

- One implementation owner per phase; preserve cross-phase invariants. Split
  frontend and non-frontend work only when ownership cannot stay bounded. With
  required preview, commit non-visible work before the inspectable phase and
  prefer fewer UI phases.
- Maintained documentation describes behavior, commands and limits, never task
  evidence such as dates, revisions, hashes or test counts. A listed
  maintenance path authorizes a correction only after a validated
  `descriptive` discovery and a root `persist` disposition. Descriptive
  `.agent/` recipe paths may be maintenance paths; normative policy and
  greenfield seeds follow WORKFLOW "Repository conventions", and nothing writes
  `.agent/` before plan approval. Executable configuration, databases,
  generated and operational data remain normal implementation scope.
- State assumptions and unresolved authority decisions; never turn them into
  implementation choices. A fact that determines feasibility (persisted type,
  schema version, API contract, signature, transaction or invariant,
  downstream consumer, migration requirement, fixture, canonical verification
  command) needs direct evidence. Any other assumption is checked at the start
  of its consuming phase; add a preparation phase only when evidence shows the
  task needs one.
- Name concrete unresolved design risks for the root's review decision and
  propose an authorized experiment when one can settle an empirical question.

## Revisions and publication

- During plan review, remain available. Read the exact `plan-review` and the
  accepted finding identifiers, publish complete replacements only for affected
  members and return the new complete bundle mapping naming each replacement.
  A validated context delta that changes a later phase's evidence gets a
  complete replacement of that phase; never widen `Context maintenance paths`
  silently.
- Use only the named artifacts and the context delta the root supplies. Write
  to the packet's artifacts directory, normally `<worktree>/.orchestra/artifacts`,
  as the next `<NN>-plan-overview.md` and `<NN>-plan-phase-p<number>.md`; if it
  cannot be written, return the same complete documents inline. Only the root
  writes the approved plan at the plan path, normally
  `<worktree>/.orchestra/plan.md`.

Return `blocked` when evidence is insufficient, a feasibility-determining fact
is unresolved, scope is materially ambiguous, canonical sources conflict, a
public or high-impact decision remains unresolved, or the work is too large for
one phase yet no boundary separates it. Fitting the work in one phase is never
a blocker.

For reusable feature maps and recipe maintenance, use
[project verification](../../orchestra-project-verification/SKILL.md); planning
cites affected entries.
