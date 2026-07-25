# Orchestra

Orchestra is a Codex-native, cost-efficient, multi-agent software-delivery workflow.

It helps an individual developer move an explicitly activated Orchestra request
from exploration or a candidate specification through confirmation, planning,
and reviewed delivery. Direct implementation and any planning-only host mode
remain separate. Orchestra starts only from an explicit `$orchestra` invocation
or an unequivocal imperative to use or start Orchestra. The root orchestrator
acts as the technical lead: it confirms the specification, selects a standard
or critical workflow, composes focused capabilities with four base agent
profiles, resolves ordinary blockers, and makes the final technical judgment.
The user remains the product owner and final authority.

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

Orchestra starts only from explicit activation. It reuses the conversation,
classifies any prior candidate checkpoint, confirms a compact specification,
creates a new branch and dedicated sibling worktree for the formal task, and
may adopt scoped prior work into that worktree without mutating the source
checkout. After approval it scales implementation, review, and verification to
task risk. It supports both direct local integration and GitHub PR delivery
when repository policy and user authority allow them.

The four profiles are `analyst`, `implementation_worker`, `reviewer`, and
`verifier`. The root selects explicit capability assignments and their
applicable internal references; public skill names stay stable. The approved
formal plan is written directly as `active` to one root-owned, unversioned path
resolved by `git rev-parse --git-path orchestra/plan.md`. Provisional specs and
unapproved plans are not persisted. Git, not the plan, remains authoritative
for code and history. Safe local integration or an authorized PR merge removes
only the exact clean task resources; `hold` and unmerged work remain available.

Each consumer repository declares that choice in `orchestra.toml`. Missing
policy is never inferred: Orchestra asks once and recommends `hybrid`. Configured
verification uses ordered argument arrays, not shell command strings.

The source repository is authoritative. Runtime resources are installed through
repository-driven direct sync, with one owner for managed files and no changes
to unrelated Codex configuration.

## Direct sync

Run synchronization explicitly from a trusted Orchestra checkout. It is outside
ordinary task execution:

```sh
python3 codex/scripts/sync.py status --modelconfig native
python3 codex/scripts/sync.py apply --dry-run --modelconfig native
python3 codex/scripts/sync.py apply --modelconfig native
python3 codex/scripts/sync.py status
python3 codex/scripts/sync.py apply
python3 codex/scripts/sync.py uninstall
```

Choose `native` or `external` on the first apply. The install manifest records
that global choice, so later status and apply calls may omit `--modelconfig`.
Passing the other value previews or applies an atomic configuration switch.
Do not switch configurations while an Orchestra task is active: every dispatch
reads the one installed runtime matrix.

Skills and their internal playbook references install under
`$HOME/.agents/skills/`. Four agent profiles install under
`$CODEX_HOME/agents/`; capability assignments and runtime helpers install under
`$CODEX_HOME/orchestra/`. When `CODEX_HOME` is unset it defaults to
`$HOME/.codex`. The tool owns only destinations recorded in
`$CODEX_HOME/orchestra/install-manifest.json` and the exactly marked Orchestra
block in `$CODEX_HOME/AGENTS.md`. Only the selected source matrix is installed,
always at `$CODEX_HOME/orchestra/roles.toml`.

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
