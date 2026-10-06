---
name: orchestra-repo-readiness
description: Use only for an explicit `$orchestra-repo-readiness` invocation or an unequivocal request to prepare, onboard, audit or repair an existing repository so agents can work in it reliably, including test-suite cleanup and its tracked `.agent/` conventions. Do not use for a greenfield idea, for ordinary mentions of conventions or cleanup, or as a substitute for `$orchestra`.
---

# Prepare a repository for agents

Bring an existing repository to a state a less capable agent can rely on by
fixing the environment, not by adding instructions. Never build product
features or activate the full workflow.

Read [runtime resources](../orchestra/runtime.md). WORKFLOW "Repository
readiness" owns scope and authority; "Repository conventions" owns `.agent/`
policy writes. Every authored source change follows
[source comments](../orchestra/references/architecture_guidance.md#source-comments).

## Target state

Check each item by running something, not by reading alone.

1. **Setup.** One documented command prepares a fresh clone or worktree,
   including dependencies, browsers and local services.
2. **Clean gates.** The hard gates are literal commands that pass at the
   inspected revision and leave `git status` clean.
3. **Deterministic gates.** The full suite passes repeatedly, on a second
   machine or a different worker count, and while another checkout of the
   repository runs it on the same machine. A failure that appears only there,
   or a gate that stops or reuses another checkout's services, is a finding.
4. **Green baseline.** Lint, type and format checks pass before any change, so
   a red result always belongs to the current change.
5. **Isolated, readable tests.** No test or module depends on state another
   leaves behind. Existing tests are short and assert what a user observes; a
   test that still passes when its subject returns nothing is a finding.
6. **Runnable in isolation.** An agent can start the application with its own
   data, configuration, ports and test credentials, never the user's profile or
   running services, drive one mapped journey and keep the evidence. Build the
   launcher and feature map with [project verification](../orchestra-project-verification/SKILL.md).
7. **Structure over words.** Agents see only the files they open, copy the
   nearest example and take the shortest path that compiles. So: one way per
   recurring task, one owner per piece of state, lists derived from one source
   instead of synced by hand, internals that other modules cannot import, and
   no workaround comments to copy.
8. **Enforced rules.** `.agent/` keeps one table pairing each rule with what
   enforces it (structure, type, lint, test, CI) plus the hard gates with exact
   argv and cwd. Prose remains only for judgment calls nothing can check.

## Diagnose

Diagnosis is the default. With execution authority from the brief, run setup
and gates for items 1 to 6, on a clean box from the user's fleet when one is
available; use `orchestra_analyst` with `repository_context` for a large
repository. Report each item as pass, fail or not checked, with command,
revision, machine and observed output, separating observation from inference.
Sampled inspection never certifies the whole repository.

## Repair

Repair needs a grant that names the area or items. Fix by leverage: make the
failure impossible through structure or data model, then a type, then a lint
whose error names the fix, then a test, and text last. Prove each new check
fails on a real past instance and passes a valid case; when the pattern is
already common, fail only on additions. Rerun the item check that failed.

Keep each coherent problem's code, tests and docs in one change with one owner,
and preserve independent implementation review through
[engineering](../orchestra-engineering/SKILL.md). For suite cleanup use
[test maintenance](../orchestra/references/architecture_guidance.md#test-maintenance)
and [behavioral verification](../orchestra/references/architecture_guidance.md#behavioral-verification).
Report product defects found while verifying; fix them only inside the grant.
Do not reorganize folders, rename for taste, sweep formatting or upgrade
dependencies incidentally.

## Conventions

Read existing `.agent/` first and change only stale, contradicted or missing
entries. Ask what evidence cannot settle in one batched question with
defaults. Before writing policy or running a new environment, present one
summary of paths, branch, commands, data and cleanup, and get confirmation
unless that summary is already approved.

## Hand off

Return the item table, the commits with what each fixed, remaining failures as
proposals, and the command that reruns the diagnosis. Do not push, merge or
open a pull request without delivery authority.

## Recurring mistakes

Run this when asked, or when a mistake class appears twice in commits, reverts
or review findings. Group the instances, repair each class at the highest level
above, and add its row to the rule table. A rule already in the table without an
enforcer that failed again is repaired the same way. Drop a rule once its
mistake can no longer happen.
