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
(cd "$build" && for entry in .codex-plugin * skills/*; do
  [ "$entry" = skills ] || rm -rf "${drive:?}/$entry"
done) &&
cp -R "$build/." "$drive/"
```

The loop removes the Drive's copy of every top-level entry the bundle ships
except `skills/`, and of every Orchestra skill folder; `cp` then writes the
new bundle in their place, so a file the new bundle no longer ships disappears.
Every other top-level entry of the Drive (`NOTES.md`, `CREW.md`, `AGENTS.md`,
`reports/`, `handoffs/`, `renders/`, `orchestra-home/`) and every other skill
folder stays untouched. It uses only POSIX shell tools, so it behaves the same
on Linux and macOS; it avoids `rsync` because macOS's openrsync keeps stale
files inside any directory a protect filter matches. A top-level file or skill
folder that a later bundle drops stays until you remove it. Keep settings and
flow overrides in that Drive's `orchestra-home/`, which the update never
touches. New threads load the updated skills.
