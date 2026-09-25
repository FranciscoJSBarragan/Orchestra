# Remote Lite review packet

Use the existing [reviewer](../orchestra-role-reviewer/SKILL.md) in standalone
mode, with independent context. WORKFLOW "Lite coordinator acceptance" owns
check scope, version handling, recovery and acceptance. Use
[decision evidence](../orchestra/references/architecture_guidance.md#decision-evidence)
to assess the original scope, not merely the supplied map.
Use [change quality](../orchestra/references/architecture_guidance.md#change-quality)
and [behavioral verification](../orchestra/references/architecture_guidance.md#behavioral-verification)
to assess necessary scope and the protection supplied by tests.

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
Acceptance basis: <settled consequential choices and any explicitly authorized check exceptions>
Superseded recommendations: <when relevant, replaced conclusions and remaining facts, risks and gaps>
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

For a pre-code decision review, supply the original brief, base revision and
current decision evidence instead of a delivered result or implementation diff.
Name the material choices to assess and use the same standalone reviewer under
WORKFLOW "Engineering guidance and evidence". Return a verdict on those choices
and unresolved dependencies; do not claim implementation or execution acceptance.
Apply shared decision evidence to recommendations presented as settled policy.
Name a material authority gap in the verdict's findings or blockers rather than
approving access choices and burying the unresolved question in supporting prose.
