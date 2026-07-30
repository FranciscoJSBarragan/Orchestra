# Orchestra

Orchestra is a Codex-native, cost-efficient, multi-agent software-delivery workflow.

It helps an individual developer move from an idea or an explicitly activated
Orchestra request through a runnable foundation, confirmed specification,
planning, implementation, review, verification, and authorized delivery. Direct
implementation and any planning-only host mode remain separate.

`orchestra-project-start` may activate implicitly for a new project, empty
directory, stack decision, or idea without a repository. It prepares a small
runnable foundation after confirmation, then offers Orchestra without silently
activating it. The full Orchestra workflow starts only from an explicit
`$orchestra` invocation or an unequivocal imperative to use or start Orchestra.
The root acts as technical lead, recommends a tier, composes focused
capabilities, resolves ordinary blockers, and makes the final technical
judgment. The user chooses the tier and remains the product owner and final
authority.

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
classifies any prior candidate checkpoint, recommends a standard or critical
tier, and creates one collision-free `orchestra/<task-slug>[-N]` branch in a
dedicated Git worktree under a portable Orchestra root before repository
analysis. Every formal task
uses that isolated checkout regardless of the CLI or host that activated
Orchestra. It supports hold, PR, or local integration when policy allows.

After plan approval, Orchestra scales implementation, review, and verification
to the active tier. The user may direct a safe tier change in either direction
without restarting the workflow or discarding valid work. Tier choice changes
model and scrutiny intensity; it never waives separate authority for production,
security, payments, destructive operations, merge, release, or deployment.

The four profiles are `orchestra_analyst`,
`orchestra_implementation_worker`, `orchestra_reviewer`, and
`orchestra_verifier`. Namespacing prevents Orchestra from intercepting ordinary
Codex agents. The root selects explicit capability assignments and their
applicable internal references. The approved
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

## First task quickstart

For an existing repository:

1. Ask: `Use Orchestra to add <visible behavior>.`
2. Orchestra summarizes the brief, recommends a tier with its cost-benefit, and
   asks you to choose the tier.
3. It creates an isolated worktree under
   `${ORCHESTRA_WORKTREE_ROOT:-$HOME/.orchestra/worktrees}`, inspects it, and
   proposes observable
   acceptance, and asks you to confirm the final specification and
   implementation plan.
4. After approval it implements, verifies, reviews, and commits accepted phases.
5. It reports `implementation complete; delivery pending` and asks whether to
   hold, open a PR, or integrate locally when repository policy allows.

For a new project, describe the idea normally. `orchestra-project-start`
activates implicitly, helps select a proportional stack, confirms the target
location and mutations, creates a runnable vertical foundation, and offers to
continue through Orchestra. Accepting that offer explicitly activates the full
workflow without repeating the greenfield discovery.

Use direct implementation instead when the change is small and you do not want
formal planning, independent review, phase commits, or delivery coordination.

## Prerequisites

- Python 3 for source synchronization and validation.
- Git for task branches, plans, commits, and worktrees.
- The project runtime and dependency manager needed by the consumer repository.
- GitHub CLI only when using PR delivery.
- Required local services and credentials for the project; Orchestra identifies
  their categories but does not print or persist secret values.

Choose `native` for the supported Codex model assignments. Choose `external`
only when the configured external providers and model identifiers are available
in the current Codex environment. The selection is global for the installed
runtime and may be switched explicitly when no Orchestra task is active.

## Direct sync

Run synchronization explicitly from a trusted Orchestra checkout. It is outside
ordinary task execution:

```sh
python3 codex/scripts/sync.py status --modelconfig native
python3 codex/scripts/sync.py apply --dry-run --modelconfig native
python3 codex/scripts/sync.py apply --modelconfig native
python3 codex/scripts/sync.py apply --modelconfig native --worktree-root /absolute/path
python3 codex/scripts/sync.py status
python3 codex/scripts/sync.py apply
python3 codex/scripts/sync.py uninstall
```

Choose `native` or `external` on the first apply. The install manifest records
that global choice, so later status and apply calls may omit `--modelconfig`.
Passing the other value previews or applies an atomic configuration switch.
Do not switch configurations while an Orchestra task is active: every dispatch
reads the one installed runtime matrix.

