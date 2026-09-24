---
name: orchestra-repo-maintenance
description: Diagnose or repair harmful code patterns, misleading documentation, obsolete instructions and low-signal tests when the user explicitly requests repository maintenance, test-suite cleanup, an audit or deslop. Excludes folder reorganization and ordinary unrelated cleanup.
---

# Maintain a repository

Read [runtime resources](../orchestra/runtime.md). WORKFLOW "Repository
maintenance" owns scope, delegation and review; "Repository conventions" owns
policy changes. Use shared guidance for [source comments](../orchestra/references/architecture_guidance.md#source-comments),
[prevention](../orchestra/references/architecture_guidance.md#prevent-recurring-failures)
and [maintenance evidence](../orchestra/references/architecture_guidance.md#maintain-patterns-and-knowledge).
The source-comment policy applies to every authored source change.

For suite audits or cleanup, use [test maintenance](../orchestra/references/architecture_guidance.md#test-maintenance)
and [behavioral verification](../orchestra/references/architecture_guidance.md#behavioral-verification).
Return the evidence for keeping, repairing, consolidating, replacing or removing
candidates in the existing output. Test cleanup does not grant authority to
change repository gates or update global agent instructions.

Resolve diagnosis or authorized repair from the request. Do not turn a request
for findings into edits or activate the full Orchestra workflow. Establish the
requested area, actual consumers and baseline evidence. Prioritize patterns that
future agents will copy or execute and whose harm can be demonstrated. Inspect
what the assignment needs; do not enforce a universal audit or finding quota.

For diagnosis, return the candidate's location, consequence, evidence and useful
correction. Distinguish observed behavior, inference and unresolved consumers.
Include examined, sampled and unexamined scope. A healthy area needs no change.

For repair, keep each coherent problem's code, tests, examples and instructions
together. Use [engineering](../orchestra-engineering/SKILL.md) in the selected
workflow and preserve independent implementation review. Investigate existing
comments before removal, preserve valid constraints, and improve the supported
path rather than merely deleting its explanation. Existing review/test evidence
can guide prevention; do not infer permission to rewrite governing policies.

Use [project verification](../orchestra-project-verification/SKILL.md) when a
missing runnable journey or tool is needed to establish acceptance. Record old
failures separately. Validate the affected behavior and any new preventive check
against both a bad and valid case. No-reference searches do not prove that code,
a dependency or a rule is unused or obsolete.

Delegate only independent modules or hypotheses when proportional and supported
by the caller. Give each repair one owner across artifact types, avoid overlapping
writers and receive compact results through existing completion-aware waiting.
The root resolves shared-policy decisions and retains final judgment. Do not
create a second coordinator, fixed reviewer panel or persistent audit database.

Return changes or findings, evidence, remaining risks and coverage in the user's
existing output form. Do not reorganize folders, make cosmetic renames, sweep
formatting or upgrade dependencies incidentally. Preserve unique knowledge and
unrelated work; remaining material candidates are follow-up proposals.
