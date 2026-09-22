---
name: orchestra-engineering
description: Apply proportional engineering practices when investigating software behavior, designing a change, implementing a feature or fix, or assessing technical evidence. Supports the user's current workflow without starting Orchestra or delegating work implicitly.
---

# Engineering in the current workflow

Read [runtime resources](../orchestra/runtime.md) once. Use the relevant parts
of [shared engineering guidance](../orchestra/references/architecture_guidance.md).
WORKFLOW "Modular engineering" owns activation, composition, and authority.

Keep the user's requested outcome and execution route. An explanation stays
read-only; an authorized implementation may investigate, experiment, implement,
and check its result without converting each activity into a separate role.
A typo normally needs only its diff and affected links inspected. Do not load
the full workflow, create task state, choose a tier, or require a report format.

Select only the material question:

| Need | Resource and result |
| --- | --- |
| Understand behavior or rationale | Shared guidance, "Understand the system": trace the relevant path and distinguish recorded intent from inference. |
| Choose an interface or uncertain approach | Shared guidance, "Design from the consumer" and "Resolve uncertainty experimentally": a caller example or bounded experiment that informs the decision. |
| Fix a defect | Shared guidance, "Evidence for consequential changes"; use [difficult debugging](../orchestra/references/difficult_debugging.md) for competing hypotheses or repeated failed corrections. |
| Improve performance | Shared guidance, "Performance evidence": comparable measurement and, where useful, a runtime profile or trace. |
| Exercise the product | Reuse the repository's verification entry; use [project verification](../orchestra-project-verification/SKILL.md) when creating, running, refreshing, or auditing that knowledge is the requested work. |
| Assess a change independently | [Reviewer role](../orchestra-role-reviewer/SKILL.md), only for a genuinely independent assignment. Self-checking is not independent review. |

Role skills remain useful bounded assignments when the caller selects one.
Their responsibility limits still apply. Reading a technical reference does not
grant another role's edit or delegation authority. If additional independent
work is justified, use the caller's established delegation and review route.

Return the result, supporting evidence, and material uncertainty in the user's
preferred form. Do not narrate which principles were loaded. Reuse exact paths
and evidence instead of copying earlier context. Installation makes this skill
discoverable; it is not proof that every host or task has selected it.
