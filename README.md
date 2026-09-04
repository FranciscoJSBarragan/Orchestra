# Orchestra

Orchestra is a cost-efficient, multi-agent software-delivery workflow for Codex,
Cursor, and Grok Build.

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
classifies any prior candidate checkpoint, and recommends an available assigned
tier. Codex native offers standard and critical; Codex external additionally
offers Luna as a cost-focused opt-in for ordinary, bounded work when the user
explicitly prioritizes cost. Cursor offers minimal, standard, and critical with
no native/external mode; this cut assigns all three and recommends standard. Grok Build assigns standard and critical on grok-4.6 and has no cheaper tier. It then creates one collision-free
`orchestra/<task-slug>[-N]` branch before repository analysis. Managed mode
creates a dedicated Git worktree under a portable Orchestra root; opt-in hybrid
mode uses the current clean primary checkout or linked worktree and creates the
task branch there. Every formal task works only on its Orchestra branch and
supports hold, PR, or local integration when policy allows.

After plan approval, Orchestra scales implementation, review, and verification
to the active tier. The user may direct a safe tier change among the tiers
available assigned tiers without restarting the workflow or discarding
valid work. Tier choice changes model and scrutiny intensity; it never waives
separate authority for production, security, payments, destructive operations,
merge, release, or deployment.

The implementation owner runs and autocorrects required local deterministic
checks before handoff, including the canonical full suite when one exists. The
reviewer inspects intent, source, diff, tests, and fresh evidence without
routinely rerunning those gates. Orchestra
creates a separate verifier only for browser or runtime boundaries, mutable
data, credentials, network or external environments, explicit repository
policy, and critical work; critical phases retain independent double evidence.

The four profiles are `orchestra_analyst`,
`orchestra_implementation_worker`, `orchestra_reviewer`, and
`orchestra_verifier`. Namespacing prevents Orchestra from intercepting ordinary
host agents. The root selects explicit capability assignments and their
applicable internal references. The approved
formal plan is written directly as `active` to one root-owned, unversioned path
at `<task-worktree>/.orchestra/plan.md`. Semantic reports live beside it under
`.orchestra/artifacts`; the self-ignored task state stays outside Git history
and requires only normal workspace access. Provisional specs and
unapproved plans are not persisted. Git, not the plan, remains authoritative
for code and history. Safe local integration or an authorized PR merge removes
only the exact clean task resources; `hold` and unmerged work remain available.

Each consumer repository declares that choice in `orchestra.toml`. Missing
policy is never inferred: Orchestra asks once and recommends `hybrid`. Configured
verification uses ordered argument arrays, not shell command strings. Phase
conventions, when present, live in tracked `.agent/` files, including hard
gates and the repository's own normative code conventions; delivery checks stay
in `orchestra.toml`.

The source repository is authoritative. Runtime resources are installed through
repository-driven direct sync, with one owner for managed files and no changes
to unrelated host configuration.

## First task quickstart

For an existing repository:

1. Ask: `Use Orchestra to add <visible behavior>.`
2. Orchestra summarizes the brief, recommends a tier with its cost-benefit, and
   asks you to choose the tier.
3. It proposes observable acceptance and asks you to confirm the final
   specification and implementation plan (one message for simple tasks). After
   confirmation it creates an isolated worktree in `managed` mode, or a fresh
   task branch in the current clean checkout in opt-in `hybrid` mode.
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

Choose `dual` to expose both Codex native V2 and external V1 Orchestra routing.
The Codex root model selector then chooses the mode automatically for each new
Codex task: native Sol selects V2, while the Orchestra Sol compatibility alias
selects V1. Choose legacy `native` or `external` only when one fixed Codex
matrix is preferred. External assignments require their configured providers
and model identifiers. Dual mode also requires CodexBridge in `catalog` mode
with a refreshed catalog that publishes the reserved `orchestra-v1/` aliases.
Orchestra sync does not change or restart CodexBridge. Cursor ignores
`--modelconfig` and reads `hosts/cursor` or `hosts/grok` roles instead.

## Direct sync

Run synchronization explicitly from a trusted Orchestra checkout. It is outside
ordinary task execution:

