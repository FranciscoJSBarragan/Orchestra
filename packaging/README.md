# Orchestra plugin bundles

The plugin contains the Orchestra workflow, reusable skills, local Python
helpers, the default flow assignment and the reference and guide of one host.
Its full workflow runs on T3 Code or Capy, and each host's guide says how to
load it. Each bundle ships only its own host's reference and guide, so neither
host loads the other's instructions; both rebuild from the same canonical
source. Package discovery is not proof that the host or a provider exposes the
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
python3 codex/scripts/package_plugin.py --target capy --output dist/capy/orchestra
```

`portable` emits an Agent Plugins 1.0 root manifest and a Codex compatibility
manifest; `capy` emits the same two manifests with Capy's host reference
and guide. `cursor` uses Cursor's native manifest. `grok` uses the
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
full validator, builds every target, and uploads one artifact named
`orchestra-plugins-<commit>`. It runs for pull requests, pushes to `main`, and
manual dispatch. Artifacts expire after 14 days; they are development
candidates, not marketplace publications or releases.

Each artifact contains `orchestra-<version>-<revision>-<target>.tar.gz` and
`SHA256SUMS`. The version comes from the canonical package metadata; the Git
revision distinguishes candidates built before the next package version.
Download the artifact from the selected successful workflow run, extract the
outer artifact, and verify the archives with `sha256sum -c SHA256SUMS` (or
`shasum -a 256 -c SHA256SUMS` on macOS). Extract the selected archive into a
new directory; its top-level `orchestra/` is the bundle its host guide loads.
Do not extract over an active installation.

## Load or install

Each bundle ships its host's guide as `README.md`: the
[T3 Code guide](t3/README.md) for `portable`, `cursor`, `grok` and `claude`,
and the [Capy guide](capy/README.md) for `capy`.

## Acceptance

The September 2026 acceptance of separate Codex, Cursor and Grok Build hosts
is recorded at the `multi-host-final` tag. The T3 Code route delivered a PR
from a request in one pass on 2026-10-28; [the roadmap](../docs/ROADMAP.md)
records that evidence and what remains.

## Lifecycle

Update and remove a bundle as its host's guide describes. Removing the bundle
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