The optional `--worktree-root` overrides `ORCHESTRA_WORKTREE_ROOT`; otherwise
sync uses `$HOME/.orchestra/worktrees`. Sync writes the effective absolute path
to `$CODEX_HOME/orchestra/worktree-root`. Before changing Codex configuration,
sync requires a readable `codex --version`. Codex 0.138 and later use the
managed `orchestra-workspace` permission profile; older clients use only the
legacy `workspace-write` sandbox. Upgrades and downgrades migrate atomically
so exactly one backend remains active, and uninstall restores the original
configuration.

Both backends authorize `$HOME/.orchestra`, any validated external worktree
root, and the exact Poetry, pip, uv, and npm cache roots reported by installed
tools. Tool discovery runs from an isolated temporary directory, rejects broad
or sensitive paths, and writes only absolute paths. Public command networking
and explicit loopback destinations are enabled, while broad private-network
access, Docker configuration, and Unix sockets remain excluded. User-owned
`sandbox_mode`, `sandbox_workspace_write.network_access`,
`default_permissions`, conflicting permission profiles, or incompatible
writable roots block synchronization without changing the file. Automatic
backend migration is limited to configuration already recorded as
Orchestra-owned.

Restart the Codex host after a permission change so new agent sessions receive
the selected backend. Re-run sync after installing another supported package
tool. Status and apply results report `codex_version`, `permission_backend`,
`permission_profile`, `profile_configured`, `sandbox_root`, detected
`cache_roots`, coarse `omitted_cache_tools`, `unconfigured_cache_tools`, and
`restart_required`. Cache access does not install project dependencies or make
an empty virtual environment ready for tests.

Sync results use:

- `ok`: requested state is complete.
- `partial`: no unsafe mutation occurred, but setup, cleanup, or requested state
  is incomplete; read `detail` and the reported changes.
- `blocked`: safety, ownership, drift, configuration, or validation prevented
  the operation; resolve the named blocker before retrying.

Eight skills and their internal playbook references install under
`$HOME/.agents/skills/`. Four agent profiles install under
`$CODEX_HOME/agents/`; capability assignments and runtime helpers install under
`$CODEX_HOME/orchestra/`. When `CODEX_HOME` is unset it defaults to
`$HOME/.codex`. The tool owns only destinations recorded in
`$CODEX_HOME/orchestra/install-manifest.json` and the exactly marked Orchestra
blocks in `$CODEX_HOME/AGENTS.md` and `$CODEX_HOME/config.toml`. Only the
selected source matrix is installed, always at
`$CODEX_HOME/orchestra/roles.toml`.

Before replacing or removing an existing owned destination, the tool writes one
current deterministic safety backup under `$CODEX_HOME/orchestra/backups/`.
Backups are not restoration history: uninstall removes only content whose digest
still matches the manifest, preserves drifted or unrelated content, and never
restores unrelated user configuration.

## Coordination CLI

Direct sync installs a fail-soft coordination helper at
`$CODEX_HOME/orchestra/scripts/coordination.py`. Orchestra uses it to expose
multiple active tasks, material agent activity, and revision-identified
Markdown artifact locators without making telemetry authoritative:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/coordination.py" task list
python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/coordination.py" task show --task <uuid>
python3 "${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/coordination.py" artifact list --task <uuid>
```

The helper lazily creates `$HOME/.orchestra/state.sqlite3` with mode `0600`.
An empty version-zero file is safely bootstrapped, while a partial, unknown, or
corrupt database remains untouched and returns `unavailable`. Artifact content
lives in each task worktree's private Git metadata. Commands return JSON and
use `invalid` or `unavailable` for coordination failures. Those results never
grant authority, validate phase transitions, or block an otherwise authorized
tier change, implementation, commit, or delivery; agents fall back to complete
inline reports and current source.

Completed task metadata remains queryable. Worktree cleanup may make old
artifact locators unavailable. Sync and uninstall manage the helper but never
own or remove the database. There is no daemon, HTTP server, MCP server, global
executable, event ledger, heartbeat system, or dashboard in this version.

Artifacts are the semantic handoff channel across context, planning,
implementation, verification, debugging, and review. Formal planning publishes
one `plan-overview` and one `plan-phase` per phase; the approved private
`plan.md` preserves the overview and exact phase IDs and paths. Agents receive
explicit authority plus exact document references and new deltas instead of a
root-authored summary chain. Git and GitHub remain authoritative for code,
commits, PR checks, and merge.

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
