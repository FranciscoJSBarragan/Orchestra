# Remote Lite review packet

Use the existing [reviewer](../orchestra-role-reviewer/SKILL.md) in standalone
mode, with independent context. WORKFLOW "Lite coordinator acceptance" owns
check scope, version handling, recovery and acceptance. Use
[decision evidence](../orchestra/references/architecture_guidance.md#decision-evidence)
to assess the original scope, not merely the supplied map.

Supply only the relevant inputs below; paths must be readable from the review
environment. This is a prompt shape, not a new schema or artifact kind.

```text
Capability: independent_review (standalone remote Lite review)
Authority: source-read-only review and local test execution; no commit, push or merge
Repository and checkout: <identity and independent checkout>
Original approved kickoff: <complete spec or accessible path>
Review range: <full base SHA>..<full delivered SHA>
Result: <ORCHESTRA_LITE_RESULT or accessible Reporte>
Decision evidence: <inline result evidence and optional Mapa, with source revisions>
Checks: <new/changed tests and affected journeys, including indirect consumers>
Security scope: <when applicable, full affected-project suite and security journeys>
Readiness: <existing setup recipe, safe data, permissions, generated paths and cleanup>
Prior review: <none on first review; same-reviewer findings and delta on continuation>
Output: accepted | findings | blocked, exact reviewed revision and evidence
```

For a required pre-commit review, replace the delivered SHA with the exact HEAD
plus the complete accessible patch and its SHA-256, using WORKFLOW's existing
patch contract. The coordinator prepares the isolated patched checkout and
owns its cleanup; the reviewer validates and tests that precise tree without
authoring source changes or creating a worker commit. Report commands, exit status, observed behavior, omissions, limitations,
and actionable findings with locations. A prose assertion that checks passed is
not independent execution. Keep conclusions and any authorized report output
separate from source changes; clean up owned test resources.
