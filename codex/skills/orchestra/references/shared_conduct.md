# Shared agent conduct

Applies to every Orchestra role. Each rule here is stated once and is not
repeated in the role skills.

## Assignment

The packet is the only assignment: perform exactly one named capability with
the explicit authority, worktree, revision identity, target artifact file
names, and stop conditions it carries. Never choose or combine capabilities,
select a model or reasoning effort, route work, spawn agents, orchestrate, or
claim product authority. Read named artifacts directly instead of asking the
root to replay their content. Stop rather than broadening the packet or
inferring the current bundle by timestamp.

## Report discipline

Omit packet replay, routine process narration, praise, unchanged context, and
duplicate evidence. Do not omit relevant security, privacy, authentication,
payment, destructive or irreversible, blocker or authority, failure or exact
error, reviewer finding, ambiguity or conflicting evidence, verification,
locator, or remaining risk information; expand it enough for the root to act.
Redact secrets, credentials, tokens, personal data, and payment data while
stating the redaction and a safe category or locator.

## Publication and telemetry

Reusable results are complete revision-identified Markdown files in the
task-private artifacts directory (`git rev-parse --git-path
orchestra/artifacts`); the file name is the artifact identifier. Writing
there or updating coordination outside the active workspace uses one exact,
narrow Guardian escalation on the first attempt; never make a known-protected
write unprivileged first. Auto-review handles that escalation without a human
prompt, while a manual reviewer may prompt by design. The escalation is
expected and is not a blocker. Coordination
telemetry records only material start, final, or blocker updates and is
fail-soft only after that correctly authorized attempt: on `invalid` or
`unavailable`, or when the artifacts directory cannot be written, continue and
return the complete result inline; never retry-loop or report a workflow
blocker solely because publication failed.

## Stop rule

Stop and report the smallest concrete blocker when the capability is missing
or not singular, required references or evidence are unavailable, scope is
unbounded, canonical sources conflict, or the action would cross the packet's
authority. Never fill an evidence gap with an unsupported guess.
