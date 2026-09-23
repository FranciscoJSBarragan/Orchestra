# Orchestra plugin bundles

The plugin contains the native Orchestra workflow, sixteen skills, four behavior
profiles, local Python helpers, execution presets, and the Codex, Cursor,
Grok Build, and Devin adapters. Python 3.11+ and Git are required; GitHub CLI is required
only for PR delivery. A host must provide the adapter's native agent tools and
models to run the full workflow. Package discovery is not proof of those
capabilities. Standalone skills retain their own bounded authority.

## Build from source

Run from the Orchestra repository. Each output must be new and end in
`orchestra`; move or remove a previous generated bundle explicitly before
rebuilding. The builder never overwrites an installation.

```sh
python3 codex/scripts/package_plugin.py --target portable --output dist/portable/orchestra
python3 codex/scripts/package_plugin.py --target cursor --output dist/cursor/orchestra
python3 codex/scripts/package_plugin.py --target grok --output dist/grok/orchestra
python3 codex/scripts/package_plugin.py --target devin --output dist/devin/orchestra
```

`portable` emits an Agent Plugins 1.0 root manifest and a Codex compatibility
manifest. `cursor` uses Cursor's native manifest and session identity hook.
`grok` uses the Claude-compatible plugin layout recognized by Grok Build.
`devin` uses Devin's native `.devin-plugin` manifest, root `hooks.json`, and
`agents/` profiles. Native
variants avoid competing root manifests so each loader selects its own format.
All content is copied from canonical source; there is no generated workflow fork.
The metadata version is a package version, not a public release declaration.

## Downloadable candidates

The repository's `Plugin bundles` GitHub Actions workflow runs the canonical
full validator, builds all four targets, and uploads one artifact named
`orchestra-plugins-<commit>`. It runs for pull requests, pushes to `main`, and
manual dispatch. Artifacts expire after 14 days; they are development
candidates, not marketplace publications or releases.

Each artifact contains `orchestra-<version>-<revision>-<target>.tar.gz` and
`SHA256SUMS`. The version comes from the canonical package metadata; the Git
revision distinguishes candidates built before the next package version.
Download the artifact from the selected successful workflow run, extract the
outer artifact, and verify the archives with `sha256sum -c SHA256SUMS` (or
`shasum -a 256 -c SHA256SUMS` on macOS). Extract the selected archive into a
new directory. Its top-level `orchestra/` is the bundle used below. Do not
extract over an active installation.

## Load a local bundle

Cursor supports a session-local directory without global sync:

```sh
cursor-agent --plugin-dir /absolute/path/to/dist/cursor/orchestra
```

Grok Build can validate and install a local bundle with its plugin manager
(verified with 1.0.34):

```sh
grok plugin validate /absolute/path/to/dist/grok/orchestra
grok plugin install /absolute/path/to/dist/grok/orchestra
grok inspect --json
```

