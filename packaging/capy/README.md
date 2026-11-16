# Orchestra for Capy

This bundle carries the Orchestra workflow, its skills, local Python helpers,
the default flow assignment and the Capy host reference. Python 3.11+ and Git
are required. The source repository's `packaging/README.md` describes building
and artifacts.

## Install and update

Capy discovers skills at `skills/<name>/SKILL.md` in a Drive, so the `capy`
bundle installs into the root of one Drive location: a Captain's Drive when a
Captain launches task roots, otherwise your own. The same command installs and
updates it. Run it from the Orchestra checkout on a Capy machine where that
Drive is mounted, after `git pull`:

```sh
drive=~/.capy/drive/<location>
build=$(mktemp -d)/orchestra &&
python3 codex/scripts/package_plugin.py --target capy --output "$build" &&
rsync -a --delete --filter='P /*' --filter='P /skills/*' "$build/" "$drive/"
```

`--delete` removes stale files inside the bundle's own top-level entries and
skill folders, so a file the new bundle no longer ships disappears. The two
protect rules keep every other top-level entry of the Drive (`NOTES.md`,
`CREW.md`, `reports/`, `handoffs/`, `orchestra-home/`) and every other
skill folder. A top-level file or skill folder that a later bundle drops stays
until you remove it. Keep settings and flow overrides in that Drive's
`orchestra-home/`, which the update never touches. New threads load the
updated skills.
