# Orchestra Hub — MVP Specification

Status: frozen. This document records the converged design. Implementation must
not reopen decisions marked as frozen; deviations require explicit user
approval first.

## 1. Purpose

Orchestra Hub is a **read-only observational viewer** for the Orchestra
coordination snapshot (`~/.orchestra/state.sqlite3`). It gives one person
visibility over multi-task orchestration from the main machine, a laptop over
Tailscale, and Hermes (a JSON-consuming agent). It observes; it never governs.

## 2. Frozen product decisions

- Single Python process: JSON API plus a minimal HTML panel.
- Lives in this repository under `hub/`. Optional component.
- Reads the coordination SQLite database directly, strictly read-only.
- Zero changes to `coordination.py`, its schema, or anything under `codex/`.
- Remote access exclusively through Tailscale (Hub listens on loopback only).
- Availability guarantee: available while the user session is logged in
  (LaunchAgent). Recovery after reboot = log in. LaunchDaemon out of scope.
- Clients: web panel, SwiftBar plugin, Hermes via plain JSON.

### Out of scope for the MVP (deferred, with entry criteria)

- **Event table / ledger** — only if snapshot polling demonstrably misses
  needed transitions in real use.
- **Schema migrations or new columns/tables** — never for the Hub; the Hub is
  a pure consumer.
- **Controlled `status`/`stage` vocabulary** — only after real use shows the
  conservative attention feed is insufficient; it would be a workflow-docs
  contract, not SQL.
- **Native menu bar app** — only if the SwiftBar plugin proves insufficient.
- **MCP adapter** — only if Hermes JSON consumption proves insufficient.
- **Remote actions (resume/approve/cancel)** — separate design with explicit
  authority controls; not part of this product line yet.
- **Central consumer cursors** — clients keep their own baselines.
- **Auth tokens / rate limiting** — tailnet isolation plus read-only routes is
  the MVP security model.

## 3. Architecture and boundary invariants

```
coordination.py ──local writes──▶ state.sqlite3 ◀──read-only── orchestra-hub
                                                                    │
panel (HTML) / SwiftBar / Hermes / laptop ──GET over loopback or Tailscale──┘
```

- **The Orchestra runtime does not depend on and does not know the Hub.**
  Nothing in runtime code paths under `codex/` references the Hub.
  Tests and monorepo configuration MAY reference both sides; the schema
  cross-check test requires it.
- Operational dependency direction: `Hub → coordination contract`,
  `Orchestra ↛ Hub`.
- If the Hub is down, broken, or incompatible, Orchestra is unaffected.

## 4. Schema compatibility contract

- The Hub declares its own compatibility set in `hub/orchestra_hub/db.py`:

  ```python
  SUPPORTED_SCHEMA_VERSIONS = frozenset({1})
  ```

- At runtime the Hub compares `PRAGMA user_version` against that set. It must
  NOT import `coordination.SCHEMA_VERSION` to decide runtime compatibility
  (that would auto-match on version bumps without review).
- A monorepo test deliberately imports both and asserts
  `coordination.SCHEMA_VERSION in SUPPORTED_SCHEMA_VERSIONS`, so a coordinator
  schema bump breaks the test until someone reviews Hub compatibility.
- Unsupported version → degraded responses (section 8), never a crash, never
  a partial read of misunderstood data.

## 5. Database access invariants

Every request that reads the database follows this exact sequence:

1. Open with URI `file:<path>?mode=ro` (`uri=True`).
2. `PRAGMA query_only = ON`.
3. `PRAGMA busy_timeout = 2000`.
4. `BEGIN DEFERRED`.
5. Immediately perform the first read (`PRAGMA user_version`), which
   materializes the read snapshot and doubles as the schema check.
6. Run all queries for the request inside that transaction.
7. `ROLLBACK` (equivalent to commit for reads) in a `finally` block.
8. Close the connection. No transaction is ever held between requests.

Guarantees (worded precisely):

- The Hub does not block normal `coordination.py` writes under WAL.
- A response reflects one consistent snapshot: either fully before or fully
  after a concurrent write, never a mix.
- A temporary `busy`/locked condition degrades cleanly (section 8) and the
  next poll retries; no absolute promise is made for damaged databases or
  exceptional locks.
- Read transactions are short-lived (per request) so WAL checkpointing is not
  delayed.

Database location: `<state_root>/state.sqlite3`, `state_root` defaulting to
`~/.orchestra` (configurable for tests, see section 10).

## 6. Material fingerprint contract

