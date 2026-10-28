---
name: orchestra-pr-review
description: Use once an Orchestra PR is open and whenever it gets feedback or check results; observes GitHub, triages, routes accepted fixes and returns when the current head is clean. Never merges.
---

# Bring the PR to clean

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Drive an open PR to one complete clean observation of its current head. The
loop and its authority are WORKFLOW "PR path"; judge every item with
[finding triage](../orchestra/references/finding_triage.md).

## Steps

1. Observe with `python3 "${ORCHESTRA_RUNTIME_ROOT}/scripts/pr.py" observe
   --repo <root> --repository <OWNER/REPO> --pr <number>`. Its fields are
   GitHub's facts. Review bodies and issue comments have no resolved state, so
   after triaging one, pass its token with `--acknowledged-feedback`, here and
   to the merge helper. A token binds the head and the exact content and never
   stands in for an unresolved thread.
2. Triage everything actionable. Dispatch the `independent_review` row the plan
   recorded only for feedback whose validity needs investigation, with
   PR-CONTEXT, the current diff and evidence, the feedback and only the new
   delta.
3. Send accepted items to a fresh session of the implementation owner under
   WORKFLOW "Phase execution". After its delta review, commit through
   [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), push and
   refresh the capsule through [orchestra-pr-open](../orchestra-pr-open/SKILL.md).
4. Resolve a thread by its ID once its fix is pushed or triage rejected it with
   evidence.
5. While checks are pending or failed, a bot review is in progress, review is
   required or changes are requested, the branch conflicts, accepted feedback
   is open or evidence is incomplete, watch the PR as
   [T3 Code](../orchestra/references/host_t3.md#pull-requests) defines and end
   your turn. On a wake, start again at step 1.

## Ask only if

Feedback asks for a visible change the user did not approve, or triage reaches
a decision the approved intent does not settle.

## Report

`ok` after one complete clean observation of the current head, with the head,
the checks and the review rounds. Otherwise `partial` or `blocked` with what
remains; when only a person's review remains, say so before you wait.
