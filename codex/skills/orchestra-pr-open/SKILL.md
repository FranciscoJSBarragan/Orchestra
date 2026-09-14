---
name: orchestra-pr-open
description: Create or update one authorized Orchestra pull request from the complete base..HEAD commit range. Use after delivery policy and explicit open-PR direction are settled, when the root must preserve the human PR body and upsert exactly one compact PR-CONTEXT capsule without granting merge authority.
---

# Open or update one PR

The root owns PR intent synthesis and directly invokes the PR helper; PR opening is not a profile or capability assignment. Require explicit repository, base, head, title, human body, exact revision, approved `plan.md` manifest, exact overview and completed phase artifact identifiers, validation reports, and known risks. Read objective, acceptance, invariants, and phase intent from those exact documents rather than a root-authored replay.

## Execute the PR-open contract

1. Confirm [orchestra-delivery-policy](../orchestra-delivery-policy/SKILL.md) authorized the PR lane and the user requested `open PR` or equivalent.
2. Inspect the full `base..HEAD` commit range and diff. Stop if base, head, or range is missing or ambiguous.
3. Write the human body and compact intent to temporary files outside the repository and arrange cleanup.
4. Resolve the terminal phase commit from the completed manifest and publish the
   intended branch at that exact revision. Have the root directly run `python3
   "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/pr.py" open --repo <root>
   --repository <OWNER/REPO> --base <base> --head <head>
   --expected-task-revision <manifest-sha> --title <title> --body-file
   <body-file> --context-file <context-file> --authorized`. The helper must
   reload policy, allow only `pr-required` or `hybrid`, require the supplied
   head to match the terminal manifest revision before any `gh` command, and
   read back the published remote head and PR body.
5. Require `ok` and exactly one `<!-- PR-CONTEXT:start -->...<!-- PR-CONTEXT:end -->` capsule. The helper preserves human content and replaces any existing capsule.
6. Remove the temporary files, then route the open PR to [orchestra-pr-review](../orchestra-pr-review/SKILL.md). The PR must receive an independent code review before a clean delivery result, even when GitHub has no actionable feedback; feedback adds delta review rather than replacing the baseline review.

The PR body is the only lifecycle for PR-CONTEXT: upsert it while the PR is open and leave closure history to GitHub. Do not create local context or PR state files. Do not merge, release, deploy, or infer authority.
