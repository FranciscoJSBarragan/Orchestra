# Orchestra

This is the clean, Codex-only foundation for Orchestra. It records the product
intent agreed with the user before implementation begins.

The repository currently contains only its canonical product and architecture
documents. No Orchestra runtime is implemented or installed from this source.
The former multi-platform implementation is preserved at
`/Users/fjsbarragan/Code/Orchestra-legacy`.

## Product statement

Orchestra is a cost-efficient, quality-focused multi-agent software delivery
workflow for individual developers and small projects. Its orchestrator is an
active technical lead: it understands the request, resolves ordinary technical
problems, delegates proportionally, verifies outcomes, and brings an approved
plan to completion without turning routine work into process ceremony.

Codex is the only target for the rebuild. Hermes, Devin, and other harnesses
remain in the legacy repository until the user decides that the Codex product
is mature enough to port.

## Canonical document order

The repository uses this precedence when interpreting product intent:

1. `VISION.md` — mission, audience, principles, success, and non-goals.
2. `docs/WORKFLOW.md` — expected behavior from request through delivery.
3. `docs/ARCHITECTURE.md` — component and role boundaries.
4. `AGENTS.md` — concise executable rules for agents.
5. Skills, profiles, scripts, tests, and hooks — implementations of the above.

Lower levels must not silently redefine higher levels. A deliberate product
change updates the relevant canonical document and its executable enforcement
in the same change.

## Agreed decisions

- Codex-first clean-room rebuild in a fresh Git repository.
- Preserve the current repository as `Orchestra-legacy` with full history.
- Keep subagents by default, scaled by task tier.
- Let the orchestrator think, decide, diagnose, and adapt inside approved scope.
- Ask the user for destructive, production, product, public-contract, or
  materially scope-expanding decisions.
- Use the fewest coherent implementation phases.
- Commit automatically after each verified and reviewed phase.
- Support local integration and PR delivery; do not require PRs universally.
- Preserve the proven behavior of `commitbot`, `openprbot`, `prbot`, and
  `prmerge`, adapted behind Orchestra naming and thin contracts.
- Spend tokens on context, implementation, debugging, tests, and meaningful
  review—not on repeated Git authority ceremonies.
- Keep specialized agent profiles with role-specific prompts.
- Use one canonical validator; hooks may invoke it but must not duplicate it.
- The user decides when the Codex version is mature enough for future ports.

## Current status and next step

- The legacy repository, WIP branch, final tag, Git bundle, and installed-runtime
  backup are preserved.
- Legacy Orchestra skills and profiles are quarantined, not deleted.
- The clean repository has fresh Git history and no implementation code.
- Codex should reload its runtime inventory before implementation planning.

The next task inspects candidate legacy assets read-only, classifies each as
`reuse`, `adapt`, `reference`, or `reject`, and produces the smallest coherent
formal implementation plan. It must not install a runtime or mutate production.

## Documentation boundary

These documents are sufficient to plan the rebuild without relying on the
original conversation or on the legacy Orchestra skill. Implementation changes
must keep them aligned rather than creating a second undocumented workflow.
