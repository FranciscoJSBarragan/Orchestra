# OrchestraHubMenu

Native macOS menu bar viewer for the Orchestra Hub and local task inbox. Hub
data remains read-only; local inbox actions invoke the installed JSON helper.

## Build

```sh
./build.sh          # produces build/OrchestraHubMenu.app
```

Requires the Xcode Command Line Tools (`swiftc`). No Xcode project, no
signing, no third-party dependencies.

## Run manually

```sh
open build/OrchestraHubMenu.app
```

Status item title: `◦` (idle) · `Repo:N` (one active repo) ·
`N repos·M` (several) · `⚠ Hub` (unreachable). The menu lists active
tasks per repository; blockers are marked with their text below.

The Local inbox section lists open, cancelled, and archived tasks. It can
cancel (after confirmation), reopen, archive, and restore them. The helper path
resolves from `ORCHESTRA_TASK_CONTROL`, then `CODEX_HOME`, then
`~/.codex/orchestra/scripts/task_control.py`. Actions run asynchronously and
never mutate Hub HTTP state.

## Autostart (LaunchAgent)

```sh
cp launchd/com.orchestra.hub.menubar.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.orchestra.hub.menubar.plist
```

Unload with `launchctl unload …` before rebuilding.
