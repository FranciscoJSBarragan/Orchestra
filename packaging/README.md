# Orchestra plugin bundles

The plugin contains the Orchestra workflow, reusable skills, local Python
helpers and the default flow assignment. Its full workflow runs inside T3 Code:
install the bundle for each provider you use as a task root (Claude Code,
Codex, Cursor or Grok), and T3 carries every role to the provider its flow row
names. Python 3.11+ and Git are required; GitHub CLI is required only for PR
delivery. Package discovery is not proof that T3 or a provider exposes the
tools the workflow needs. Standalone skills retain their own bounded authority
in any harness.

## Build from source

Run from the Orchestra repository. Each output must be new and end in
`orchestra`; move or remove a previous generated bundle explicitly before
rebuilding. The builder never overwrites an installation.

```sh
python3 codex/scripts/package_plugin.py --target portable --output dist/portable/orchestra
python3 codex/scripts/package_plugin.py --target cursor --output dist/cursor/orchestra
python3 codex/scripts/package_plugin.py --target grok --output dist/grok/orchestra
python3 codex/scripts/package_plugin.py --target claude --output dist/claude/orchestra
```

`portable` emits an Agent Plugins 1.0 root manifest and a Codex compatibility
manifest. `cursor` uses Cursor's native manifest. `grok` uses the
Claude-compatible plugin layout recognized by Grok Build. `claude` uses Claude
Code's `.claude-plugin` manifest and ships one read hook. Native variants avoid
competing root manifests so each loader selects its own format. All content is
copied from canonical source; there is no generated workflow fork. The metadata
version is a package version, not a public release declaration.

## Prepare a pinned remote source

Use the shared recipe at `skills/orchestra/references/source_preparation.md`
(source: `codex/skills/orchestra/references/source_preparation.md`). The same
resource ships in every bundle.

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

## Load a bundle

Claude Code validates a bundle and loads it for one session without
installation:

```sh
claude plugin validate /absolute/path/to/dist/claude/orchestra
claude --plugin-dir /absolute/path/to/dist/claude/orchestra
```

Its `hooks/hooks.json` lets agents read the package's own files without
prompts; it allows only `Read`, `Glob`, and `Grep` inside the bundle.

To install it for every Claude Code session, wrap the bundle in a local
marketplace: copy it to a persistent catalog folder as `orchestra/` and add
`.claude-plugin/marketplace.json` beside it:

```json
{
  "name": "orchestra-local",
  "owner": {"name": "<your name>"},
  "plugins": [{"name": "orchestra", "source": "./orchestra"}]
}
```

Then register the catalog and install from it:

```sh
claude plugin marketplace add /absolute/path/to/catalog
claude plugin install orchestra@orchestra-local
```

The catalog folder must stay in place while the plugin is installed.

Cursor supports a session-local directory:

```sh
cursor-agent --plugin-dir /absolute/path/to/dist/cursor/orchestra
```

Grok Build can validate and install a local bundle with its plugin manager:

```sh
grok plugin validate /absolute/path/to/dist/grok/orchestra
grok plugin install /absolute/path/to/dist/grok/orchestra
grok inspect --json
```

For Codex, add the portable bundle to your chosen local marketplace using the
provider's plugin tools, then install `orchestra@<marketplace-name>`. The bundle
is not itself a marketplace catalog. Codex manages its cached copy and updates;
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

To update, rebuild into a fresh directory, replace the installed source
deliberately, and check the installed copy before trusting a manager's success
message: Grok Build 1.0.34 once reported a live symlink on `plugin update` and
left the installed bytes unchanged, while uninstall and install refreshed them.
Start a new T3 thread so the provider reloads skills.

Invoke the Orchestra skill in a T3 thread with the name that provider exposes;
plugins may namespace skill names. An unequivocal instruction such as “Use
Orchestra to implement this change” also activates it. The root resolves
runtime paths from the loaded skill and checks the `t3-code` tools before task
setup. Loading alone does not start work and never changes permissions.

## Acceptance

The September 2026 acceptance of separate Codex, Cursor and Grok Build hosts
is recorded at the `multi-host-final` tag. Acceptance of the T3 Code route,
from a request to a delivered PR in one pass, is pending in
[the roadmap](../docs/ROADMAP.md).

## Lifecycle

Update and remove through each provider's plugin manager. Removing the bundle
leaves private tasks and worktrees intact; clear those only through their
explicit lifecycle tools. Distribution, public catalogs, publication, and
installation into your active environment are separate actions from building
this artifact.

Format references: [Agent Plugins](https://agent-plugins.org/specification),
[Codex plugins](https://developers.openai.com/plugins/build/plugins),
[Cursor plugins](https://cursor.com/docs/reference/plugins),
[Claude Code plugins](https://code.claude.com/docs/en/plugins-reference), and
[Grok plugins](https://docs.x.ai/build/features/skills-plugins-marketplaces).

## Modular entries

All targets include `orchestra-engineering`, `orchestra-project-verification`,
`orchestrator` and `orchestra-repo-readiness` from canonical sources.
References relocate with the bundle. Engineering and verification entries
allow provider discovery; the initiative coordinator and repository readiness
require an explicit request. Distribution makes resources available, not
guaranteed selection. See
[modular acceptance](../docs/evaluation/MODULAR_ACCEPTANCE.md) for source tests,
local integration canaries and the separate live evaluation boundary.
