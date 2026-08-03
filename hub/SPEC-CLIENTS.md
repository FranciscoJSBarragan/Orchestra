# Orchestra Hub — Clients v2 Specification (Iteration 1)

Status: frozen. This document records the converged design for the second
client generation of Orchestra Hub. Implementation must not reopen decisions
marked as frozen; deviations require explicit user approval first.

## 1. Purpose and motivation

The MVP validated the Hub server and its read-only contract. Real use produced
two findings, both anticipated by `SPEC.md` §2 entry criteria:

- The primary need is **rich state visibility** (what is being worked on,
  where, and how it is going), not notifications.
- The SwiftBar plugin proved insufficient: third-party container, limited
  personalization. The "native menu bar app" entry criterion is met.

Iteration 1 therefore delivers two first-party read-only clients and retires
SwiftBar:

1. A terminal dashboard (TUI) as the primary state view.
2. A minimal native macOS menu bar app for quick glances.
3. (Optional) cosmetic styling for the existing web panel.

## 2. Frozen product decisions

- The Hub server API, database access, and security model are **unchanged**.
  Both clients consume the existing endpoints only: `GET /v1/summary`,
  `GET /v1/tasks/{id}`, `GET /v1/health`.
- Both clients are strictly read-only observers. No actions, no writes, no
  remote control. Same posture as SPEC.md §1.
- Both clients read the listen port from `<state_root>/hub.toml` (`port`,
  default `7343`) and connect to `http://127.0.0.1:<port>` only. Remote
  viewing remains the job of the web panel over Tailscale.
- Both clients poll with `If-None-Match`/`ETag`; a `304` means "render
  nothing new".
- Hub unreachable or degraded (`503`) → each client shows an explicit
  "Hub unreachable"/"degraded" state. No crash, no fabricated data, no
  retry storm (next poll retries naturally).
- SwiftBar (app and plugin) is uninstalled and `hub/swiftbar/` is deleted
  from the repository **after** the menu bar app passes acceptance.
- Notifications are **out of scope** for this iteration (deferred to the
  menu bar app v2, entry criterion: real use shows glancing is not enough).

### Out of scope (deferred, with entry criteria)

- **Native notifications** — only after the menu bar app proves useful.
- **Remote TUI over Tailscale** — only if laptop terminal use is actually
  wanted; would be a config knob, not a design change.
- **Actions from any client (resume/approve/cancel)** — separate product
  line with explicit authority design; unchanged from SPEC.md.
- **Historic/timeline views** — would require the events ledger; unchanged
  entry criteria from SPEC.md §2.

## 3. Dependency policy (amends the MVP guardrail, server unchanged)

- The Hub **server** remains Python stdlib only (SPEC.md §15 stands).
- The **TUI client** may use exactly one third-party dependency: `textual`
  (pure Python), pinned in `hub/tui/requirements.txt`, installed in a local
  virtual environment that is never imported by the server or its tests.
- The menu bar app uses Swift with Apple system frameworks only (`AppKit`,
  `Foundation`). No Xcode project, no SwiftPM dependencies, no code signing
  or notarization (personal use, local build).

## 4. TUI (`hub/tui/`)

Package `orchestra_hub_tui`, entry `python -m orchestra_hub_tui`.

- Python ≥ 3.11. Dependency: `textual` (pinned range in `requirements.txt`).
- Layout (single screen):
  - **Header:** Hub status (`ok`/`degraded`/`unreachable`), total active
    tasks, blocker count, last successful poll age.
  - **Left panel:** tree of repositories → their tasks. Active tasks
    emphasized; completed tasks collapsed under the repository node.
    Repository rows show `name (active/completed)`.
  - **Main panel:** detail of the selected task — label, tier, stage,
    status, branch, worktree, summary, blocker (highlighted when non-empty),
    next_action, snapshot age, activities table
    (`agent · capability · state · summary · updated_at`), artifacts table
    (`kind · phase · producer · available`).
  - **Footer:** key bindings.
- Keys: arrows/`j`/`k` navigate, `enter`/selection loads detail, `r` forces
  refresh, `q` quits. Nothing else in iteration 1.
- Data flow: poll `/v1/summary` every 5 seconds with ETag; fetch
  `/v1/tasks/{id}` when the selection changes or its fingerprint changed in
  the latest summary. All rendering from allowlisted API fields; the TUI
  never invents states (free-text `stage`/`status` rendered verbatim,
  SPEC.md §8 semantics).
