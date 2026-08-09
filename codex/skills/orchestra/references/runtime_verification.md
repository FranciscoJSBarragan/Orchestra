# Runtime verification playbook

Use this internal playbook only with the `orchestra_verifier` profile and the explicit `runtime_verification` capability.

## Contract

- Run the packet's smallest sufficient set of targeted tests, runtime checks, static checks, or log inspections against the exact revision.
- Confirm command arguments and working directory before execution. Commands must not pass through an unrequested shell wrapper or mutate source.
- Orchestra synchronizes Guardian (`:workspace`, `on-request`, and Auto-review)
  as the default. The active permission choice for the task, host, or launcher
  remains authoritative: Orchestra never changes it or blocks execution solely
  because it differs.
- When Guardian is active, commands inside the workspace run directly and one
  exact command that crosses a protected boundary requests one narrow
  escalation for automatic review. With manual approvals, that escalation may
  prompt the user; with Full Access, it runs without the workspace sandbox
  boundary. Never retry a denial through a workaround or broaden permissions.
  Deterministic syntax, type, compile, lint, import, assertion,
  validation-contract, and CLI-usage failures remain real failures. A missing
  external service, credential, or dependency may return `blocked`, but never
  broadens task authority.
- Require test-data provenance, creation or reset method, safe identifiers, and
  cleanup when the check uses mutable data. Reuse repository fixtures or seeds.
- Record each command or scenario, exit status, salient output, observed behavior, and any permitted generated or temporary side effects.
- Follow shared resource hygiene: stop owned test processes before every handoff and recreate them when a later rerun needs them. Retain a process only when the packet explicitly authorizes its category for phase reuse, and report its exact handle on every return.
- Distinguish product failure, test failure, flaky or nondeterministic evidence, and environment/tooling failure. Never reinterpret skipped, partial, stale, or failed evidence as passing.
- Re-run only checks affected by an accepted fix unless a canonical full-suite gate is explicitly required.

Return `blocked` when the environment, dependency, credential, test data, revision, or evidence source is unavailable or unsafe. Return `failed` when trustworthy evidence demonstrates unmet acceptance or a regression.
