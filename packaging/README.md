# Orchestra plugin bundles

The plugin contains the native Orchestra workflow, fifteen skills, four behavior
profiles, local Python helpers, execution presets, and the Codex, Cursor, and
Grok Build adapters. Python 3.11+ and Git are required; GitHub CLI is required
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
```

`portable` emits an Agent Plugins 1.0 root manifest and a Codex compatibility
manifest. `cursor` uses Cursor's native manifest and session identity hook.
`grok` uses the Claude-compatible plugin layout recognized by Grok Build. Native
variants avoid competing root manifests so each loader selects its own format.
All content is copied from canonical source; there is no generated workflow fork.
The metadata version is a package version, not a public release declaration.

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
