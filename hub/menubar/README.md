# OrchestraHubMenu

Native macOS menu bar viewer for the Orchestra Hub (read-only). See
`../SPEC-CLIENTS.md` section 5 for the frozen design.

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

## Autostart (LaunchAgent)

```sh
cp launchd/com.orchestra.hub.menubar.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.orchestra.hub.menubar.plist
```

Unload with `launchctl unload …` before rebuilding.
