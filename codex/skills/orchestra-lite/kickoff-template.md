# Kickoff template

Copy the block below into the worker's first message. Field names are fixed
and Spanish; give every mandatory field a value, omit optional
fields you do not need, and never quote this block inside documentation you
want the worker to analyze. The policy for every field is in WORKFLOW
"Orchestra Lite companion".

Resolve material acceptance choices and required-check readiness before dispatch,
using WORKFLOW "Engineering guidance and evidence". Put settled decisions and
any explicitly authorized exceptions in the existing `Decisiones` field; the
template adds no decision-review mode or result version.

```text
ORCHESTRA_LITE_SPEC
Versión: 2
Repo:
Base:
Slug:
Rama: auto
PR:
Tier:
Recursos:
Autorización: implementar, commit, push, abrir borrador
Objetivo:
Aceptación:
-
Exclusiones:
-
Decisiones:
-
Checks: auto
Revisión: coordinador
Actualizar STATUS: no
Mapa:
Reporte:
```

| Field | Required | Value |
| --- | --- | --- |
| `Versión` | no | `2` (default for this worker); another requested version blocks before mutation |
| `Repo` | yes | GitHub `owner/name`; must match the checkout's origin |
| `Base` | yes | base branch |
| `Slug` | yes | kebab-case task slug |
| `Rama` | yes | `auto` (worker creates `orchestra/<slug>`) or the task branch the platform already created |
| `PR` | yes | `worker`, `coordinador`, or `plataforma`: who opens the draft PR |
| `Tier` | no | `minimal` or `standard`, informational; `critical` blocks and belongs to `$orchestra` |
| `Recursos` | no | model and effort the worker was launched with, informational |
| `Autorización` | yes | explicit list of the actions granted; trim it to what is actually authorized |
| `Objetivo` | yes | one to three sentences |
| `Aceptación` | yes | verifiable criteria, one per line |
| `Exclusiones` | no | what not to touch; empty by default |
| `Decisiones` | no | decisions already taken; name the absolute resolution root when `Mapa` or `Reporte` is relative; for a fresh-worker continuation include ownership, expected full branch SHA and the original `Base.Referencia` / `Base.SHA` from the prior result under WORKFLOW; empty by default |
| `Checks` | no | `auto` (default) or explicit commands, one per line; repository-mandatory checks remain required unless explicitly excepted in `Decisiones` under WORKFLOW's authority and reporting rules |
| `Revisión` | no | `coordinador` (default) or `bugbot`; `ninguna` is rejected |
| `Actualizar STATUS` | no | `no` (default) or `sí` followed by the status file path to include in the delivered commit range before final checks and review |
| `Mapa` | no | readable decision-evidence input path, absolute or relative to the absolute context root named in `Decisiones`; omitted means establish applicable evidence in the result |
| `Reporte` | no | task-owned output path for the same final JSON, absolute or relative to the absolute context root named in `Decisiones`; omitted means chat only |