- Computed **only by the Hub**. Clients store and compare opaque strings.
- `material_fingerprint_version` is `1` and is returned alongside every
  payload containing fingerprints. If the field set or canonicalization ever
  changes, the version bumps and clients re-baseline silently instead of
  emitting a false "everything changed" storm.
- Input: canonical JSON (sorted keys, `,`/`:` separators, UTF-8, non-ASCII
  preserved) of exactly these nine task fields, all as stored strings:

  ```
  blocker, head_revision, id, label, next_action, stage, status, summary, tier
  ```

- `updated_at`, `created_at`, `base_revision`, `repository`, `worktree`, and
  `branch` are deliberately excluded (timestamps drive no notifications;
  the rest are immutable per task).
- Output format: `sha256:<64 lowercase hex>`.

## 7. HTTP API contract

All endpoints are GET. The server physically implements no mutating routes;
`POST`, `PUT`, `PATCH`, and `DELETE` return `405` with an `Allow: GET` header.
All JSON bodies are built exclusively from the allowlisted fields below —
never from `SELECT *` passthrough.

### Allowlists

- Task: `id, label, repository, worktree, branch, base_revision,
  head_revision, tier, stage, status, summary, blocker, next_action,
  created_at, updated_at` plus computed `material_fingerprint` and `stale`.
- Activity: `agent_id, capability, state, summary, updated_at`.
- Artifact: `id, kind, phase, revision, producer, created_at` plus computed
  `available`. The artifact filesystem `path` is **never** serialized.

Local repository/worktree paths are exposed deliberately: they are part of
the product. Artifact content, prompts, diffs, and environment variables are
never exposed.

### `GET /v1/health` — always `200`

```json
{"status": "ok", "database": "available", "schema_version": 1,
 "generated_at": "2026-08-02T18:00:00Z"}
```

Degraded variant (still `200`; health reports, it does not fail):

```json
{"status": "degraded", "database": "missing", "detail": "…",
 "generated_at": "2026-08-02T18:00:00Z"}
```

`database` is one of `available | missing | busy | unsupported-schema | error`.

### `GET /v1/summary`

```json
{
  "status": "ok",
  "material_fingerprint_version": 1,
  "repositories": [
    {"path": "/abs/path", "name": "Repo", "pinned": false, "observed": true,
     "active_tasks": 2, "completed_tasks": 5}
  ],
  "tasks": [ TaskSummary, … ],
  "attention": [
    {"task_id": "…", "label": "…", "repository": "…",
     "reasons": ["blocker"], "blocker": "…", "next_action": "…",
     "updated_at": "…"}
  ]
}
```

- `tasks`: all tasks, ordered `updated_at DESC, id` (same ordering as
  `coordination.py task list`).
- `repositories`: union of observed (derived from `tasks.repository`) and
  pinned (TOML) repositories. `name` = pinned name, else path basename.
  Sorted by `name`, then `path`.
- No `generated_at` in this body: the body must be byte-stable when nothing
  changed so the `ETag` works. Clients use the HTTP `Date` header if needed.

`TaskSummary` is the task allowlist verbatim, e.g.:

```json
{"id": "…", "label": "…", "repository": "/abs", "worktree": "/abs",
 "branch": "orchestra/x", "base_revision": "<hex>", "head_revision": "<hex>",
 "tier": "standard", "stage": "implementation", "status": "active",
 "summary": "…", "blocker": "", "next_action": "…",
 "created_at": "…Z", "updated_at": "…Z",
 "material_fingerprint": "sha256:…", "stale": false}
```

### `GET /v1/tasks[?status=<exact>]`

```json
{"status": "ok", "material_fingerprint_version": 1, "tasks": [TaskSummary, …]}
```

Optional exact-match `status` filter, mirroring `coordination.py task list`.

### `GET /v1/tasks/{id}`

```json
{"status": "ok", "material_fingerprint_version": 1,
 "task": TaskSummary,
 "activities": [{"agent_id": "…", "capability": "…", "state": "…",
                 "summary": "…", "updated_at": "…"}],
 "artifacts": [{"id": "…", "kind": "…", "phase": 1, "revision": "<hex>",
                "producer": "…", "created_at": "…", "available": true}]}
```

Unknown id → `404` `{"status": "invalid", "reason": "unknown task"}`.

### Errors and caching

- Unknown path → `404` `{"status": "invalid", "reason": "not found"}`.
- Database unavailable on data endpoints → `503`
  `{"status": "degraded", "database": "<condition>", "detail": "…"}`.
- `/v1/summary`, `/v1/tasks`, `/v1/tasks/{id}`: strong `ETag` (sha256 of the
  response body); `If-None-Match` hit → `304` with empty body.

