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

## Next: plugin adoption and distribution

Resume this sequence after implementing and validating the agreed engineering
guidance inspired by pstack. That work adds no pstack runtime dependency.
Bridge remains out of scope.

1. Independently review the native-core and plugin-packaging change, focusing
   on runtime paths, agent dispatch, and migration from existing installations.
2. Prove a complete task from a clean plugin installation in Codex, then Cursor
   and Grok: planning, implementation, independent review, verification, commit,
   resume, and cleanup. Skill discovery alone does not satisfy this acceptance.
3. Prepare versioned downloadable bundles and a clear installation/update path;
   automate package construction and validation in CI before public publication.
4. Rehearse sync-to-plugin migration, update, and uninstall without duplicate
   skills or loss of task data, configuration, or worktrees. Keep the active
   installation on direct sync until that migration is explicitly selected.
5. Reconcile README distribution wording and document separately the hosts with
   verified installation and those with verified end-to-end workflow execution.

Task Control and Hub remain optional. Additional harnesses and comparative model
benchmarks follow these adoption checks. This list records follow-up work; it
does not itself authorize publication or a change to the active installation.

## Deferred quality and model evaluation

After the plugin acceptance sequence above, compare the baseline and revised
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
