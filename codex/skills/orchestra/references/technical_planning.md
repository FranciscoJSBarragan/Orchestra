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
- Map every planned test or check to an observable acceptance journey or a
  named regression risk. Do not add duplicated coverage, count-driven tests,
  or tests coupled to implementation details unless those details are an
  approved contract.
- Define the fewest independently reviewable phases. Each phase document must
  be independently executable and state one outcome, its relationship to the
  overview, preconditions and dependencies, exact allowed scope, required
  behavior, acceptance criteria, verification, outputs consumed by later
  phases, material risks, exclusions, and stop conditions.
- Preserve cross-phase invariants and assign one implementation owner per phase. Split frontend and non-frontend work only when ownership cannot remain safely bounded.
- Identify assumptions and unresolved authority decisions explicitly. Do not
  silently convert them into implementation choices. A persisted type, schema
  version, API contract, signature, transaction or invariant, downstream
  consumer, migration requirement, fixture, or canonical verification command
  that determines feasibility must be direct evidence, not an executable-plan
  assumption.
- Include execution readiness in the phase that consumes it: runtime,
  dependencies, services, permissions, credential categories, test-data source
  and reset, commands, and generated paths. Add a preparation phase only when
  current evidence demonstrates that the task needs one.
- Expect the root to decide whether the complete candidate bundle needs
  independent review. A trivial single-phase Luna or standard bundle may skip it;
  non-trivial multi-phase or cross-component bundles require one review, and a
  critical bundle requires a review focused on its named measurable risk.
- Remain available while a dispatched plan review is active. Read the exact
  `plan-review` artifact and accepted finding identifiers, then publish complete
  replacement overview or phase documents only for affected members. Return a
  new complete bundle mapping and identify every replacement; do not publish a
  patch that forces later consumers to reconstruct a phase.
- Use only the context delta supplied by the root in addition to named
  artifacts. Write each publication directly to the task-private artifacts
  directory (`git rev-parse --git-path orchestra/artifacts`): the overview as
  the next `<NN>-plan-overview.md` file and each phase as
  `<NN>-plan-phase-p<number>.md`. If the directory cannot be created or
  written, return the same complete documents inline.
- Return the candidate bundle to the root for review and user approval. Only
  the root writes or updates the approved overview and exact phase manifest at
  `git rev-parse --git-path orchestra/plan.md`.

Return `blocked` when evidence is insufficient, a feasibility-determining fact
is unresolved, scope is materially ambiguous, canonical sources conflict, a
public or high-impact decision remains unresolved, or no proportional phase
boundary can be defended.
