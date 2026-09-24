# Shared architecture and engineering guidance

Use the sections relevant to the assigned change, risk, or evidence question
in either standalone or Orchestra phase mode. Architecture analysis uses the
review frame; other roles consume the applicable design, change, and evidence
guidance without requiring an architecture assignment. This is a shared
reference, not a capability playbook or a checklist for every task. Apply it
within the role's existing authority; it never authorizes edits, extra agent
dispatches, or new gates. WORKFLOW "Engineering guidance and evidence" owns
operational routing and evidence placement.

## Source comments

This policy applies whenever an Orchestra entry authors source text, including
ordinary engineering, Lite, project-start, maintenance and delegated work. Do
not add explanatory comments, narrative docstrings, TODO/FIXME commentary,
decorative section markers or commented-out code. Express behavior and
invariants through names, structure, types and executable tests. Why a change
was made belongs in its commit or PR; retain durable constraints in existing
maintained documentation, without copying removed commentary indiscriminately.

Preserve required legal notices and syntax with an actual machine consumer:
shebangs, encoding declarations, compiler/linter directives, generator markers
and configured public documentation contracts. A functional docstring needs a
named consumer such as CLI help, runtime schema generation or a configured
public API documentation build. Generic `pydoc`, `help()` or IDE display is not
such a consumer. A directive's required reason syntax may remain; a separate
trailing explanation is narrative. Do not add suppressions to evade this rule.

The policy covers application code, tests, scripts and executable configuration.
It takes priority over generic advice to copy nearby patterns, while respecting
instruction hierarchy and binding repository contracts. Report a conflicting
normative convention once and resolve it through the applicable authority;
never silently strip required interface documentation or change a hard gate.
An explicitly authorized policy revision needs no duplicate approval.

Legacy removal is bounded maintenance, not an unrelated sweep during feature
work. Check whether code or comment is wrong, investigate the actual workaround
and preserve verified constraints in behavior, tests or maintained docs before
removing their only explanation. Unresolved intent remains a finding. Keep
vendor/generated material under its real owner's lifecycle. Do not change APIs
or move narrative into docstrings merely to avoid comment syntax. The forward
rule does not certify that untouched legacy files contain no comments.

## Prevent recurring failures

For a verified recurring failure, distinguish missing guidance, incorrect
routing, missing context, ambiguous instructions and failure to follow a rule.
First consider excluding the bad state or path through data, API or ownership
design; then mechanical detection through types, compiler/lint/CI, a regression
test or reliable tool; then concise guidance where judgment is necessary.
Choose the strongest proportionate correction within scope, not an expensive
rewrite or another prohibition by default. Existing review evidence can inform
the choice; do not create a transcript-mining or reflection service.

When old debt cannot be removed safely at once, use an existing linter baseline
or Git comparison to prevent new instances while reducing the old set. A retained
exception needs an actual consumer and removal condition. Prove a new check
rejects the bad case and accepts a valid one. A new gate is normative policy;
use existing authorization rather than allowing the failed task to invent its
own permissions. This criterion works outside the full workflow checkpoint.

## Maintain patterns and knowledge

Ask what a later agent would do after copying or following the candidate.
Prioritize exposed examples, supported-path callers and instructions with a
concrete harmful outcome, including false-confidence tests and outdated tools.
A reproducible risk is enough; observed propagation strengthens the evidence.
Age, model provenance and stylistic taste alone do not establish a defect.

A no-reference search or low coverage never proves non-use. Trace relevant
imports, manifests, dynamic registration, persisted identifiers, generated
consumers and public or cross-repository interfaces before removal. Unknown
consumers remain a limitation; do not silently delete or deprecate the contract.
Preserve intentional distinctions when consolidating apparently similar code.

For docs and examples, verify commands and the supported behavior, retain unique
caveats at their canonical home and account for important external links. Broken
references may be descriptive corrections when intent is clear. Conflicting
normative instructions require authority reconciliation; noncompliant code does
not prove a rule obsolete. Keep unresolved historical constraints until evidence
settles them. A TODO without an owner is not automatically worthless.

Repair one coherent problem across its implementation, tests, examples and
instructions. If a mock hides the claimed behavior, demonstrate that gap with a
small controlled bad case and replace or strengthen the coverage. Record baseline
failures separately; never weaken expected behavior to make a cleanup green.
Report examined, sampled and unexamined scope. A healthy area needs no change.

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

## Understand the system

For an explanation or investigation, start at the relevant caller and trace
the data, decisions, effects and failure path far enough to answer the question.
Show a concrete example and exact source references; do not narrate the entire
repository. Separate what the implementation does from why it was designed
that way. Consult targeted history, tests, issues or dependency documentation
only when they can settle that rationale. An absent rationale stays an
inference; a historical comment is not proof of current behavior. Ask for
clarification only when the unresolved meaning changes the requested result.

