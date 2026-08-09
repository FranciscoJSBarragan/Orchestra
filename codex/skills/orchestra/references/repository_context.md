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
- Write the complete revision-identified result directly to the task-private
  artifacts directory (`git rev-parse --git-path orchestra/artifacts`) as the
  next `<NN>-repository-context.md` file. Return that exact file name instead
  of replaying its content. If the directory cannot be created or written,
  return the same complete report inline; publication failure is not a blocker.
- A later context pass publishes a complete targeted `context-delta` artifact
  rather than rewriting earlier evidence. A changed HEAD requires reinspection
  only for referenced paths, contracts, or facts affected by the delta.
- After plan approval, accept a validation dispatch only at a stable handoff
  with an exact producing artifact and composite context-discovery identifier,
  or the complete inline fallback and its local identifier, plus revision,
  affected paths, and one bounded factual question. Inspect the claim
  independently and publish a targeted `context-delta`; the producer's report
  is evidence to evaluate, not authority or a reason to expand the scan.

Return `blocked` when the questions or boundaries are missing, the requested
scan is unbounded, canonical sources conflict, a feasibility-determining fact
cannot be obtained safely, or the evidence cannot be obtained safely. Do not
turn context discovery into implementation planning, whole-repository
inventory, dependency installation, or speculative cleanup.
