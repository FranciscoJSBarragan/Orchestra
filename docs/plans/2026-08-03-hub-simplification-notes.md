# Hub simplification notes (deferred analysis)

Status: deferred. The user decided to keep both clients: the menubar app for
quick attention checks and notifications, and the TUI for detailed flow
inspection. They are complementary surfaces over the same read-only hub API.
These notes record the findings for a later pass; none of this blocks or
changes the orchestration workflow.

## Current inventory

| Component | Lines (approx.) | Role |
| --- | --- | --- |
| `hub/orchestra_hub/` (server) | ~766 | Loopback GET-only JSON API + HTML panel over `state.sqlite3` |
| `hub/tui/orchestra_hub_tui/` | ~522 | Textual dashboard, 5s polling with ETag |
| `hub/menubar/` | ~392 | Swift status item, 30s polling, blocker notifications |

All three are correctly non-authoritative and read-only. SwiftBar was retired
cleanly; no dead code remains. Build artifacts and virtualenvs are properly
git-ignored.

## Duplication found (candidates for a shared layer)

1. Config/port reading implemented three times:
   - `hub/orchestra_hub/config.py` (full TOML loader, ~70 lines)
   - `hub/tui/orchestra_hub_tui/client.py` (duplicate port parsing)
   - `hub/menubar/main.swift` (line-based parsing, no TOML library)
2. Attention/blocker detection implemented three times:
   - `hub/orchestra_hub/api.py` `attention_entries()`
   - `hub/tui/orchestra_hub_tui/viewmodel.py` `attention_flags()`
   - `hub/menubar/main.swift` `notifyBlockerChanges()`
3. Timestamp/age formatting implemented four times
   (`api.py`, `panel.py`, `viewmodel.py`, `main.swift`).
4. Repository grouping implemented three times
   (`api.py` `repository_entries()`, `viewmodel.py` `build_tree()`,
   `main.swift` `activeRepos()`).
5. HTTP polling with ETag duplicated between TUI client and menubar.

## Recommended direction (when revisited)

- Move attention detection, age formatting, and repository grouping into the
  server API response so clients render precomputed fields instead of
  re-deriving them. This removes most cross-language duplication without
  merging clients: the server already owns the fingerprint/ETag logic, so it
  is the natural single place for derived presentation state.
- Keep the Swift line-based config parser as-is (no TOML library in Swift is
  an acceptable tradeoff); simplify it to read only the port.
- Share one Python config module between server and TUI.
- Do not add new clients or make any client authoritative (VISION non-goals).

## Explicit non-actions

- Do not retire the TUI or menubar: both have a real user and distinct use
  cases (quick glance + notifications vs. detailed flow view).
- Do not couple hub changes to orchestration workflow changes; the hub only
  consumes coordination snapshots and must keep degrading gracefully when the
  store is absent.
