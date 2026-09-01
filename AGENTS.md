# Orchestra Agent Rules

`docs/WORKFLOW.md` is the canonical home for every operational rule. This file
names what is required and where the mechanism is specified; it does not
restate mechanics. When this file and `docs/WORKFLOW.md` appear to disagree,
`docs/WORKFLOW.md` wins.

## Product source of truth

Read `VISION.md`, `docs/WORKFLOW.md`, and `docs/ARCHITECTURE.md` before changing
Orchestra's workflow. Skills, scripts, profiles, tests, and hooks implement those
documents; they do not redefine them independently. Each normative rule has
exactly one home; other documents reference it instead of restating it.

## Language

- User-facing communication is concise, practical Spanish.
- Code, comments, commits, plans, prompts, profiles, schemas, and internal docs
  are English.

## Activation

Orchestra is an explicit planned-work route, not the default implementation
route: it activates only via `$orchestra` or an unequivocal imperative to
use or start Orchestra, while ordinary plan requests, descriptive mentions,
and direct fixes stay outside it. A planning-only host mode reuses the
conversation, pauses before task setup, and later continues without a second
invocation; Orchestra observes the host mode and never changes it.
`orchestra-project-start` may activate implicitly for a greenfield idea but
never activates the full workflow without an explicit user choice. Details:
`docs/WORKFLOW.md` ("Activation and specification gate").

## Root orchestrator

The root owns specification alignment, tier recommendation, capability
routing, compact synthesis, blocker resolution, the local plan, phase commits,
and final technical judgment. It follows the autonomy policy in
`docs/WORKFLOW.md` ("Autonomy within an approved objective"): within an
approved objective it makes reversible in-scope decisions without re-asking
and stops only at the hard gates named there. The user chooses the active tier
and remains the final authority. Tier semantics, host matrices, checkout and
branch rules, agent flow, phase execution, review policy, delivery, and
browser/permission routing are all specified in `docs/WORKFLOW.md`; do not
duplicate them here or in skills.

## Anti-overengineering rules

- One canonical source for each fact.
- One canonical validator; hooks and CI only invoke it.
- No persisted artifact without a named consumer and lifecycle.
- No new state machine, lock, transaction layer, or schema when Git, GitHub, or
  a simple result object already provides the required truth.
- No whole-workflow restart for a local step failure.
- No repeated discovery when a targeted context delta is sufficient.
- New domain guidance is an internal capability playbook or role skill unless
  it requires a genuinely different responsibility boundary.
- No authoritative plan CLI, Kanban board, event ledger, benchmark control
  plane, or workflow state engine.
- Every test proves observable acceptance or a named regression risk; tests pin
  structure and invariants, never prose wording.
- Prefer deletion and direct code over compatibility layers.

Before accepting a mechanism, name its consumer, the demonstrated failure or
reproducible risk it addresses, why an existing primitive is insufficient, its
lifecycle and cleanup, and why a smaller direct implementation does not
suffice. Prompts state outcomes, invariants, authority, and stop conditions
while leaving ordinary technical judgment to the capable agent.
