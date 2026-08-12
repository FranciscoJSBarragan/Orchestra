# OrchestraHubMenu

Native macOS menu bar viewer for the Orchestra Hub. It is strictly read-only;
prepared and active tasks both arrive through the Hub GET API.

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

The status item uses an icon alone when idle, `<repo> <count>` for one active
repository, `<n> repos · <tasks>` for several, and `!` when unreachable. The
menu lists prepared and active tasks per repository, prefixes known tasks with
their human ID, and marks blockers with their text below. It exposes only
`Open panel`, `Refresh now`, and `Quit`; task mutation happens from an
authorized chat or local CLI, never from the menu bar.

## Autostart (LaunchAgent)

```sh
cp launchd/com.orchestra.hub.menubar.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.orchestra.hub.menubar.plist
```

Unload with `launchctl unload …` before rebuilding.
