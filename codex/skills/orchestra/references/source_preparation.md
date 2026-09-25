# Prepare a pinned remote source

For cloud or disposable workers, prepare Orchestra before dispatch rather than
asking every role to rediscover installation. The environment owner selects an
approved full commit SHA and one destination per revision. The same SHA must
reach the coordinator, worker and reviewer. This is source mode from
[runtime resources](../runtime.md), not a new host adapter or plugin installation.

The shipped `scripts/prepare_source.py` (source:
`codex/scripts/prepare_source.py`) uses Python 3.11+ and Git to prepare a shallow,
detached checkout or verify an existing clean checkout without fetching again:

```sh
python3 /absolute/path/to/orchestra/scripts/prepare_source.py \
  --revision <approved-full-commit-sha> \
  --destination /absolute/path/to/orchestra-sources/<approved-full-commit-sha>
```

The compact JSON returns `revision`, `source_root`, `skills_root`, `runtime_root`
and `workflow`. In source mode `runtime_root` is `<source>/codex`, while
`workflow` is `<source>/docs/WORKFLOW.md`; pass these exact paths in the assignment.
`--repository` can select an explicit Git mirror or local source instead of the
default Orchestra repository. Branches and tags are not accepted as revisions;
resolve a chosen release label to its full SHA before preparation.

A first installation must provision the helper from an already trusted bundle
or the approved source revision through the environment's existing setup
mechanism. Do not download a moving `main` helper and call that a pinned setup.
A prepared VM image or build can retain the source checkout; verify it at
launch rather than reinstalling on every role. Describe an expected cold start
as preparation, not as a missing-skill failure. Cursor Cloud Build configuration
belongs to the consuming environment and needs a live discovery test there;
this helper does not configure it or prove native plugin loading.

Preparation has one owner per destination and never runs concurrently against
that path. The helper refuses an existing wrong revision, dirty checkout,
non-checkout or symlink instead of resetting, cleaning or replacing it. Failed
fresh fetches and resource checks remove only its temporary staging directory.
Keep prepared sources read-only during tasks, with reports and task data
elsewhere. The environment owner retains revisions needed by active work and
removes obsolete owned directories when no consumer remains. There is no
cache registry, automatic updater or change to global permissions.

An installed plugin can also supply a pinned runtime when its selected content
and host loading are verified. Package archives identify their revision
and checksum; a version label alone does not establish loaded bytes. Do
not switch runtime copies during an active assignment. Plugin availability is
not proof that a host loaded its instructions: runtime resources route the
continuity rules when a skill is selected, while ordinary work without a loaded
skill needs the host's applicable persistent instructions. Plugin installation
does not silently rewrite those global instructions.
