# Kickoff template

Copy the block below into the worker's first message. Field names are fixed
and Spanish; give every mandatory field a value, omit optional
fields you do not need, and never quote this block inside documentation you
want the worker to analyze. The policy for every field is in WORKFLOW
"Orchestra Lite companion".

```text
ORCHESTRA_LITE_SPEC
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
Reporte:
```

| Field | Required | Value |
| --- | --- | --- |
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
| `Decisiones` | no | decisions already taken; for a fresh-worker continuation include the existing branch ownership and expected full SHA under WORKFLOW; empty by default |
| `Checks` | no | `auto` (default) or explicit commands, one per line; repository-mandatory checks always run |
| `Revisión` | no | `coordinador` (default) or `bugbot`; `ninguna` is rejected |
| `Actualizar STATUS` | no | `no` (default) or `sí` followed by the status file path to include in the delivered commit range before final checks and review |
| `Reporte` | no | absolute path where the final JSON is also written; omitted means chat only |
