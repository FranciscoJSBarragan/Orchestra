# Orchestra Tasks for macOS

Native local task manager for Orchestra. One app provides a compact menu-bar
view and a full SwiftUI workspace. It obtains cards and action capabilities
from Task Control, then merges only observational progress from the Hub's
GET-only API by exact task UUID.

## Features

- Active, drafts, ready, cancelled, completed, archived, and trash sections.
- Search, detail, literal progress summaries, blockers, and next actions.
- Create/edit drafts, add notes, archive/restore, recoverable trash, restricted
  permanent deletion, request/withdraw safe stops, and reopen cancelled tasks.
- Clearing the repository field while editing a draft explicitly removes its
  repository association; leaving the preloaded value unchanged preserves it.
- `Copy start instruction` puts `Start <ID> with Orchestra` on the clipboard
  for use in Codex, Cursor, Grok, or Devin; it never launches a host or starts work.
- System light/dark appearance and English/Spanish localization.

The app prefers `${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/task_control.py`
and falls back to the bundled helper. Python 3.11 or newer is required.
Permanent deletion is allowed only when Task Control reports that the trashed
draft has no preparation, ownership, notes, dependencies, initiative, run,
completion, or delivery evidence. Trash and archive never touch Git resources.

## Build

```sh
./test.sh
./build.sh          # produces build/Orchestra Tasks.app
./install.sh
```

Requires the Xcode Command Line Tools (`swiftc`) and Python 3.11+. The build is
ad-hoc signed and has no third-party dependencies. The installer manages only
the app and `com.orchestra.tasks` LaunchAgent; runtime sync remains owned by
`codex/scripts/sync.py`.

## Run manually

```sh
open "build/Orchestra Tasks.app"
```

The app remains usable for card management when the Hub is unavailable; only
live progress is absent. Notifications are limited to new blockers and pending
safe-stop requests.

## Autostart (LaunchAgent)

```sh
./install.sh
```

Installation uses `RunAtLoad` without `KeepAlive`, replaces the app and plist
atomically, and restores the previous pair when launchd cannot start the new
version. `./uninstall.sh` preserves Task Control data, runtime files, Hub, Git,
worktrees, commits, and chats.
