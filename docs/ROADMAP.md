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

## Preventive engineering and maintenance

The maintenance entry extends modular engineering with evidence-backed diagnosis
and authorized repair of harmful code, documentation, rules and examples. Folder
reorganization is excluded. Shared guidance owns the source-comment policy and
prevention ladder; enforcement, personal adoption and real-project outcomes are
separate acceptance classes in the modular evaluation recipe.

After source/package validation, verify personal global-rule adoption and fresh
root/worker behavior on the supported hosts. Then select the real pilot repository
and area, preserve its baseline, prove a reusable journey and review a bounded
repair. Matched quality evaluation retains the plugin acceptance prerequisite.
No source test demonstrates universal instruction inheritance or improved code.
Event intake, scheduled gardener jobs, automatic feature-map maintenance, formal
verification and dashboards remain deferred. Existing distribution, coordinator
host acceptance and Bridge work above retain their separate boundaries.

## Decision evidence and remote Lite acceptance

The v2 source contract keeps coordinator instructions with the worker and ships
explicit legacy interpretation. Cloud coordinators must select the same pinned
revision and refresh their kickoffs; source changes do not migrate active workers.
Decision evidence applies proportionally across ordinary roles, full Orchestra
and Lite. Package conformance proves routing and shapes, not agent compliance.

After the existing plugin acceptance boundary, start the bounded
[three-case pilot](evaluation/MODULAR_ACCEPTANCE.md#decision-evidence-pilot)
with decision mapping and independent review together, holding resources fixed.
The external coordinator supplies verified case bases and hidden expected
outcomes. Only isolate the two effects if the combined pilot reveals a question
that warrants the extra runs. Keep correctness and regressions ahead of cost or
speed, and preserve all earlier distribution, adoption and Bridge follow-ups.
