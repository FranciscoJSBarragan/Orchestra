# Technical planning playbook

Use this internal playbook only with the `analyst` profile and the explicit `technical_planning` capability. Also apply [architecture guidance](architecture_guidance.md) when the packet names architecture or cross-component design.

## Contract

- Convert the root's settled objective and bounded evidence into the smallest executable plan; do not reopen settled product choices.
- Define the fewest independently reviewable phases. Each phase must state one outcome, exact allowed scope, acceptance criteria, verification, dependencies, material risks, and stop conditions.
- Preserve cross-phase invariants and assign one implementation owner per phase. Split frontend and non-frontend work only when ownership cannot remain safely bounded.
- Identify assumptions and unresolved authority decisions explicitly. Do not silently convert them into implementation choices.
- Recommend an extra critical plan review only for a named measurable risk, supporting evidence, affected area, and independently detectable defect class.
- Return the plan to the root. The root alone writes and updates the local plan at `git rev-parse --git-path orchestra/plan.md`.

Return `blocked` when evidence is insufficient, scope is materially ambiguous, canonical sources conflict, a public or high-impact decision remains unresolved, or no proportional phase boundary can be defended.
