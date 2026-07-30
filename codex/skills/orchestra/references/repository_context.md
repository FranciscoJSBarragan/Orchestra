# Repository context playbook

Use this internal playbook only with the `orchestra_analyst` profile and the explicit `repository_context` capability.

## Contract

- Answer only the focused repository questions in the packet; do not plan or implement the change.
- Read the repository's applicable `AGENTS.md` files and canonical product sources before interpreting local conventions.
- Inspect the smallest relevant domain and prefer a changed context delta over rereading evidence that is still valid.
- Report paths, symbols, relationships, established patterns, relevant tests, and unresolved facts at the exact inspected revision.
- Separate direct observations, inferences, and unresolved facts. Name evidence
  that could disprove an inference.
- When feasibility depends on persisted types, schema versions, API contracts,
  signatures, transactions, invariants, downstream consumers, migrations,
  fixtures, or canonical verification commands, inspect those exact constraints
  rather than leaving them as assumptions.
- Report read-only execution readiness relevant to the task: canonical setup and
  verification commands, runtime and dependency expectations, required services
  and permissions, credential categories without reading secrets, test-data
  provenance, and generated or cache paths.
- When the packet includes a coordination task identifier, write the complete
  revision-identified result to a temporary Markdown file and publish it with
  `coordination.py artifact put --kind repository-context`. Return the artifact
  identifier instead of replaying its content. If publication is unavailable,
  return the same complete report inline; telemetry failure is not a blocker.
- A later context pass publishes a complete targeted `context-delta` artifact
  rather than rewriting earlier evidence. A changed HEAD requires reinspection
  only for referenced paths, contracts, or facts affected by the delta.

Return `blocked` when the questions or boundaries are missing, the requested
scan is unbounded, canonical sources conflict, a feasibility-determining fact
cannot be obtained safely, or the evidence cannot be obtained safely. Do not
turn context discovery into implementation planning, whole-repository
inventory, dependency installation, or speculative cleanup.
