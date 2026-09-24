# Lite coordinator consumption

Use this resource as the external coordinator, not as the worker. Read
[runtime resources](../orchestra/runtime.md) and WORKFLOW "Orchestra Lite
companion", especially "Lite coordinator acceptance" and "Result contract".
Those sections own the policy. Pin these instructions and the worker to the
same Orchestra revision. Updating a local bundle does not update a cloud
worker that still clones an earlier revision.

Prepare the [kickoff](kickoff-template.md) from the approved objective,
acceptance, exclusions and actual authority. For v2, explicitly send
`Versión: 2`. Resolve the repository and base, worker resources, check readiness,
PR owner and review route before launch. Shared Project Context paths can be
used for `Mapa` and `Reporte`; put their absolute resolution root in
`Decisiones` when using relative paths and verify recipient access. For a fresh
continuation, put the original baseline and expected branch SHA in `Decisiones`
as specified in WORKFLOW. Do not assume that an arbitrary VM-local absolute path is shared.

When useful, assign a bounded `repository_context` question through the existing
[analyst](../orchestra-role-analyst/SKILL.md), using the caller's selected
resources. Supply its revision-identified evidence to the worker. Otherwise the
worker establishes the applicable evidence itself. Neither choice adds a role,
requires a new artifact format or changes the user's model assignments.

Read the completed result once from the final message or `Reporte`, then apply
the version and status rules in WORKFLOW:

| Shape | Reference | Interpretation |
| --- | --- | --- |
| No `Versión`, exactly the valid v1 keys/types | [v1 example](result-v1-example.json) | Legacy delivery report; no v2 evidence or baseline guarantee; not acceptable for a v2 assignment. |
| Integer `Versión: 2` | [v2 example](result-example.json) | Versioned baseline, evidence and delivery report; independent acceptance still pending. |
| Anything else | WORKFLOW "Result contract" | Unsupported or malformed; reconcile the producer before consuming it. |

Use the [review packet](review-packet.md) for an independent review and assigned
remote checks. Read the actual findings and execution evidence before judging
acceptance. Return accepted corrections to the same worker and meaningful deltas
to the same reviewer. Recover existing handles on interruption; do not launch a
second writer to obtain a progress update. Report exact accepted revision,
remaining blockers and delivery state to the user. Completion does not confer
merge authority.
