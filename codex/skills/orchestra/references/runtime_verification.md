# Runtime verification playbook

Use this internal playbook only with the `orchestra_verifier` profile and the explicit `runtime_verification` capability.

## Contract

- Run the packet's smallest sufficient set of targeted tests, runtime checks, static checks, or log inspections against the exact revision.
- Confirm command arguments and working directory before execution. Commands must not pass through an unrequested shell wrapper or mutate source.
- Run tests in the ordinary sandbox unless the packet declares a concrete elevated requirement.
- Classify a failure from its direct evidence before requesting elevation. Rerun
  the exact same command, arguments, and working directory once with elevated
  permission only when sandboxing, permissions, filesystem access, network
  access, sockets, local services, or protected caches could plausibly explain
  it. Do not elevate deterministic syntax, type, compile, lint, import,
  assertion, validation-contract, or CLI-usage failures. If the cause is
  genuinely ambiguous, one exact elevated retry is allowed. If it passes,
  accept that evidence and record the sandbox dependency. Otherwise classify
  trustworthy deterministic or repeated evidence. Return `blocked` when
  required elevation is unavailable or unsafe.
- Require test-data provenance, creation or reset method, safe identifiers, and
  cleanup when the check uses mutable data. Reuse repository fixtures or seeds.
- Record each command or scenario, exit status, salient output, observed behavior, and any permitted generated or temporary side effects.
- Retain only explicitly permitted test processes for reuse by this same verifier during the phase. Report their exact handles on every return. On the root's phase-teardown request, stop only those owned processes, report the result, and do not run new verification.
- Distinguish product failure, test failure, flaky or nondeterministic evidence, and environment/tooling failure. Never reinterpret skipped, partial, stale, or failed evidence as passing.
- Re-run only checks affected by an accepted fix unless a canonical full-suite gate is explicitly required.

Return `blocked` when the environment, dependency, credential, test data, revision, or evidence source is unavailable or unsafe. Return `failed` when trustworthy evidence demonstrates unmet acceptance or a regression.
