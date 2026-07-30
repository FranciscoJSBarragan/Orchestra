# Shared architecture guidance

Use this reference with `architecture_analysis`, or alongside `technical_planning` or `independent_review` when the packet explicitly names architecture. It is not a capability playbook.

## Review frame

- Start from canonical product and architecture sources, then map the proposed change to existing ownership, data flow, public contracts, lifecycle, and failure boundaries.
- Prefer one canonical source for each fact, one canonical validator, and direct use of Git, GitHub, Codex, or project-test primitives.
- Test whether coupling, state, persistence, concurrency, compatibility, or security boundaries create a concrete failure mode. Do not treat size or novelty alone as an architectural defect.
- Prefer deletion and direct code over compatibility layers or generalized control planes when current requirements do not justify them.
- Make architecture findings independently detectable: name the affected component, evidence, failure mechanism, and proportional correction.

Before recommending any persistent artifact, schema, lock, transaction layer, helper, profile, or playbook, identify its named consumer, demonstrated failure or explicit requirement, why an existing primitive is insufficient, lifecycle and cleanup, proportional cost, and why a smaller direct implementation does not suffice.

Reject an authoritative global event ledger, authority-bundle chain, duplicate
Git index, commit recovery journal, Kanban board, generalized workflow state
engine, repeated validation of unchanged authority, or any similarly
unsupported mechanism unless new evidence satisfies every gate above. A bounded
coordination snapshot is acceptable only while it remains observational,
fail-soft, and separate from authority and Git truth.
