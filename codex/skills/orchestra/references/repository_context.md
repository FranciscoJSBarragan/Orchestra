# Repository context playbook

Use this internal playbook only with the `analyst` profile and the explicit `repository_context` capability.

## Contract

- Answer only the focused repository questions in the packet; do not plan or implement the change.
- Read the repository's applicable `AGENTS.md` files and canonical product sources before interpreting local conventions.
- Inspect the smallest relevant domain and prefer a changed context delta over rereading evidence that is still valid.
- Report paths, symbols, relationships, established patterns, relevant tests, and unresolved facts at the exact inspected revision.
- Separate direct observations from inferences and name evidence that could disprove an inference.

Return `blocked` when the questions or boundaries are missing, the requested scan is unbounded, canonical sources conflict, or the evidence cannot be obtained safely. Do not turn context discovery into implementation planning, whole-repository inventory, or speculative cleanup.
