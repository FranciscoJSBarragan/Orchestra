---
name: orchestra-repo-onboard
description: Use only for an explicit `$orchestra-repo-onboard` invocation or an unequivocal request to onboard an existing repository into Orchestra by analyzing it and writing its tracked `.agent/` conventions (hard gates, prerequisites, normative code conventions). Also use to refresh a stale `.agent/` store. Do not use for a greenfield idea, for ordinary mentions of conventions, or as a substitute for `$orchestra`.
---

# Onboard an existing repository

For every authored source change, apply [Source comments](../orchestra/references/architecture_guidance.md#source-comments),
including authorized helper scripts. This does not grant new write authority.

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

Turn one existing repository into a place where Orchestra workers stop
rediscovering the same facts: verify how the project is really built, tested,
and structured, ask the user only what evidence cannot settle, and write a
short tracked `.agent/` store. This lane never implements product changes and
never activates the full Orchestra workflow.

## Establish the boundary

Inspect the target directory read-only. Require meaningful application code
under Git; for an idea, an empty directory, or a stack decision, stop and let
`orchestra-project-start` handle it. If the user wants planned delivery of a
change, stop and let them invoke `$orchestra`. Read
`${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/WORKFLOW.md` ("Repository conventions")
for the taxonomy and the authority rules that every `.agent/` write obeys.

When `.agent/` already exists, run in refresh mode: read it first and produce
only deltas — stale, contradicted, or missing entries — never a rewrite.

## Analyze with bounded evidence

Use the `orchestra_analyst` profile with the `repository_context` capability,
or perform the same bounded reading directly when the repository is small. Ask
only these questions, each answered with exact paths and the inspected
revision:

- canonical setup, run, test, lint, type-check, and build commands, from
  Makefile, CI, package manifests, and scripts, plus which of them the project
  treats as mandatory before merge;
- runtime and dependency expectations, required services, credential
  categories without secret values, test-data provenance, generated paths;
- existing `AGENTS.md`, contributor docs, linters, and formatters, so that
  nothing they already enforce is repeated;
- the real layering and ownership boundaries the code demonstrates, the
  dominant patterns for the surfaces the project has (persistence, API, UI,
  jobs), the test style actually used, and pinned libraries whose replacement
  would be a decision;
- delivery policy in `orchestra.toml`, present or missing.

Separate observed facts from inferences. Do not inventory the repository,
install dependencies, run mutating commands, or start planning a change.

When existing commands leave a material acceptance gap, assess the missing
parts using [shared engineering guidance](../orchestra/references/architecture_guidance.md)
("Verification recipes"). Cite maintained project instructions and distinguish
source-backed commands from runs actually observed at a named revision. Record
unresolved prerequisites or execution as such. Analysis remains read-only.
Offer [project verification](../orchestra-project-verification/SKILL.md) when a
feature map, interaction helper or proven journey would close the gap. Include
its exact writes, safe data, execution and cleanup in the confirmation below;
only after that boundary may onboarding execute the authorized recipe. Include
a fresh-agent reproduction when proving the handoff is part of that scope;
a verified command alone does not demonstrate a complete user journey.

## Ask only what evidence cannot settle

Batch the questions into one consolidated request. Ask only when an answer
changes how agents must work in this repository: whether an observed pattern is
normative or historical accident; which commands are hard gates versus
diagnostics; explicit prohibitions and forbidden substitutions; the delivery
policy when `orchestra.toml` lacks one. Offer the evidence-backed default for
each question. Do not ask about preferences that a linter, formatter, or
existing document already settles.

## Admit only what earns its place

A candidate entry qualifies when a competent agent reading the code would
otherwise get it wrong, and its evidence or the user's answer supports it.
Reject general engineering principles, restatements of tooling defaults, facts
the code demonstrates on its own, task or branch state, secrets, and personal preferences. Descriptive setup and
verification entries qualify when they have the concrete future consumer and
proof level defined by WORKFLOW "Project verification". Prefer fewer, shorter files.
Every hard gate names its exact argv and cwd. Every convention is one to three
sentences with the reason or the failure it prevents.

## Confirm, write, verify

Present one mutation summary: exact policy and operational-documentation paths,
any needed verification helper, the branch, commands, data and cleanup. Require
explicit confirmation before writing or running the proposed environment;
existing explicit approval of that same summary satisfies the boundary.
On confirmation, write only those files on the agreed task branch, execute the
authorized representative journey and repository hard gate when present, read
the results, and commit under the repository's review policy. Preserve draft
labels for recipes that could not run; do not implement product fixes merely
because verification discovered them. Do not push, merge, open a PR, or write `orchestra.toml`
unless the user chose the delivery policy in the same confirmation.

## Hand off

Return the written paths with a one-line summary each, the commands verified
and their observed results, any question left unresolved, and the branch and
commit. Then note that `$orchestra` will read the store on its next task in
this repository. Do not activate `$orchestra` automatically.
