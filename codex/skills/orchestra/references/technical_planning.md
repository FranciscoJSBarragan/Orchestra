# Technical planning playbook

Use this internal playbook only with the `orchestra_analyst` profile and the explicit `technical_planning` capability. Also apply [architecture guidance](architecture_guidance.md) when the packet names architecture or cross-component design.

## Contract

- Convert the root's settled objective and bounded evidence into the smallest executable plan; do not reopen settled product choices.
- Define the fewest independently reviewable phases. Each phase must state one outcome, exact allowed scope, acceptance criteria, verification, dependencies, material risks, and stop conditions.
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
- Recommend an extra critical plan review only for a named measurable risk, supporting evidence, affected area, and independently detectable defect class.
- Return the plan to the root for review and user approval. Before approval it remains in conversation or system temporary storage; only the root writes the approved plan directly as `active` at `git rev-parse --git-path orchestra/plan.md`.

Return `blocked` when evidence is insufficient, a feasibility-determining fact
is unresolved, scope is materially ambiguous, canonical sources conflict, a
public or high-impact decision remains unresolved, or no proportional phase
boundary can be defended.
