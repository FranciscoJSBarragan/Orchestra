# Difficult debugging playbook

For direct role use, apply WORKFLOW "Standalone tools": keep the engineering
guidance below, but omit phase-only transport, artifact IDs, and formal plan
bundles. Return inline evidence or an explicitly requested output path.

Use this internal playbook only with the `orchestra_analyst` profile and the explicit `difficult_debugging` capability after an escalation trigger fired — the same causal failure repeated, correction cycles demonstrably failed to converge, scope expanded, or evidence indicates a deeper shared cause — and the root chose deeper diagnosis over reassessing the approach, recommending a tier change, or asking the user.

## Contract

- Require the repeated failure signature, attempted approaches, changed context delta, relevant logs and verification, diagnostic scope, exclusions, and revision.
- Reproduce or trace only within the permitted diagnostic boundary. Distinguish the observed symptom, triggering condition, causal mechanism, and affected scope.
- Form competing hypotheses, seek discriminating evidence, record disproved hypotheses, and state confidence in the supported root cause.
- Recommend the smallest local corrective action for the same implementation owner. Do not implement it or restart discovery, planning, or the whole workflow.
- Prefer source, runtime, test, and log evidence over intuition; do not claim a guess as diagnosis.
- When coordination is available, publish the complete diagnosis as
  `debugging-report` and return its exact identifier. The implementation owner
  reads that document directly; the root does not restate the diagnosis.

Return `blocked` when failures are not demonstrably the same, safe reproduction or tracing is unavailable, the diagnosis crosses an authority boundary, or no root cause is supported by current evidence. Ask for the smallest missing evidence.
