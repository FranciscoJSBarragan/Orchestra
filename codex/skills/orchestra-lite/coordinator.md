# Lite coordinator consumption

Use this resource as the external coordinator, not as the worker. Read
[runtime resources](../orchestra/runtime.md) and WORKFLOW "Orchestra Lite
companion", especially "Lite coordinator acceptance" and "Result contract".
Those sections own the policy. Pin these instructions and the worker to the
same Orchestra revision. Updating a local bundle does not update a cloud
worker that still clones an earlier revision.
For disposable remote environments, use runtime resources' "Prepared remote
source" before worker launch when a source checkout is selected. Verify the
returned revision and supply its absolute roots to each consumer.

Apply WORKFLOW "Conversation continuity" throughout the assignment, including
worker commentary and user questions while waiting. Consume a completed handoff
under "Engineering guidance and evidence"; a short summary is not the complete
analysis and an intermediate update is not a failed or finished worker.

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

Use [decision evidence](../orchestra/references/architecture_guidance.md#decision-evidence)
to make the consequential acceptance criterion explicit. Apply WORKFLOW
"Engineering guidance and evidence" before writer launch: reconcile mandatory
checks and environment readiness, and obtain a bounded decision review when
required. Record settled decisions and their evidence in the existing kickoff;
do not ask an implementer or reviewer to guess missing product policy.
The kickoff's [decision examples](kickoff-template.md#decision-handoff) identify
authority and superseded recommendations without replacing facts or residual
risks. Reuse applicable decision-review evidence and name its reviewed revision;
an unresolved material policy question prevents dependent writer launch.

Read the completed result once from the final message or `Reporte`, then apply
the version and status rules in WORKFLOW:

| Shape | Reference | Interpretation |
| --- | --- | --- |
| No `Versión`, exactly the valid v1 keys/types | [v1 example](result-v1-example.json) | Legacy delivery report; no v2 evidence or baseline guarantee; not acceptable for a v2 assignment. |
| Integer `Versión: 2` | [v2 example](result-example.json) | Versioned baseline, evidence and delivery report; independent acceptance still pending. |
| Anything else | WORKFLOW "Result contract" | Unsupported or malformed; reconcile the producer before consuming it. |

Check the actual object's keys, types and status implications, not just its
`Estado`. Under the v2 contract a success with a null or nonzero check exit code
is inconsistent and needs producer reconciliation; it is not accepted because
other tests passed. Compare the executed checks with the required set and the
claimed tree, inspecting referenced evidence. Optional unexecuted diagnostics
are reported in `Riesgos / no hecho`; moving an unavailable required gate there
does not discharge it. Canonical source conformance checks shipped examples,
not this live report. For an explicitly authorized exception, require the
requirement, authority, reason and limits in `Decisiones tomadas` and the
unverified behavior in `Riesgos / no hecho`, per WORKFLOW. Compare against the
remaining required set; the exception is not a passing check or a waiver of
independent acceptance. Resolve other omissions rather than accepting a green
subset or retroactively weakening acceptance.

Use the [review packet](review-packet.md) for an independent review and assigned
remote checks. Read the actual findings and execution evidence before judging
acceptance. Return accepted corrections to the same worker and meaningful deltas
to the same reviewer. Recover existing handles on interruption; do not launch a
second writer to obtain a progress update. Report exact accepted revision,
remaining blockers and delivery state to the user. Completion does not confer
merge authority.

Apply WORKFLOW "Review policy" to suggested findings before delivery: classify
their impact and return accepted in-scope fixes to the same worker, with the
affected verification and delta review. Cheap edits are not automatically
required, and documentation or test edits are not automatically review-exempt.
