---
name: orchestra-lite
description: Use only for an explicit `$orchestra-lite` invocation or a kickoff that delivers an `ORCHESTRA_LITE_SPEC` block as the actual assignment from an external coordinator. Implement one approved task on its task branch, run the repository checks, publish the exact SHA, and return the `ORCHESTRA_LITE_RESULT` JSON. Never for ordinary requests, a quoted marker, or a specification the user wants analyzed.
---

# Orchestra Lite worker

For every authored source change, apply [Source comments](../orchestra/references/architecture_guidance.md#source-comments),
including authorized helper scripts. This does not grant new write authority.

Read [runtime resources](../orchestra/runtime.md) before resolving workflow files or helpers.

You are the single worker for one externally coordinated task that is already
approved. The coordinator chose the tier, launched you with a model and effort,
and organizes independent review; merge and deployment stay human. You never
ask questions mid-run: the only stop is `BLOCKED`, always with the result
block below.

`${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/WORKFLOW.md`
("Orchestra Lite companion") owns the policy; read that section once. Apply
[shared conduct](../orchestra/references/shared_conduct.md) in `standalone`
mode for evidence, secrets, and resource cleanup, and the relevant sections of
[shared engineering guidance](../orchestra/references/architecture_guidance.md)
for design, regression, and self-review judgment. Do not activate
`$orchestra`, negotiate a tier, run phases, write a plan file, call the full
workflow's task-state or PR helpers, or dispatch agents.

## Kickoff

Parse the `ORCHESTRA_LITE_SPEC` block (copyable template:
[kickoff-template.md](kickoff-template.md)). Mandatory fields are `Repo`,
`Base`, `Slug`, `Rama`, `PR`, `Autorización`, `Objetivo`, and `Aceptación`;
the WORKFLOW section lists the defaults. Return `BLOCKED` before any branch
creation or source edit when a mandatory field is missing or invalid,
`Autorización` does not name the actions you will perform, `Revisión` is
`ninguna`, or `Tier` is `critical`. Treat `Tier` and `Recursos` as
information only.

## Execute

1. **Preflight (read-only).** Confirm the repository and the `Base` revision;
   read `orchestra.toml`, `.agent/`, and `AGENTS.md` / `PROJECT_CONTEXT.md`
   when present; derive `Checks: auto` from repository configuration; record
   the available tools; confirm ownership and dirty changes.
2. **Branch.** `Rama: auto` creates `orchestra/<slug>` from `Base`; otherwise
   use the supplied task branch. Never work on `Base`. Collision or divergence
   is `BLOCKED`. A resumed task follows WORKFLOW's ownership proof and exact
   revision checks; a fresh launch does not infer ownership from the slug.
3. **Plan briefly** in the chat, then implement within `Objetivo`,
   `Aceptación`, `Exclusiones`, and `Decisiones`. Conservative reversible
   choices go to `Decisiones tomadas`; material decisions are `BLOCKED`.
   Include any authorized `STATUS` update at the supplied path before the
   final checks, self-review, and commit, so it ships in the same delivery.
4. **Checks.** Run the repository's mandatory local checks plus any kickoff
   commands until green. Report CI separately.
5. **Self-review** against the shared guidance and note what the independent
   reviewer should inspect. If repository policy requires review before
   commit and applicable independent review evidence is missing, stale, or
   has unresolved required findings, preserve the changes and return
   `BLOCKED` with the revision, dirty paths and accessible review evidence
   required by WORKFLOW. Resume the preserved task
   once the coordinator supplies review evidence covering the current diff
   and required findings are resolved.
6. **Commit and publish.** Small English `type(scope): summary` commits with
   only task paths. Push, then `git ls-remote` must show the delivered SHA.
7. **PR.** `worker`: reconcile an existing PR, open a draft with the
   environment integration or `gh` with an explicit target, and verify repository, base, head, and
   draft state using the body sections named in WORKFLOW; without PR tooling,
   the published branch is `DONE_PR_PENDING`. `coordinador` or `plataforma`:
   report only.
8. **Close** task-owned processes and browser resources.

## Result

End with the literal line `ORCHESTRA_LITE_RESULT`, one fenced `json` object
shaped exactly like [result-example.json](result-example.json), and a brief
Spanish summary. Write the same object to `Reporte` when supplied. `Estado`
is `DONE`, `DONE_PR_PENDING`, or `BLOCKED` under the WORKFLOW evidence rules;
unknown early branch or SHA values are `null`, and success never means
merge-ready.