```sh
python3 codex/scripts/sync.py status --modelconfig dual
python3 codex/scripts/sync.py apply --dry-run --modelconfig dual
python3 codex/scripts/sync.py apply --modelconfig dual
python3 codex/scripts/sync.py apply --modelconfig dual --checkout-mode hybrid
python3 codex/scripts/sync.py apply --host cursor
python3 codex/scripts/sync.py apply --host grok
python3 codex/scripts/sync.py apply --host all --modelconfig dual
python3 codex/scripts/sync.py status --modelconfig native
python3 codex/scripts/sync.py apply --modelconfig native --worktree-root /absolute/path
python3 codex/scripts/sync.py status
python3 codex/scripts/sync.py apply
python3 codex/scripts/sync.py uninstall
```

`--host` is `codex`, `cursor`, `grok`, or `all`. Default `codex` preserves
existing installs and does not write `~/.cursor` or `~/.grok`. Shared skills
still install under `$HOME/.agents/skills/` for any host. Choose `dual`, `native`, or `external` on
the first Codex apply. The install manifest
records that global choice, so later status and apply calls may omit
`--modelconfig`. Passing another value previews or applies an atomic
configuration switch. Do not switch the installed configuration while an
Orchestra task is active. Within `dual`, each task's automatically detected
`native` or `external` mode is immutable; changing protocol mode requires a new
task opened with the matching root model entry.

The optional `--worktree-root` overrides `ORCHESTRA_WORKTREE_ROOT`; otherwise
sync uses `$HOME/.orchestra/worktrees`. Sync writes the effective absolute path
to `${ORCHESTRA_HOME:-$HOME/.orchestra}/worktree-root` and, for Codex, also
mirrors it at `$CODEX_HOME/orchestra/worktree-root`. `--checkout-mode managed|hybrid`
selects the task-checkout strategy and is persisted at
`${ORCHESTRA_HOME:-$HOME/.orchestra}/checkout-mode` with a Codex compatibility
mirror; `managed` is the backward-compatible
default. Hybrid mode uses either the primary checkout or a linked worktree when
it is clean, but always creates a new `orchestra/*` branch before work and never
implements directly on `main`. Dirty, detached, conflicted, or otherwise
ambiguous checkouts require one explicit decision. Before changing Codex configuration,
sync requires Codex 0.146.0 or later. It installs the built-in `:workspace`
permission profile with `approval_policy = "on-request"` and
`approvals_reviewer = "auto_review"`. Older or unreadable clients block before
mutation. Historical manifest-owned Full Access and legacy blocks migrate
atomically, while uninstall remains version-independent and restores the
original configuration.

Guardian is the synchronized default, not a runtime requirement. An explicit
permission choice for the current task, host, or launcher remains authoritative;
Orchestra neither changes it nor blocks solely because it differs. When
Guardian is active, the workspace boundary permits routine repository work
while exact escalations for protected paths such as shared Git metadata are
reviewed automatically. Manual approvals may prompt the user, while Full Access
runs without that workspace sandbox boundary. Sync does not install a custom
permission profile, writable-root list, worktree helper, or command rule.
User-owned `sandbox_mode`, `default_permissions`, conflicting permission
profiles, or incompatible legacy sandbox tables block synchronization without
changing the file. Sync takes reversible ownership of `approval_policy`,
`approvals_reviewer`, and `default_permissions`; unrelated options such as
`web_search` are preserved byte-for-byte. Task Control never launches an
execution host or
changes permissions; adoption uses the current native chat's configured choice.

Restart the Codex host after a permission change so new agent sessions receive
the selected backend. Status and apply results report `codex_version`,
`permission_backend`,
`permission_profile`, `profile_configured`, `checkout_mode`, `sandbox_root`, detected
`cache_roots`, coarse `omitted_cache_tools`, `unconfigured_cache_tools`, and
`restart_required`. Cache access does not install project dependencies or make
an empty virtual environment ready for tests.

Sync results use:

- `ok`: requested state is complete.
- `partial`: no unsafe mutation occurred, but setup, cleanup, or requested state
  is incomplete; read `detail` and the reported changes.
- `blocked`: safety, ownership, drift, configuration, or validation prevented
  the operation; resolve the named blocker before retrying.

