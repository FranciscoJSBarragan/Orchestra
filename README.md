# Orchestra

Orchestra is a Codex-native, cost-efficient, multi-agent software-delivery workflow.

It helps an individual developer move a software change from a clear objective
to a reviewed, verified, and committed result. The root orchestrator acts as
the technical lead: it frames the problem, selects a proportional workflow,
composes focused capabilities with four base agent profiles, resolves ordinary
blockers, and makes the final technical judgment. The user remains the product
owner and final authority.

## Product sources

Product intent follows this precedence:

1. `VISION.md` defines mission, audience, principles, success, and non-goals.
2. `docs/WORKFLOW.md` defines behavior from request through delivery.
3. `docs/ARCHITECTURE.md` defines component and role boundaries.
4. `AGENTS.md` provides concise executable rules for agents.
5. Skills, profiles, scripts, tests, and hooks implement those sources.

Lower levels must not silently redefine higher levels. A deliberate product
change updates the relevant canonical document and its executable enforcement
together.

## Delivery model

Orchestra scales discovery, planning, implementation, review, and verification
to task risk. It supports both direct local integration and GitHub PR delivery
when repository policy and user authority allow them.

The four profiles are `analyst`, `implementation_worker`, `reviewer`, and
`verifier`. The root selects explicit capability assignments and their
applicable internal references; public skill names stay stable. Standard and
critical work use one root-owned, unversioned plan resolved by
`git rev-parse --git-path orchestra/plan.md`. Git, not the plan, remains
authoritative for code and history.

Each consumer repository declares that choice in `orchestra.toml`. Missing
policy is never inferred: Orchestra asks once and recommends `hybrid`. Configured
verification uses ordered argument arrays, not shell command strings.

The source repository is authoritative. Runtime resources are installed through
repository-driven direct sync, with one owner for managed files and no changes
to unrelated Codex configuration.

## Advisory Graphify lifecycle

For standard and critical planned repositories, the root uses Graphify by
default as advisory context. Read-only configuration/freshness checks and query
may run before approval. Missing command, required artifact boundary, or safely
repairable required hooks add one bootstrap phase; stale/pending evidence or
hook/query failure falls back to source as `partial` without another bootstrap.
Nothing mutates before plan approval. Light work never adopts Graphify
automatically.

Before hook status, detection canonicalizes `git rev-parse --git-dir` and
`git rev-parse --git-common-dir`. When they differ, native hook refresh is
unsupported for that linked worktree: it preserves common hooks, records hook
automation as `partial`, and skips status, install, reinstall, uninstall,
wrappers, alternate hooks, and hook-only bootstrap. When the command exists, it
still checks relevant Git delta and pending evidence before query smoke; a graph
proven fresh at HEAD is usable advisory context, otherwise source is
authoritative. When the command is missing, it adds bootstrap and uses source
because query cannot run. Artifact configuration may also authorize that
bootstrap, with its hook step skipped. Only an eligible non-linked worktree with the command
available executes `graphify hook status` exactly once; it does not call hook
status twice.

Approved bootstrap uses `uv tool install --upgrade graphifyy`, one complete
`graphify .` build, and repository ignore/versioning changes. The root reviews,
verifies, and commits that initial snapshot before running
`graphify hook install`, then reruns active detection. Exactly
`graphify-out/graph.json`, `graphify-out/graph.html`, and
`graphify-out/GRAPH_REPORT.md` are versioned;
`manifest.json`, `cost.json`, and other generated data remain ignored. Before
installing hooks, the root first proves the worktree is non-linked and resolves
Git's actual destination including `core.hooksPath`. A linked worktree,
destination inside the tracked worktree, or installation that would modify a
tracked hook is preserved as `partial`; no wrapper or alternate hook is
created. Only safely untracked, installation-local hooks may be treated as
clone-local, reinstalled after cloning, or removed with
`graphify hook uninstall`. Never use `graphify codex install`.

Before using a configured graph, unusable evidence falls back to source. After
functional phases, the root runs semantic
`graphify . --update` at most once before plan completion and creates one
graph-only commit only when tracked outputs changed. Graphify failure is
`partial` and never overrides Git, source, tests, runtime evidence, or
independent review. External credentials or material cost require separate user
authority.

## Direct sync

Run synchronization explicitly from a trusted Orchestra checkout. It is outside
ordinary task execution:

```sh
python3 codex/scripts/sync.py status
python3 codex/scripts/sync.py apply --dry-run
python3 codex/scripts/sync.py apply
python3 codex/scripts/sync.py uninstall
```

Skills and their internal playbook references install under
`$HOME/.agents/skills/`. Four agent profiles install under
`$CODEX_HOME/agents/`; capability assignments and runtime helpers install under
`$CODEX_HOME/orchestra/`. When `CODEX_HOME` is unset it defaults to
`$HOME/.codex`. The tool owns only destinations recorded in
`$CODEX_HOME/orchestra/install-manifest.json` and the exactly marked Orchestra
block in `$CODEX_HOME/AGENTS.md`.

Before replacing or removing an existing owned destination, the tool writes one
current deterministic safety backup under `$CODEX_HOME/orchestra/backups/`.
Backups are not restoration history: uninstall removes only content whose digest
still matches the manifest, preserves drifted or unrelated content, and never
restores unrelated user configuration.

## Conformance

Run the deterministic suite validator from the repository root:

```sh
python3 codex/scripts/validate_suite.py --quick
python3 codex/scripts/validate_suite.py --full
```

The versioned pre-commit hook invokes only quick validation. Full validation is
the manual and CI entry point.

Bootstrap, sync, and installation work do not invoke Orchestra itself. Model
benchmarking is deferred until the composable runtime works end to end.
