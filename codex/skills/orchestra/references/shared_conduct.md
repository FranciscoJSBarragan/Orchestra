# Shared agent conduct

Before any authorized source write, apply [Source comments](architecture_guidance.md#source-comments).
This applies even when no other engineering section is relevant; it never grants
write authority to a read-only role.

Every Orchestra role reads this contract before its role skill. It supplies
the common assignment, authority, evidence, cleanup, report, and stop rules;
role skills add only capability-specific behavior.

## Operating-mode router

Classify the invocation before reading role-specific inputs. An invocation is
`orchestra_phase` when the caller explicitly identifies an activated Orchestra
assignment, including context or planning before plan approval, or supplies a
formal Orchestra packet. Otherwise it is a `standalone` direct task. Do not
infer the mode from whether identifiers happen to be present. A role skill
invocation never activates the full Orchestra workflow, creates a checkout,
selects a tier or model, or starts a coordinator.

In `standalone` mode, use the direct brief relevant to the requested operation:
target, intent, bounded scope or allowed paths, revision identity, and the
evidence or acceptance basis needed for that operation. Resolve those details
from the user's task and current worktree when safe; ask only for a material
detail that cannot be inferred. Do not require or invent `plan-overview`,
`plan-phase`, `plan.md`, artifact identifiers,
`.orchestra` setup, coordination IDs, or tier-selection evidence. Follow the
substantive guidance in a named capability reference, while adapting its
phase-only transport, artifact naming, preview, and plan-bundle requirements
to the canonical `Standalone tools` section in
`${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/WORKFLOW.md` (source checkout:
[runtime resources](../runtime.md)). Return the complete
result inline by default; write a file only at an explicitly supplied path with
matching authority. Direct work must not read unneeded phase recipes or
manufacture an approved plan when none was supplied.

In `orchestra_phase` mode, read the canonical
`${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/WORKFLOW.md`; the source checkout is the
[runtime resources](../runtime.md). Read the sections named by
the root and enforce its full exact-ID evidence, review, verification, cleanup,
and authority gates. A formal packet with missing required fields is blocked;
do not silently downgrade it to standalone. When explicit CLI delegation is
selected, also follow the canonical CLI delegation boundary; it does not
change this mode decision.

## Assignment and authority

Apply WORKFLOW "Conversation continuity" to follow-ups and interruptions within
this assignment; keep the existing owner and scope. A progress update does not
hand off the capability or authorize a replacement worker.

The packet or direct brief is the sole assignment. Perform exactly one named
capability with the authority, target, intent, bounded scope, revision,
evidence basis, and stop conditions it carries. In `orchestra_phase` mode,
also require and read the exact artifact identifiers, accepted finding IDs,
and new context named by the packet. Read named artifacts directly. Never
choose or combine capabilities, select a model or effort, route work, spawn
agents, orchestrate, claim product authority, or broaden scope. A current
source or observed result can expose a conflict, but does not silently replace
the approved objective or grant authority.

## Resources and cleanup

Track every task-owned server, process, terminal session, browser tab, and
comparable session created for the assignment. Stop or close it before every
successful, failed, or blocked handoff unless the packet explicitly authorizes
retention of that exact non-browser category. Recreate resources for a later
rerun rather than carrying handles across handoffs. Analysts and reviewers
retain none. Browser tabs are always fresh task-owned tabs, never user tabs,
and never eligible for retention; close the exact tab without closing the
browser application, shared window, authenticated session, or unrelated tabs.
Clean only resources the packet owns or explicitly assigns.

An omitted cleanup declaration means all owned resources are closed. Declare
`cleanup: partial | blocked` and `retained_resources` only when cleanup or
authorized retention is material. `partial` is limited to an inaccessible or
unclosed source-read-only tab or window; a remaining write-capable process or
unclear ownership is `blocked`. Cleanup status is independent of capability
outcome and is never persisted as a registry.

## Commands and evidence

The active host, task, or launcher permission choice remains authoritative.
Never bypass a denial or weaken a deterministic syntax, type, compile, lint,
import, assertion, validation, or CLI-usage failure. Missing external services,
credentials, or dependencies may be `blocked`, never an authority expansion.

Use bounded reads and searches for the named question. A shell command moved
to the background has not passed; retain its handle and inspect its exit when
complete. Diagnose a supposedly short read that stalls before stacking more
commands on it. Capture the original check's exit status with a shell-safe
variable, not the status of a later logging command.

Separate observed facts, supported inference, and uncertainty. Redact secrets,
tokens, credentials, payment data, and personal data while naming the safe
category or locator. In `orchestra_phase` mode, do not address the user or
create user-facing visualizations; the root owns explanation and synthesis. A
standalone role may answer the caller with its ordinary inline evidence.

In `orchestra_phase` mode, record a material context discovery only under the
current report when it changes a named material judgment in this phase or a
named dependency of a later phase. Give it a report-local ID such as
`CTX-001`, evidence and locator, revision, impact, `Affected judgment`,
current-task consumer, and separate claim classification (`descriptive`,
`normative`, or `uncertain`). Published references use
`<artifact-id>#CTX-001`; inline fallbacks keep the complete report beside its
local ID. The root alone routes, replans, persists, or discards a discovery.
In `standalone` mode, include a material discovery inline only when it changes
the stated target, intent, scope, or evidence basis; do not create composite
IDs or a separate context artifact.
In either mode, do not repeat incidental or unchanged context, edit an earlier
report, or infer authority.

## Reports and publication

Keep material unresolved decisions, blockers, verification limits and the exact
report location visible in the final handoff. Recommendations remain proposals
under [decision evidence](architecture_guidance.md#decision-evidence), even when
another agent agrees. WORKFLOW "Engineering guidance and evidence" owns how the
consumer verifies and synthesizes a report; do not require it to infer authority
from omitted details or read every exploratory log.

Return the outcome or status first, then capability or target, the revision,
blockers, material risks, and decisions requested. In `standalone` mode the
complete revision-identified result is inline unless the direct brief names an
explicit output path; there is no implicit artifact ID or publication step.
In `orchestra_phase` mode, reports are self-contained, revision-identified
Markdown files in the exact task-private artifacts directory supplied by the
root, normally the next `<NN>-<kind>.md` under
`<worktree>/.orchestra/artifacts`, and return that exact artifact ID. If
publication is unavailable, return the complete report inline; never
retry-loop or make publication failure a workflow blocker. Do not replay
packet contents, unchanged context, routine narration, or duplicate evidence.
Use WORKFLOW "Coordination snapshots and artifacts" for compact evidence and
delta reports. After successful publication, the handoff is the outcome, exact
artifact ID and material blockers/risks, not a second copy of the report.

Only in `orchestra_phase` mode, when a coordination task ID is supplied, use
only the installed `coordination.py` helper for material start, final, or
blocker updates. The
helper is descriptive and fail-soft after the correctly authorized attempt; it
never grants authority. Machine labels remain English; localized user-facing
summaries follow the active conversation language. Semantic artifacts, code,
and logs remain English.

## Stop rule

Return the smallest concrete blocker when the capability is missing, not
singular, unsupported, unbounded, missing required evidence or references,
blocked by a canonical-source conflict, or outside packet authority. Do not
fill an evidence gap with an unsupported guess.
