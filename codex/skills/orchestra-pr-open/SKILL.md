---
name: orchestra-pr-open
description: Use when the user asked for a PR and the delivery policy allows one; opens or updates the task's single PR with a human body and one PR-CONTEXT capsule.
---

# Open or update the PR

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Publish the finished task as one PR that a reader understands and that later
triage can judge. Authority and the loop after opening are WORKFLOW "PR path".

## Steps

1. Inspect the complete `base..HEAD` range and diff. Stop if the base, head or
   range is ambiguous.
2. Write two temporary files outside the repository:
   - the human body, following
     [writing for readers](../orchestra/references/architecture_guidance.md#writing-for-readers);
   - the capsule's intent, read from the approved plan and phase documents
     rather than recalled, with the fields "PR path" lists.
3. Run `python3 "${ORCHESTRA_RUNTIME_ROOT}/scripts/pr.py" open --repo <root>
   --repository <OWNER/REPO> --base <base> --head <head>
   --expected-task-revision <terminal-sha> --title <title> --body-file <body>
   --context-file <intent> --authorized`. It refuses a head other than the
   completed plan's terminal phase commit, publishes the branch and reads back
   the remote head and body.
4. Require `ok` and exactly one `PR-CONTEXT` capsule. The helper keeps human
   edits to the body and replaces only the capsule.
5. Delete the temporary files and continue with
   [orchestra-pr-review](../orchestra-pr-review/SKILL.md).

## Report

The PR URL, its head and the helper's status.