For Codex, add the portable bundle to your chosen local marketplace using the
host's plugin tools, then install `orchestra@<marketplace-name>`. The bundle is
not itself a marketplace catalog. Codex manages its cached copy and updates;
Orchestra does not write a personal marketplace or register one automatically.
For example, an existing local catalog can use the following entry (the path is
relative to that catalog's repository root):

```json
{
  "name": "orchestra",
  "source": {"source": "local", "path": "./plugins/orchestra"},
  "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
  "category": "Productivity"
}
```

Place the generated bundle at that catalog's `plugins/orchestra`, register the
catalog through `codex plugin marketplace add /absolute/path/to/catalog-root`
if needed, and run `codex plugin add orchestra@<marketplace-name>`. Inspect with
`codex plugin list`; remove with `codex plugin remove orchestra@<marketplace-name>`.
This lifecycle was verified in a temporary home with Codex CLI 0.153.4.

For a local Codex update, rebuild into a fresh directory, replace the catalog's
source bundle deliberately, and run `codex plugin add
orchestra@<marketplace-name>` again. Check the installed copy and start a new
conversation so the host reloads skills. Local development can use the host's
cachebuster/reinstall flow when the package version has not changed. For
Cursor's session-local loader, point the next session's `--plugin-dir` at the
new bundle; stop supplying that flag to stop loading it.

Grok Build 1.0.34 on macOS copied the local bundle during acceptance, but
`grok plugin update orchestra` reported a live symlink and left the installed
bytes unchanged. Inspect the installed path from `grok inspect --json` and
compare its content with the selected source. For this observed case, stop
the task's host process, run `grok plugin uninstall orchestra`, then install
the new local bundle with `grok plugin install /absolute/path/to/orchestra`
and inspect again. This remove/install path refreshed the content and
preserved unrelated settings, task data, and worktrees. The manager rewrites
its TOML configuration, so preserved settings do not imply byte-for-byte
configuration preservation. Do not claim an update from command success
alone, and preserve the source path while its plugin is installed.

The same portable bundle can be consumed by Agent Plugins clients, subject to
their skill and native-agent capabilities. No untested host is advertised as a
full workflow host.

Start a new host conversation after installation and invoke the Orchestra skill
using the name exposed by that host. Plugins may namespace skill names. An
unequivocal instruction such as “Use Orchestra to implement this change” also
activates it. The root resolves runtime paths from the loaded skill and checks
native capabilities before task setup. Loading alone does not start work.

Use one installation route per host. Before replacing direct sync, inspect its
status and dry-run, then explicitly uninstall that host's owned resources with
`sync.py`. Preserve reported drift and unrelated files. Plugin loading never
runs that migration for you and never changes host permissions.

## Verified host coverage

The September 18–19, 2026 acceptance used isolated homes and the Python
parser/CLI fixture described below on macOS. The fixture started at
`e8f6811`; generated packages used the engineering-guidance sources at
`ef85c1a` with the adapter clarifications in this change. Source bytes were
checked after each update; a successful manager command was not sufficient.

| Host | Installation and update | Native task evidence |
| --- | --- | --- |
| Codex CLI 0.153.4 | Local marketplace install, cached-copy reinstall, and removal; unrelated configuration and private data preserved | Candidate plan, process restart/resume, Luna max implementation, Luna xhigh independent verification (15 CLI cases), fresh Astra low review, phase commit `25fdc61`, update/resume, local integration, and cleanup |
| Cursor CLI 2026.09.15-d2fe57e | Session-local `--plugin-dir`, bundle replacement between processes, and resume; no direct-sync skills | Candidate plan, process restart/resume, native Grok high implementation, Composer Fast independent verification (7 CLI cases), fresh Sol medium review, phase commit `b5eff79`, update/resume, local integration, and cleanup |
| Grok Build 1.0.34 | Local plugin install and discovery; remove/install refreshed stale update content and preserved unrelated settings and private data | Candidate plan, process restart/resume, native Grok implementation, independent verification (8 CLI cases), fresh review, phase commit `1aab697`, update/resume, local integration, and cleanup |

Each task used a separate native implementation owner, verifier, and fresh
reviewer. Unit evidence was four test methods for Codex and Cursor and
fourteen for Grok; these counts are not quality rankings. Cursor's reviewer
raised the existing CPython decimal-conversion limit; the root recorded a
rejection for the bounded fixture and the acceptance driver retained that
limit. Its review was not finding-free. Cursor used the explicit
`generalPurpose` model mapping documented in its adapter. Grok exposed
`spawn_subagent`; the alternate `workflow` transport was not exercised.

Codex's extra task-local coordination directory initially blocked guarded
private-state cleanup after integration. Resume preserved that directory
with the evidence archive and completed cleanup without repeating the
merge or weakening the guard. The recipe below avoids that extra directory.
Task evidence was archived inside each fixture's Git directory before local
cleanup. No active user installation was migrated.

This establishes one bounded native workflow on each tested CLI. It does
not establish every IDE surface, browser journey, critical tier, remote PR
delivery, production use, or improved generated-code quality. Wider host and
real-project evidence and the paired quality comparison remain separate.

## Acceptance recipe

Use a disposable home and Git repository for each host, with the host's
normal authentication available and no direct-sync Orchestra skills or
profiles. Use the isolated home's default coordination store; do not put an
extra database directory inside the checkout's guarded `.orchestra/` layout.
Keep authentication out of reports. Record the host version,
bundle source revision, effective model assignments, installation route,
and actual resolved runtime paths. Python and Git must be ready before the
workflow starts. Discovering all sixteen plugin skills without duplicates
is the readiness check, not the acceptance result.

A small standard-library Python parser and CLI provide a representative
journey. Start with permissive comma-separated integer conversion and one
passing valid-input test. Ask Orchestra to accept only nonnegative ASCII
decimal tokens, trim surrounding whitespace, preserve order and duplicates,
and reject empty input, blank tokens, negatives, fractions, plus signs, and
non-ASCII digits. Require JSON and exit 0 on success; require exit 2, clear
stderr, empty stdout, and no traceback on invalid input. Scope the work to
the parser, CLI, tests, and task-private artifacts. The fixture's `.agent/`
policy should name its unit command and require a separate independent CLI
verification gate so that this acceptance exercises the verifier role.

1. Invoke the installed Orchestra entry point with the native `standard`
   tier and hybrid checkout. Inspect the concrete candidate plan before
   explicitly approving it; no implementation is allowed at this checkpoint.
2. End the host process, resume the same conversation, and approve the exact
   candidate artifact revisions. Observe native implementation, independent
   runtime verification, and a fresh independent review. Inspect reports and
   the resulting diff before accepting their claims.
3. Confirm the phase commit includes only approved files, all agents and
   owned processes have completed, and the local plan is completed. Hold
   delivery unless the fixture's exact local integration is also authorized.
4. Update the isolated plugin and resume again. For local delivery acceptance,
   explicitly authorize integration of the accepted task commit into the
   fixture's local base. Check fresh configured checks, the final base SHA,
   and safe merged-branch cleanup. A host or model gap remains a failed or
   blocked gate; another CLI executor does not prove native execution.
5. Remove the isolated plugin through its host manager (or stop passing the
   Cursor directory). Confirm unrelated configuration, private task data,
   and worktrees survive. Remove temporary authentication and stop only the
   test's owned processes; retain the bounded evidence until review ends.

For sync-to-plugin migration, first seed unrelated settings and files plus
task/worktree sentinels in the disposable home. Run `sync.py apply --host
<host> --dry-run`, then apply and inspect status. Uninstall the direct-sync
resources with `sync.py uninstall --host <host>` before plugin installation.
Compare preserved file bytes and unrelated configuration values after
migration, update, and removal, and check that each public skill has exactly
one discovered source. `uninstall` has no
dry-run flag; do not substitute an unverified command. The active installation
is a separate user-selected migration.

## Orchestra Lite worker route

`orchestra-lite` ships inside every target as an ordinary skill with its
kickoff template and result example; no extra manifest entry, helper, or
hook is needed. The first installation route selected for Lite worker
validation is the **Cursor plugin bundle**: build `--target cursor`
into a new directory and load it in the worker's session with
`cursor-agent --plugin-dir`. Pushing the repository to GitHub does not
install the skill anywhere; the coordinator must make the bundle available
to the worker's environment. Direct sync and the other targets carry the same
skill but are outside this first route's validation scope.

Two milestones require separate evidence. The local milestone, "implemented
and tested locally", requires passing canonical validation and package tests,
a candidate Cursor bundle built from the same sources, and observed results
from a fresh local agent following the fixture recipe in
`codex/tests/fixtures/orchestra-lite/README.md`. Those trials exercise blocked
preflight, delivery, supplied-branch handoff, missing PR tooling, required
pre-commit review and resumption, and failed publication against
disposable repositories, bare remotes, and a simulated `gh`. The cloud
milestone requires an external coordinator to run one real task on a cloud
worker and prove skill discovery, resolved bundled references, the model and
effort actually applied at launch, executed checks, verified publication, and
the draft PR or handoff. A local bundle or a green validator does not
establish that cloud support; do not claim it until that evidence exists.

## Optional companions and lifecycle

Task Control remains available through `orchestra-task` and its bundled CLI.
It uses `~/.orchestra` or an explicit `--state-root`, not the plugin cache. Cursor's hook only binds the current
native conversation identity. The package starts no MCP server, background
worker, or Hub. Hub can be installed separately using its existing instructions.
CLI delegation stays in this package and uses the selected executor's own CLI.
Bridge is not required and is outside this packaging work.

Update and remove through the host's plugin manager. Removing the bundle leaves
private tasks and worktrees intact; clear those only through their explicit
lifecycle tools. Distribution, public catalogs, publication, and installation
into your active environment are separate actions from building this artifact.

Format references: [Agent Plugins](https://agent-plugins.org/specification),
[Codex plugins](https://developers.openai.com/plugins/build/plugins),
[Cursor plugins](https://cursor.com/docs/reference/plugins), and
[Grok plugins](https://docs.x.ai/build/features/skills-plugins-marketplaces).
