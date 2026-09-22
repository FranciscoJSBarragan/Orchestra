# Orchestra Roadmap

## Status

This roadmap is non-canonical. It does not override `VISION.md`,
`docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, or `AGENTS.md`.

The native workflow packages from canonical sources into relocatable bundles.
Shared engineering guidance now supports conditional design, regression,
state, performance, and verification practices through the existing roles.
Conformance and package checks establish integration, not improved generated
code quality. Plugin installation is an alternative to direct sync; it does
not create a second runtime.

## Distribution

Local plugin packaging is supported. Public marketplace publication remains a
separate explicit delivery decision after host acceptance and real-project
workflow evidence. This roadmap does not prescribe an implementation design.

Bridge integration is deferred. Native adapters and CLI delegation remain in
Orchestra. Task Control and Hub stay optional.

## Plugin adoption evidence

The engineering guidance and native/plugin source changes received independent
review. Clean isolated Codex, Cursor, and Grok CLI installations completed a
bounded task through planning, process restart/resume, native implementation,
independent verification and review, phase commit, and agent cleanup.
[Packaging documentation](../packaging/README.md) records host versions,
actual dispatch, lifecycle caveats, delivery coverage, and a repeatable recipe.

The sync-to-plugin migration rehearsal preserved unrelated configuration,
task data, and worktrees without duplicate direct-sync skills. Codex cached
updates and removal were checked; Grok's stale local update required explicit
remove/install. Cursor used a session-local bundle. The `Plugin bundles` CI
workflow validates canonical sources and produces versioned downloadable
candidates and checksums, without creating a release or marketplace entry.

The remaining adoption work is broader real-project evidence, including
managed worktrees and remote PR delivery through installed plugins. Migrate
the active direct-sync installation only when explicitly selected. Public
publication remains a separate delivery decision.

Task Control and Hub remain optional. Additional harnesses and comparative model
benchmarks follow these adoption checks. This list records follow-up work; it
does not itself authorize publication or a change to the active installation.

## Deferred quality and model evaluation

After the bounded plugin acceptance above, compare the baseline and revised
engineering guidance on matched tasks, models, reasoning effort, budgets, and
environments. Include regression fixes, contract changes with indirect
consumers, stateful recovery, and a user journey. Use repeated paired runs and
independent assessment of executable acceptance and resulting changes;
correctness and regressions precede maintainability, latency, and token cost.
Keep this a bounded evaluation, separate from changes to model assignments.
No quality improvement is established by conformance checks alone.

The approved capability matrix is the initial runtime contract. A comparative
benchmark is deferred until the four profiles, capability playbooks, local plan
resume flow, and conformance suite work end to end. Bootstrap and installation
work must not invoke Orchestra to evaluate Orchestra.

After that boundary, representative canary tasks may compare the approved model
assignments using correctness, defects found by independent review, verification
reliability, latency, and token use. The benchmark informs a later explicit
product decision; it does not silently rewrite assignments, add a benchmarking
profile, persist workflow telemetry, or require a benchmark control plane.

## Modular workflow acceptance

Reusable engineering and project-verification entries plus an explicit parent
coordinator now compose with full Orchestra, Lite and custom child workflows.
[Modular acceptance](evaluation/MODULAR_ACCEPTANCE.md) separates source/routing
checks, the two-repository integration canary, live host trials and matched
quality evaluation. Host-provided checkouts are retained for host cleanup after
authorized delivery. The same four roles and seven internal playbooks remain.

Broader live parent/child acceptance, active-installation updates and public
distribution remain explicit subsequent work. Current source tests do not prove
that every host discovers a skill, that cloud resume works in all environments,
or that generated code improves. Keep comparative evaluation after bounded
plugin acceptance and preserve the pending distribution and Bridge work above.
