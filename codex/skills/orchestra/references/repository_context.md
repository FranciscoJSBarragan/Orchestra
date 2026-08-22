# Repository context playbook

Use this internal playbook only with the `orchestra_analyst` profile and the explicit `repository_context` capability.

## Contract

- Answer only the focused repository questions in the packet; do not plan or implement the change.
- Read `.agent/` first, then the repository's applicable `AGENTS.md` files and canonical product sources before interpreting local conventions. Report the convention taxonomy (scope, hard gate, diagnostic-only, forbidden substitutions, opt-in, prerequisites) from those files. If `.agent/` is missing, say `none` plus the inference sources; never invent gates. A `normative` or `uncertain` conflict with `AGENTS.md` or delivery checks is an authority boundary: block and do not guess.
- Inspect the smallest relevant domain and prefer a changed context delta over rereading evidence that is still valid.
- Report paths, symbols, relationships, established patterns, relevant tests, and unresolved facts at the exact inspected revision.
- Separate direct observations, inferences, and unresolved facts. Name evidence
  that could disprove an inference.
- Identify the canonical versioned sources that support each material project
  guardrail. For context-maintenance questions, keep evidence classification
  (observed fact, supported inference, or unresolved uncertainty) separate from
  context classification: `descriptive` for a current-state fact, `normative`
  for intended behavior or a constraint, and `uncertain` when the source's role
  cannot be established. Classify the claim, not an entire mixed-purpose file.
- Never treat current code as proof that a normative source is stale. Report a
  code-versus-intent conflict explicitly so the root can decide whether code,
  documentation, the phase, or user authority must change.
- When feasibility depends on persisted types, schema versions, API contracts,
  signatures, transactions, invariants, downstream consumers, migrations,
  fixtures, or canonical verification commands, inspect those exact constraints
  rather than leaving them as assumptions.
- Report read-only execution readiness relevant to the task: canonical setup and
  verification commands, runtime and dependency expectations, required services
  and permissions, credential categories without reading secrets, test-data
  provenance, and generated or cache paths.
- Write the complete revision-identified result directly to the exact
  task-private artifacts directory supplied by the packet, normally
  `<worktree>/.orchestra/artifacts`, as the
  next `<NN>-repository-context.md` file. Return that exact file name instead
  of replaying its content. If the directory cannot be created or written,
  return the same complete report inline; publication failure is not a blocker.
- A later context pass publishes a complete targeted `context-delta` artifact
  rather than rewriting earlier evidence. A changed HEAD requires reinspection
  only for referenced paths, contracts, or facts affected by the delta.
- After plan approval, accept a validation dispatch only at a stable handoff
  with an exact producing artifact and composite context-discovery identifier,
  or the complete inline fallback and its local identifier, plus revision,
  affected paths, mandatory `Affected judgment`, named current-task consumer,
  and one bounded factual question. The packet must state how at least one
  possible result could change acceptance, a finding disposition, replanning,
  or a required `persist`; otherwise return `blocked` without scanning.
  Inspect the claim independently after that gate and publish a targeted
  `context-delta`; the producer's report is evidence, not authority.
- A validation `context-delta` states the claim result (`confirmed`,
  `disproved`, or `unresolved`), both classifications, exact source paths and
  inspected revision, whether the candidate target is versioned
  human-readable documentation or executable/operational state, and the
  evidence needed by the root's disposition. Also state the result's effect on
  the named judgment and consumer. Publish an unresolved conflict instead of
  guessing which source should win.
- After an authorized context-documentation correction, accept one bounded
  revalidation dispatch for the changed paths and current dirty revision.
  Publish a fresh targeted `context-delta` that confirms or rejects the
  correction; do not edit the source or accept the implementer's report as
  proof. This post-edit revalidation is mandatory and bypasses the earlier
  decision-change admission gate because it proves an edit already made.

Return `blocked` when the questions or boundaries are missing, the requested
scan is unbounded, a material canonical-source conflict remains unresolved, a
feasibility-determining fact cannot be obtained safely, or the evidence cannot
be obtained safely. When publication is possible, preserve the bounded conflict
and its classifications in the targeted `context-delta` before returning the
blocker. Do not turn context discovery into implementation planning,
whole-repository inventory, dependency installation, or speculative cleanup.
