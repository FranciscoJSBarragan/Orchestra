---
name: orchestra-repo-readiness
description: Use only for an explicit `$orchestra-repo-readiness` invocation or an unequivocal request to prepare, onboard, audit or repair an existing repository so agents can work in it reliably, including test-suite cleanup and its tracked `.agent/` conventions. Do not use for a greenfield idea, for ordinary mentions of conventions or cleanup, or as a substitute for `$orchestra`.
---

# Prepare a repository for agents

Agents copy what a repository shows them and trust what its checks report.
Bring an existing repository to a state a less capable agent can rely on by
fixing the environment, not by adding instructions. This skill never builds
product features and never activates the full workflow.

Read [runtime resources](../orchestra/runtime.md). WORKFLOW "Repository
readiness" owns scope and authority; "Repository conventions" owns `.agent/`
policy writes. Every authored source change follows
[source comments](../orchestra/references/architecture_guidance.md#source-comments).

## Target state

Each item is checked by running something, never by reading alone.

1. **Setup.** One documented command prepares a fresh clone or worktree,
   including dependencies, browsers and local services.
2. **Clean gates.** The hard gates are literal commands that pass at the
   inspected revision and leave `git status` clean.
3. **Deterministic gates.** The full suite passes repeatedly and on a second
   machine or a different worker count. A failure that appears only there is a
   finding, not noise.
4. **Green baseline.** Lint, type and format checks pass before any change, so
   a red result always belongs to the current change.
5. **Isolated, readable tests.** No test or module depends on state another
   leaves behind. Existing tests are short and assert what a user observes; a
   test that still passes when its subject returns nothing is a finding.
6. **Runnable in isolation.** An agent can start the application with its own
   data, configuration, ports and test credentials, never the user's profile or
   running services, drive one mapped journey and keep the evidence. Build the
   launcher and feature map with [project verification](../orchestra-project-verification/SKILL.md).
7. **Structure over words.** One canonical way per recurring task, registries
   derived instead of hand-edited lists that every change touches, and no
   workaround comments that agents would copy.
8. **Short conventions.** `.agent/` holds only what still needs words: hard
   gates with exact argv and cwd, prerequisites, prohibitions and conventions
   whose violation the code cannot reject.

## Diagnose

Diagnosis is the default. With execution authority from the brief, run setup
and gates for items 1 to 6, on a clean box from the user's fleet when one is
available. Use the `orchestra_analyst` profile with `repository_context` for a
large repository. Report every item as pass, fail or not checked, with the
command, revision, machine and observed output. Separate observed facts from
inference. A healthy item needs no change, and sampled inspection never
certifies the whole repository.

## Repair

Repair needs a grant that names the area or items. Fix by leverage: make the
failure impossible through structure or data model first, then add a mechanical
check (type, lint, test, CI), and write `.agent/` text only for what neither can
express. Prove each repair against a bad and a valid case and rerun the item
check that failed.

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
entries. Admit an entry only when a competent agent reading the code would
otherwise get it wrong. Ask what evidence cannot settle in one batched question
with evidence-backed defaults. Before writing policy or running a new
environment, present one summary of paths, branch, commands, data and cleanup,
and get confirmation unless the same summary is already approved.

## Hand off

Return the item table, the commits with what each fixed, remaining failures as
proposals, and the command that reruns the diagnosis. Do not push, merge or
open a pull request without delivery authority. Later, when a review finding
recurs in this repository, route it back here as a check or a structural fix,
not as more text.
