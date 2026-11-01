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
2. Before the first clean result the complete range needs the terminal review
   WORKFLOW "Review policy" requires. A single-phase task's phase review
   already is it; for a multi-phase task, dispatch the baseline review of the
   whole range now, as the review pair.
3. Triage everything actionable. Dispatch the `independent_review` row the plan
   recorded only for feedback whose validity needs investigation, with
   PR-CONTEXT, the current diff and evidence, the feedback and only the new
   delta.
4. Send accepted items to a fresh session of the implementation owner under
   WORKFLOW "Phase execution". After its delta review, commit through
   [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md), push and
   refresh the capsule through [orchestra-pr-open](../orchestra-pr-open/SKILL.md).
5. Resolve a thread by its ID once its fix is pushed or triage rejected it with
   evidence. A resolution without a push brings no wake, so observe again at
   once.
6. Act on what the observation still shows:
   - failed checks or accepted feedback: back to step 4;
   - a conflict, or a base the branch must catch up with: WORKFLOW "Base
     refresh before delivery";
   - more threads or comments than the helper reads in one page: `blocked`,
     since a wake cannot complete them;
   - a merge state GitHub is still computing: observe once more before
     deciding, since no watcher event follows it;
   - pending checks, a bot review in progress or a person's review: watch the
     PR as
     [T3 Code](../orchestra/references/host_t3.md#pull-requests) defines and
     end your turn. On a wake, start again at step 1.

## Ask only if

Feedback asks for a visible change the user did not approve, or triage reaches
a decision the approved intent does not settle.

## Report

`ok` after one complete clean observation of the current head, with the head,
the checks and the review rounds. Otherwise `partial` or `blocked` with what
remains; when only a person's review remains, say so before you wait. With
merge authority, continue with [orchestra-pr-merge](../orchestra-pr-merge/SKILL.md).
