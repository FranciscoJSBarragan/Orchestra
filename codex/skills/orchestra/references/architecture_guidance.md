# Shared architecture and engineering guidance

Use the sections relevant to the assigned change, risk, or evidence question
in either standalone or Orchestra phase mode. Architecture analysis uses the
review frame; other roles consume the applicable design, change, and evidence
guidance without requiring an architecture assignment. This is a shared
reference, not a capability playbook or a checklist for every task. Apply it
within the role's existing authority; it never authorizes edits, extra agent
dispatches, or new gates. WORKFLOW "Engineering guidance and evidence" owns
operational routing and evidence placement.

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

## Design from the consumer

- For a meaningful contract or component change, describe a concrete caller's
  input, expected result, and relevant failure behavior before choosing an
  interface. Use existing consumers to test whether the proposed abstraction
  earns its cost; do not invent callers or require multiple designs for a local
  edit.
- Where invalid combinations cause a real defect risk, prefer types or data
  shapes that exclude them, preserve semantic distinctions, and make relevant
  variants exhaustive. Reuse the project's schema authority and conventions;
  a new wrapper type or public-contract change still needs justification and
  scope.
- Separate business decisions from network, filesystem, or framework effects
  when that improves reasoning or testing. Parse external input at its boundary;
  mutable authorization, ownership, or persistence invariants may still need
  rechecking at the operation that relies on them. Internal origin alone is
  not proof of validity.
- Judge readability by the layers and independent state a reader must follow
  to explain behavior. Simplify pass-through wrappers or scattered decisions
  when their cost is concrete. Line counts, stylistic taste, and abstraction
  counts alone are not findings.

## Evidence for consequential changes

- Identify assumptions that determine correctness, including indirect callers,
  persisted data, and behavior of the actual dependency version. Inspect the
  relevant source, contract, or executable evidence beyond the immediate diff.
  Name an unresolved assumption and its consequence instead of treating passing
  unrelated tests as proof. Feasibility blockers follow the planning contract.
- Before removing a consequential guard or compatibility path, inspect its
  relevant tests and targeted Git history. Use an associated issue or PR only
  when it can settle a material question. Distinguish recorded intent from
  inferred rationale; unavailable history is an evidence gap, not a requirement
  to search every source or preserve dead code indefinitely.
- For a defect fix, when practical, capture a failing regression test or
  minimal reproducer before editing implementation. Confirm it fails for the
  reported behavior, then run the same scenario against the correction. Reuse
  existing infrastructure and keep useful regression coverage. When the prior
  failure cannot be reproduced safely or proportionately, state that limit and
  the alternative evidence; never manufacture a failure or claim an unobserved
  before/after result.

## State and repeated changes

- For shared-state risk, first consider removing sharing or narrowing
  ownership. Otherwise identify the invariant and use an existing transaction,
  ownership boundary, or synchronization primitive that actually protects it.
  A documented order of operations alone does not establish concurrency safety.
- For stateful operations, examine interruption points, repeated execution,
  partial success, and recovery. Prove safe retry or idempotency where relied
  upon; reconcile the actual state or stop when an external effect may already
  have occurred. Do not add a recovery journal or transaction layer without
  satisfying the review frame's mechanism test.
- For repetitive edits, prefer a deterministic transformation when it reduces
  error or review cost. Validate one representative change, inspect the full
  affected scope or dry-run diff, and check exceptions before broad application.
  Keep the transformation within authorized paths. Retain a helper only for a
  named continuing consumer; otherwise use a task-local tool and clean it up.

## Performance evidence

For performance work, record a reproducible baseline, workload, environment,
metric, and hypothesis before changing the implementation. Isolate the proposed
change and compare under equivalent conditions, with enough repetitions to
separate the result from normal variation. Preserve correctness checks and
report relevant resource or latency regressions. A noisy or unmatched result
is inconclusive, not an improvement. Use existing benchmarks or a bounded
task-local measurement; ordinary work does not acquire a benchmark requirement.

## Verification recipes

Use the repository's existing commands, fixtures, and documentation first. When
they do not already establish the named acceptance, supply only the missing
recipe: prerequisites and safe data/reset; exact startup or check commands and
cwd; an observable readiness condition when a service is needed; the
representative user journey or runtime scenario and expected results; evidence
to capture; and cleanup of owned resources or data. Omit inapplicable parts and
reference maintained instructions instead of copying them.

Distinguish a recipe established from source from a run actually observed at a
named revision. A command exit or reachable page is sufficient only when it
proves the requested behavior. The assigned executor records results and
limitations; missing access or unsafe data never grants execution authority.
