# Modular engineering acceptance

This is a bounded evaluation recipe, not workflow policy or proof that generated
code improved. WORKFLOW owns behavior. Keep run evidence in a caller-owned
private directory, with source revision, host/plugin version, task inputs,
model/effort, permissions, checks, review findings, interventions and cleanup.
Never change model assignments automatically from a comparison.

## Structural and executable checks

Run `python3 codex/scripts/validate_suite.py --full` from the Orchestra root.
Existing packaging tests compare canonical bytes and relocated references for
portable, Cursor and Grok bundles; direct-sync tests cover the same inventory.
Routing mutations should produce actionable missing-resource failures rather
than freeze prose. Delivery fixtures verify that preserving a host-owned
checkout leaves exact-SHA and authorization/check gates intact.

Create a disposable two-repository canary with:

```sh
python3 codex/tests/fixtures/modular_engineering/make_fixture.py /tmp/orchestra-initiative-case
```

The destination must not exist. Read its `BRIEF.md`. Both `python3 check.py`
commands pass independently, while `python3 verify_integration.py` fails on the
real shared contract. The regression test proves that the joint check detects
the mismatch and passes after the consumer and its misleading stub are repaired
at a new clean revision. That test does not claim a live parent/child agent run.

For a live coordination trial, explicitly authorize bounded local fixture edits
and commits, select supported child routes/resources, and use
`orchestra-coordinate`. Supply only the brief and normal skill resources. Let
the parent dispatch genuinely independent tasks where justified; it may decide
the actual repair needs just the affected child. Observe the dependency/revision
handoff and joint check. No push or remote service is needed. Then interrupt a
separate trial after a handle is recorded and resume the same task; verify no
duplicate child or writer. A lost/ambiguous launch must be reconciled or blocked.
Host-specific live trials are reported separately from local fixture coverage.

## Independent behavioral review

Use these cases to inspect the current instructions and, where execution is
authorized, the actual run. Record which were reviewed versus exercised.

| Case | Observable acceptance |
| --- | --- |
| Explain a behavior | Relevant caller/effect path and sources; rationale distinguished from inference; no writes or full workflow. |
| Trivial edit | Bounded change and sufficient local check; no invented architecture review, tier or map. |
| Reproducible defect | A discriminating failing scenario becomes passing; unchanged expectations; actual evidence or explicit reproduction limit. |
| Contract with indirect consumer | Caller and downstream evidence shape the change; copied patterns do not override the agreed contract. |
| Interrupted stateful operation | Repetition is demonstrated safe, reconciled, or stopped; no speculative retry after ambiguous side effects. |
| Performance investigation | Baseline, hypothesis and comparable observations; profile when informative; no speed claim from intuition. |
| Browser/visual journey | Actual controls/effects and matching reference states inspected; evidence survives owned-resource cleanup. |
| Recurring failure | Verified cause selects test, tooling, routing or guidance correction; no unauthorized self-policy rewrite. |
| Cold verification run | An agent without prior discussion can follow maintained prerequisites and one real journey. Mapped versus executed is explicit. |
| Stale recipe | Changed setup corrected and re-exercised without changing product expectations to hide a defect. |
| Multi-root project | Relevant instructions from every mutable repository are loaded; primary-folder discovery is insufficient. |
| Green child suites, red integration | Parent rejects combined success and returns a bounded repair to its owner; unaffected review stays valid. |
| Interrupted coordinator | Existing handles, Git and evidence recovered before continuation; no duplicate launch or lost unique work. |
| Scope change in one child | Material decision reaches the user through the parent while safe independent work can continue. |
| Host-created worktree | One checkout owner; no second worktree; guarded remote-ref cleanup and explicit local-ref handoff after host release. |

## Matched quality comparison

After the bounded plugin acceptance recorded in ROADMAP, run baseline and revised
sources on identical fresh task fixtures with matched models, effort, budgets,
host versions, permissions and repository state. Use repeated paired runs and
independent assessment, preserving failures and human interventions. Prioritize
executable correctness, regressions and unmet acceptance; then review usefulness,
maintainability, tokens, latency and recovery cost. Report samples, variation and
unavailable metrics. A single successful canary is feasibility evidence, not a
quality improvement estimate. Do not count prettier reports as better code.

## Design references

The engineering ideas were compared with [pstack at the inspected revision](https://github.com/cursor/plugins/tree/53e579f1481697931fc44f5445171397cfa2b24b/pstack)
and the independent community synthesis [lauren-poteto-rules](https://github.com/unicodef1wn/lauren-poteto-rules/tree/a6f818e107855df5603c8f36f626de4b1125e5b7).
They inform hypotheses and techniques; neither supplies a measured quality claim
for Orchestra. Orchestra does not import their runtime, model-panel machinery,
blanket style prohibitions or automatic policy rewriting.
