# Orchestra for T3 Code

This bundle carries the Orchestra workflow, its skills, local Python helpers,
the default flow assignment and the T3 Code host reference. Its full workflow
runs on T3 Code: install a `portable`, `cursor`, `grok` or `claude` bundle
for each provider you use as a task root (Claude Code, Codex, Cursor or Grok),
and T3 carries every role to the provider its flow row names. Python 3.11+ and
Git are required; GitHub CLI is required only for PR delivery. The source
repository's `packaging/README.md` describes building, artifacts and lifecycle.

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

Cursor loads a copied bundle from `~/.cursor/plugins/local/orchestra` after a
reload (it skips symlinks that leave that folder), or one for a session:

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

To update Claude Code, Codex and Cursor with one command, keep the bundles
under one fixed folder so catalogs never change path. Register once: the Claude
Code catalog is `<folder>/current/claude` and the Codex catalog entry's source
is `<folder>/current/portable/orchestra`. Cursor needs no registration. The
first run builds `current` and stops at the reinstall step until those catalogs
are registered; register them and run it again. Then each update is:

```sh
git pull
python3 codex/scripts/update_local.py --root <folder> --claude <marketplace> --codex <marketplace> --cursor
```

Pass only the providers you use. The script runs the full validator, builds into
`<folder>/next` (writing the Claude Code catalog with the given name), moves
`current` to `previous` (dropping the older `previous`) and promotes the new
build to `current`. It then uninstalls and reinstalls through `claude plugin` and
`codex plugin`, replaces Cursor's local copy (Cursor's manager adds only Git
marketplaces) and fails unless every bundle file is byte-identical in each
installed copy; it writes no provider configuration. Managers can report success
and leave stale bytes, as Grok Build 1.0.34 did on `plugin update`. Start a new
T3 thread so the provider reloads skills. To roll back, move `previous` back to
`current`, then uninstall and install through each manager.

Invoke the Orchestra skill in a T3 thread with the name that provider exposes;
plugins may namespace skill names. An unequivocal instruction such as “Use
Orchestra to implement this change” also activates it. The root resolves
runtime paths from the loaded skill and checks the `t3-code` tools before task
setup. Loading alone does not start work and never changes permissions.