- Attention styling: a task row is highlighted only for the API-reported
  reasons (`blocker` non-empty, `stale == true`).
- Unreachable/degraded: keep the last rendered data dimmed with a visible
  banner "Hub unreachable (retrying)"; never clear the screen to an error.

## 5. Menu bar app (`hub/menubar/`)

Name: **OrchestraHubMenu**. Swift, AppKit, single source file
(`main.swift`, target ≤ ~300 lines), built by `build.sh` with `swiftc` into
a minimal `OrchestraHubMenu.app` bundle (`Info.plist` with
`LSUIElement = true`, no Dock icon, no main window).

- **Status item title** (frozen rule, max 40 characters):
  - No active tasks → `◦` (dimmed glyph only).
  - One repository with active tasks → `<name>:<active_count>`
    (e.g. `Orchestra:2`).
  - Multiple → `<n> repos·<total_active>` (e.g. `2 repos·5`).
  - Hub unreachable/degraded → `⚠ Hub`.
  - A repository is "active" when it has at least one task with
    `status != "completed"`.
- **Menu contents:**
  - One section per active repository (header = repo name), listing its
    active tasks as `label — stage/status`; a task with a non-empty
    `blocker` is marked and shows the blocker text as an indented
    disabled item (truncated to 80 chars).
  - When nothing is active: a single disabled item "No active tasks".
  - When unreachable: a single disabled item "Hub unreachable".
  - Separator, then: "Open panel" (opens `http://127.0.0.1:<port>/` in the
    default browser), "Refresh now", "Quit".
- Poll `/v1/summary` every 30 seconds with `URLSession` and ETag. All menu
  strings come from API fields verbatim (AppKit menu items are plain text;
  no injection surface).
- Autostart: user LaunchAgent `com.orchestra.hub.menubar` (`RunAtLoad`,
  `KeepAlive`), template in `hub/menubar/launchd/`, pointing at the built
  `.app` binary.
- Config: reads `port` from `~/.orchestra/hub.toml` with a tolerant
  line-based parse (`port = N` top-level); malformed or missing → 7343.
  The menu bar app must not gain a TOML library for this.

## 6. Web panel styling (optional task)

- Embedded `<style>` block in `panel.py` only: dark theme, monospace
  numerals, colored badges for stage/status and attention reasons.
- No JavaScript, no external assets, no CDN. Escaping and structure
  unchanged; the existing XSS and panel tests must keep passing with at
  most selector/markup-level assertion updates.

## 7. Testing contract

- **TUI:** `unittest` for the HTTP client (ETag round-trip, 304 handling,
  unreachable → typed result, degraded 503 → typed result) and for the
  pure view-model functions (summary JSON → tree rows / detail rows,
  attention flags passthrough). Textual widget/UI behavior is verified by
  a manual smoke checklist, not automated UI tests, in this iteration.
- **Menu bar app:** manual smoke checklist (build succeeds, status item
  appears with the frozen title rule for 0/1/n active repos, menu contents,
  unreachable state, Open panel, LaunchAgent load/unload). No XCTest
  infrastructure in this iteration.
- **Panel styling:** the entire existing `hub/tests` suite passes.
- The existing Hub server test suite must pass untouched at every commit.

## 8. Acceptance journeys

1. From a terminal, see all repositories and tasks, select a task, and read
   its summary, blocker, activities, and artifacts — updating live.
2. Glance at the menu bar and know which repositories have active work and
   how many tasks, without opening anything.
3. Open the menu and see active tasks per repository with stage/status and
   blockers; jump to the web panel from it.
4. Stop the Hub: TUI shows a banner over dimmed data; menu bar shows
   `⚠ Hub`; both recover alone when the Hub returns.
5. SwiftBar is fully removed; the menu bar app survives logout/login via
   its LaunchAgent.

## 9. Anti-over-engineering guardrails (binding)

- No changes to `hub/orchestra_hub/` beyond the optional `panel.py` style
  block. No new endpoints, fields, or query parameters.
- No shared "client framework" between the TUI and the Swift app; they are
  independent consumers of a stable HTTP contract.
- TUI: one package, ≤ 4 modules (`__main__`, `app`, `client`, `viewmodel`).
  If a module approaches ~250 lines, simplify rather than add structure.
- Swift app: one source file plus build script and plists. No SwiftPM
  package, no asset catalogs, no preferences UI.
- No caching layers, no persistence in either client beyond in-memory
  state (the ETag value included).
