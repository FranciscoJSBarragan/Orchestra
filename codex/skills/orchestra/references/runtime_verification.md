# Runtime verification playbook

Use this internal playbook only with the `verifier` profile and the explicit `runtime_verification` capability.

## Contract

- Run the packet's smallest sufficient set of targeted tests, runtime checks, static checks, or log inspections against the exact revision.
- Confirm command arguments and working directory before execution. Commands must not pass through an unrequested shell wrapper or mutate source.
- Run tests in the ordinary sandbox unless the packet declares a concrete elevated requirement.
- Before broader verification, diagnosis, or returning any failed test as product evidence, rerun the exact same command, arguments, and working directory once with elevated permission. If it passes, accept that evidence and record the sandbox dependency. If it fails again, classify the repeated result. Return `blocked` when elevation is unavailable or unsafe.
- Record each command or scenario, exit status, salient output, observed behavior, and any permitted generated or temporary side effects.
- Retain only explicitly permitted test processes for reuse by this same verifier during the phase. Report their exact handles on every return. On the root's phase-teardown request, stop only those owned processes, report the result, and do not run new verification.
- Distinguish product failure, test failure, flaky or nondeterministic evidence, and environment/tooling failure. Never reinterpret skipped, partial, stale, or failed evidence as passing.
- Re-run only checks affected by an accepted fix unless a canonical full-suite gate is explicitly required.

Return `blocked` when the environment, dependency, credential, test data, revision, or evidence source is unavailable or unsafe. Return `failed` when trustworthy evidence demonstrates unmet acceptance or a regression.