## 8. Attention rules (MVP — unambiguous evidence only)

`stage`, `status`, and activity states are free-text labels. The MVP therefore
classifies only:

- **`blocker`**: task `status != "completed"` and `blocker` is non-empty.
- **`stale`**: task `status != "completed"` and `updated_at` older than
  `stale_after_minutes` (default 60, configurable).

Everything else is displayed as reported text. The panel labels the section
"Possible attention". No semantic interpretation of free text, no liveness
inference: silence is shown as "last snapshot X min ago", never as a
fabricated blocked state. Material change detection is client-side via
fingerprint comparison.

## 9. Panel (`GET /`)

- Server-rendered HTML, no JS framework; auto-refresh via
  `<meta http-equiv="refresh" content="30">`.
- Sections: Possible attention, Repositories, Tasks (all, with status/stage
  columns and "last snapshot X min ago").
- **Every dynamic value passes through `html.escape`.** Task `label`,
  `summary`, `blocker`, `next_action`, and activity/artifact text are
  untrusted input; an XSS test with hostile payloads is an acceptance
  criterion.

## 10. Configuration

Optional TOML file at `<state_root>/hub.toml` (default `~/.orchestra/hub.toml`).
Missing file → all defaults. Unknown keys are ignored.

```toml
port = 7343                 # loopback listen port (host is NOT configurable)
stale_after_minutes = 60
state_root = "/Users/me/.orchestra"   # test/dev override only

[[repositories]]            # pinned repositories (may have no tasks yet)
path = "/Users/me/Code/NeniTPV"
name = "NeniTPV"
```

The bind host is hard-coded to `127.0.0.1` as a security invariant.

## 11. Security invariants

- Listens exclusively on loopback. Tailscale Serve is the only remote proxy.
- No mutating endpoints exist; non-GET methods return `405`.
- No endpoint reads filesystem paths supplied by request parameters.
- No artifact content, prompts, diffs, code, or environment variables in any
  response.
- Field-allowlist serialization everywhere; HTML escaping everywhere.
- Network acceptance (Phase 2, on the real machine): canary from the
  authorized laptop over Tailscale succeeds; the same request against the
  Mac's LAN IP fails; mutating methods return `405` through the proxy too.

## 12. Availability

- Runs as a user LaunchAgent (`com.orchestra.hub`), `RunAtLoad` + `KeepAlive`.
- The MVP deliberately adopts a user service and does not promise
  availability before login. The exact Tailscale variant/behavior on this
  machine is verified during Phase 2, not assumed.
- Requires Python ≥ 3.11 (`tomllib`); the LaunchAgent must point to a
  verified 3.11+ interpreter.

## 13. Client baseline contract (SwiftBar; Hermes follows the same rules)

- Clients persist `{material_fingerprint_version, {task_id: fingerprint}}`
  locally (SwiftBar: `~/.orchestra/hub-monitor.json`).
- First sync (or lost/mismatched-version state file): establish baseline; emit
  at most **one aggregated notification** if blockers currently exist; never
  one notification per task.
- Subsequent polls notify only when a fingerprint appears, changes, or a
  blocker reason appears/disappears.
- Hub unreachable → show "Hub unreachable" state; do not notify repeatedly.

## 14. Acceptance journeys

1. From the main machine, view tasks grouped by repository.
2. Same summary from the laptop via Tailscale.
3. A single notification when a blocker appears, and when it disappears.
4. Clear degradation — without affecting Orchestra — for a missing, busy, or
   schema-incompatible database.
5. Stale snapshots and unavailable artifacts are shown as such, with no
   inference of live agents or fabricated states.
6. A pinned repository with zero tasks appears in the catalog.
7. Negative network verification: loopback-only listener, LAN IP unreachable,
   Tailscale canary works, mutating methods return `405`, no remote write
   endpoint exists.

## 15. Anti-over-engineering guardrails (binding for implementation)

- Python stdlib only. No third-party dependencies, no framework, no ORM, no
  async runtime. `http.server.ThreadingHTTPServer` is sufficient.
- No new tables, columns, views, triggers, or migrations anywhere.
- No abstraction layers for hypothetical future backends; SQLite is the only
  data source.
- No auth/token system, no rate limiting, no user management.
- No WebSockets/SSE; polling with ETag is the mechanism.
- Keep modules focused; if any module approaches ~250 lines, stop and
  simplify rather than adding structure.
- Do not modify anything outside `hub/` (the schema cross-check test imports
  `codex/scripts/coordination.py` read-only).