Thirteen skills and their internal playbook references install under
`$HOME/.agents/skills/`. Shared helpers install under
`${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/` and, for Codex, also under
`$CODEX_HOME/orchestra/scripts/`. Four Codex agent profiles install under
`$CODEX_HOME/agents/`; the Codex capability matrix installs under
`$CODEX_HOME/orchestra/roles.toml`. The Cursor matrix installs under
`${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/cursor/roles.toml`. The Grok matrix
installs under `${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/grok/roles.toml`. When
`CODEX_HOME` is unset it defaults to `$HOME/.codex`. When `ORCHESTRA_HOME` is
unset it defaults to `$HOME/.orchestra`. The tool owns only destinations
recorded in the install manifest.

Before replacing or removing an existing owned destination, the tool writes one
current deterministic safety backup under `$CODEX_HOME/orchestra/backups/`.
Backups are not restoration history: uninstall removes only content whose digest
still matches the manifest, preserves drifted or unrelated content, and never
restores unrelated user configuration.

## Coordination CLI

Direct sync installs a fail-soft coordination helper at
`${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/coordination.py`. Orchestra uses it to expose
multiple active tasks, material agent activity, and revision-identified
Markdown artifact locators without making telemetry authoritative:

```sh
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/coordination.py" task list
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/coordination.py" task show --task <uuid>
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/coordination.py" artifact list --task <uuid>
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

## Prepared-task Kanban

Direct sync also installs `$orchestra-task` and its local JSON helper. Any
harness can capture or prepare a card without activating Orchestra. New cards
receive immutable IDs such as `A1`; a native Codex, Cursor, or Grok Build chat later adopts
that ID
and starts the normal visible Orchestra flow:

```sh
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/task_control.py" task list
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/task_control.py" task create \
  --title "<title>" --brief "<objective>" --idempotency-key "<stable-key>"
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/task_control.py" task prepare \
  --task A1 --repository "<repo>" \
  --repository-context-file "<context>" \
  --specification-file "<specification>" --confirmed
```

One card is the default: Orchestra keeps sequential complexity in plan phases.
When an explicitly confirmed brief has genuinely independent execution,
acceptance, repository, or delivery boundaries, `task decompose --confirmed`
atomically reuses the source card, creates the minimum additional cards, and
records an immutable initiative DAG. `blocked_by` supports `completed` and
`delivered`; unrelated cards in the same initiative are shown as parallel.
Preparation is allowed while blocked, but adoption waits for the dependency.

`task finish` records the reviewed terminal Git revision. After an authorized
local integration or PR merge returns exact verified evidence, the owning
native chat records it with `task record-delivery`. A `delivered` dependency in
the same Git repository also requires the adopting checkout to contain the
recorded integration revision. The helper never pulls or transports context.

The helper stores private state in `$HOME/.orchestra/control.sqlite3` and
revision-bound documents below `$HOME/.orchestra/tasks/<id>/`. Direct sync also
registers the local stdio `orchestra_tasks` MCP server, exposing capture,
query, notes, preparation, confirmed decomposition, archive, and restore only. It cannot adopt, transfer, reclaim, finish, or record delivery for a task,
start an execution host, create a worktree, or change permissions. From a native
Codex, Cursor, or Grok Build chat,
say `Arranca A1 con Orchestra`; that chat adopts the UUID, activates normal
Orchestra, and Coordinator registers the same UUID after checkout creation.
The store never substitutes for the native conversation, approved `plan.md`,
Git, or user authority.
The Hub remains GET-only. The native menu-bar app reads cards and capabilities
from Task Control and invokes that same local JSON CLI for its bounded card
actions. There is no daemon, remote MCP transport, or mutable web console.

The CLI additionally supports draft editing, recoverable trash, restricted
purge, cooperative safe-stop requests, and reopening cancelled cards. A safe
stop never interrupts active work: the owning root handles it at a stable
handoff, cleans resources, blocks the existing plan, and acknowledges with its
Codex, Cursor, or Grok identity. The same prior owner can resume the preserved
checkout and plan after reopening. Purge requires the exact short ID and is
limited to an evidence-free trashed draft; short IDs are never reused. These
sensitive lifecycle and ownership commands are not exposed through MCP.

The native `hub/menubar` app gets cards and action capabilities from the shared
Task Control runtime, merges only Hub progress by exact UUID, and remains
usable when Hub is down. Its neutral start action copies an instruction for any
supported host. The app installer owns only the app and its RunAtLoad
LaunchAgent; `sync.py` alone owns the shared runtime.

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
