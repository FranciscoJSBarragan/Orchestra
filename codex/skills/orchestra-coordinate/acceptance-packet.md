# Cross-environment acceptance packet

WORKFLOW "Cross-environment acceptance" owns applicability and responsibility.
Use this only to close a named gap after consuming the child's exact-revision
evidence. It supplements the child's workflow; it does not move its ordinary
review and correction loop into the parent.

Choose the existing [verifier](../orchestra-role-verifier/SKILL.md) for runtime
or browser execution, or the [reviewer](../orchestra-role-reviewer/SKILL.md) for
independent source judgment. Each receives one capability and its normal role
limits. Apply [decision evidence](../orchestra/references/architecture_guidance.md#decision-evidence),
[change quality](../orchestra/references/architecture_guidance.md#change-quality)
and [behavioral verification](../orchestra/references/architecture_guidance.md#behavioral-verification).

Illustrative packet, not a schema:

```text
Capability: <one existing review or verification capability>
Missing proof: <the concrete risk or inaccessible/different environment>
Authority: <source-read-only role and specifically authorized execution>
Repository and checkout: <identity, independent checkout, owner>
Approved objective and decisions: <accessible specification and relevant evidence>
Revision: <full base SHA and exact child revision to inspect>
Child evidence: <implementation, independent review, commands and results>
Acceptance: <missing behavior, checks, authorized exceptions and their limits>
Readiness: <setup recipe, safe data, permissions and cleanup>
Output: <role verdict, exact inspected revision, commands/exit codes and limits>
```

Verify that the receiver can retrieve the revision and read the reports before
discarding a remote environment. Keep reports and test outputs separate from
source; identify and clean up owned resources. A required unavailable check is
not a pass. Route any correction to the existing child and preserve its evidence.
