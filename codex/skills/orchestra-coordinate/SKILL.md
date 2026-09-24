---
name: orchestra-coordinate
description: Coordinate an explicitly requested initiative across independent projects, repositories, or task roots. Keep shared contracts, dependencies and combined acceptance in the parent while each child uses Orchestra, Orchestra Lite or the user's selected workflow. Does not activate from an ordinary multi-file change.
---

# Coordinate independent task roots

Read [runtime resources](../orchestra/runtime.md) and WORKFLOW "Initiative
coordination". That section owns authority, checkout ownership, dispatch,
recovery, and combined acceptance. This skill is explicit-only: a request to
coordinate independent projects or task roots is sufficient; merely mentioning
several folders is not. Use one task when ordinary phases address the work.

Keep the parent focused on the shared result. Identify the participating
repositories and their actual checkouts, applicable instructions, shared
contracts, ordering, and observable joint acceptance. Reuse the conversation's
approved scope and authority. Name only unresolved material choices to the user.
Do not collect implementation details from every repository into this context.

Prepare a compact initiative index at a caller-owned private path outside the
source trees, unless an existing task document already serves that consumer.
Use [the packet and index example](packet-example.md) as a shape, not a new
schema. It links the actual child plans/results and session handles; it never
duplicates their phase state or replaces Git, host state, or user authority.
Task Control cards may be linked when already in use; the Hub is optional.

Select a child route per responsibility:

- Full [Orchestra](../orchestra/SKILL.md) for a child needing its planned,
  independently reviewed phases. Carry the explicit activation, approved scope,
  tier and delivery bounds into its own root; do not make it a leaf implementer.
- [Orchestra Lite](../orchestra-lite/SKILL.md) for a fresh bounded cloud worker
  with its kickoff and external review contract. Respect its supported tiers
  and exact publication authority. Read its
  [coordinator instructions](../orchestra-lite/coordinator.md) from the same pinned
  revision as the worker. Lite cannot become a delegating child root.
- [Engineering](../orchestra-engineering/SKILL.md) or the user's custom flow for
  a bounded task that does not need Orchestra. State its review and completion
  expectations instead of silently certifying it as an Orchestra phase.

Use [host transports](host-transports.md) to dispatch supported task roots.
The leaf-role delegate is still appropriate for an independent review or other
bounded role; its no-commit/no-subagent contract cannot run a full child root.
Before parallel mutation, establish one writer per checkout and concrete
cross-repository contracts. Wait for a dependency's required revision or
evidence rather than relying on a child's optimistic progress description.

At stable handoff, consume the child's compact result once: exact revision,
acceptance and review evidence, unresolved issues, delivery state, and owned
resource cleanup. Run the combined journey against the actual set of revisions.
If integration exposes a local defect before delivery, send the same child a
focused delta and recheck affected evidence. After delivery, follow WORKFLOW's
new bounded repair-task rule from the delivered base. Do not repeat an unchanged child's code review.

On interruption, recover existing handles before dispatching again. Keep a
blocked child's question separate from independent work that can continue.
Return the joint result, actual child revisions, combined evidence, limitations,
and delivery state. Do not claim initiative completion merely because every
child reported success.
