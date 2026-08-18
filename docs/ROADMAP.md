# Orchestra Roadmap

## Status

This roadmap is non-canonical. It does not override `VISION.md`,
`docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, or `AGENTS.md`.

Current work prioritizes dependable repository-driven direct sync and proven
software-delivery behavior. The sequence is canonical contract first,
executable routing and conformance second, then real-project evidence.

## Deferred distribution boundary

Plugin and marketplace distribution remains deferred until all of these
conditions hold:

- install, update, status, and uninstall are dependable;
- user configuration is preserved reliably;
- standard and critical workflows succeed in real projects;
- local and PR delivery are proven;
- the user judges the product mature;
- packaging reduces friction without creating a second runtime.

Cursor local plugin install under `~/.cursor/plugins/local` is not marketplace
distribution. Agent Plugins / Cursor Marketplace publication stays deferred.

Meeting these conditions permits a product decision about distribution; it does
not prescribe an implementation design.

## Deferred model benchmark

The approved capability matrix is the initial runtime contract. A comparative
benchmark is deferred until the four profiles, capability playbooks, local plan
resume flow, and conformance suite work end to end. Bootstrap and installation
work must not invoke Orchestra to evaluate Orchestra.

After that boundary, representative canary tasks may compare the approved model
assignments using correctness, defects found by independent review, verification
reliability, latency, and token use. The benchmark informs a later explicit
product decision; it does not silently rewrite assignments, add a benchmarking
profile, persist workflow telemetry, or require a benchmark control plane.