## Resolve uncertainty experimentally

When an implementation choice rests on uncertain library behavior, integration
semantics or feasibility, prefer a small discriminating experiment over a more
elaborate speculative plan. State the question, expected observations and
decision it will inform. Reuse a fixture, scratch checkout or existing test
tool and preserve the result, actual versions and limitations. A prototype's
success proves only the behavior it exercised, not production readiness.

Experiments obey the caller's mutation, data and cost authority. A read-only
analyst may propose a probe or inspect existing results; it cannot install,
write or start services merely by calling the action research. Keep disposable
code private, clean up owned resources, and retain a helper only if it has a
continuing repository consumer. Choose the smallest supported mechanism from
the observations; do not create an experiment phase for routine certainty.

## Decision evidence

For a change whose correctness depends on callers, permissions, persistence or
compatibility, connect the approved scope to the relevant journey and decision:
caller → boundary → business decision/effect → expected behavior → verification.
Include consequential exceptions, unchanged paths and exclusions, not just edited
symbols. A short inline account often suffices; use a map only when it helps
another owner consume the evidence. Trivial edits do not require one.

For each material decision, identify the inspected repository and revision,
source locations or observed scenario, what that evidence establishes, and its
limits. Distinguish facts, supported inference and unresolved uncertainty. A
file/line citation or a search hit alone is not proof of the claimed behavior.
Follow relevant wrappers, imports, dynamic registrations and indirect or external
consumers; report search scope when consumers cannot be established. "No callers
found" is uncertainty, never permission to remove, expose or change a contract.

Check descriptive claims in comments and documentation against current evidence.
Keep intended behavior from the approved specification and normative sources
separate: an exposed endpoint can prove the code violates the requirement, not
that authentication is unnecessary. An intentional public caller establishes a
compatibility need, not by itself that its endpoint is safe. For authorization
changes, cover denied unauthenticated and insufficient-permission requests,
authorized success, credential propagation and any retained pre-login journeys.

Consume supplied evidence at its named revision. Inspect the affected delta and
missing paths instead of repeating valid research. Reconcile the map with the
original scope before changing code and before accepting it: omitted decisions
must not disappear merely because no row mentions them. An independent reviewer
actively looks for omissions and challenges the supplied conclusions.

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
  existing infrastructure and keep useful regression coverage. Identify the exact
  base, test inputs and observed failure; an import, setup or environment error
  is not evidence of the product defect. Distinguish regression tests from
  preservation tests, which may legitimately pass both before and after. When the prior
  failure cannot be reproduced safely or proportionately, state that limit and
  the alternative evidence; never manufacture a failure or claim an unobserved
  before/after result.
- Check test sensitivity where false confidence is a material risk: confirm the
  targeted reproducer detects the original defect, a controlled incorrect
  result, or the relevant boundary case. Inspect whether a mock bypasses the
  behavior being claimed. Do not add mutation testing or new tests to every
  edit; prefer one discriminating check over many assertions of the same fact.
- Nearby code is context, not automatic design authority. Before copying a
  pattern that affects correctness, check its actual consumers and constraints.
  Improve a demonstrated local defect within scope; propose broader policy or
  pattern changes separately when they were not authorized.

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
Use a runtime profile, query plan or trace when it can distinguish the proposed
bottleneck from competing explanations. Report what was measured, including
correctness and resource tradeoffs; less code or a plausible optimization is
not measured speed. Avoid changing several independent mechanisms at once.

## Verification recipes

Use the repository's existing commands, fixtures, and documentation first. When
they do not already establish the named acceptance, supply only the missing
recipe: prerequisites and safe data/reset; exact startup or check commands and
cwd; an observable readiness condition when a service is needed; the
representative user journey or runtime scenario and expected results; evidence
to capture; and cleanup of owned resources or data. Omit inapplicable parts and
reference maintained instructions instead of copying them.

For visual or interaction acceptance, identify the actual state, viewport and
reference before comparison. Exercise relevant controls, error/empty states and
responsive behavior; inspect screenshots at matching states and account for
dynamic data. A reachable page, attractive screenshot or changed snapshot is
not proof of functional correctness or parity. Use the existing design system
and user-approved visual intent rather than inventing taste-based gates.

Distinguish a recipe established from source from a run actually observed at a
named revision. A command exit or reachable page is sufficient only when it
proves the requested behavior. The assigned executor records results and
limitations; missing access or unsafe data never grants execution authority.
