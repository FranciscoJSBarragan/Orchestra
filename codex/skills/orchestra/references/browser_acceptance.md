# Browser acceptance playbook

Use this internal playbook only with the `orchestra_verifier` profile and the explicit `browser_acceptance` capability. Browser acceptance uses the active user-selected tier.

## Contract

- Require `browser_route: auto | in_app | chrome`. An explicit user route,
  relayed by the root or supplied directly in the agent conversation, must be
  attempted even when the scenario is a canary for a previously failing tool,
  and remains fixed without fallback. Do not
  veto or substitute a user-selected route; return its concrete technical
  blocker when it cannot run.
- For `auto`, follow the host spawn reference: on Codex, explicitly select the dedicated Chrome connector first and fall back to Codex's in-app Browser only when Chrome is unavailable or has a technical capability gap that the in-app Browser can satisfy; Cursor maps `auto` to Playwright.
- For `in_app`, use only Codex's in-app Browser; on Cursor return `blocked`. For `chrome`, use only the dedicated Chrome connector. Do not substitute Computer Use or standalone browser automation. Cursor `auto` may use Playwright as the host-mapped surface.
- A functional failure, application timeout, or selector problem never triggers fallback. For an allowed `auto` fallback, capture the Chrome blocker, close any dedicated Chrome tab already created, open a new in-app Browser task tab, and repeat the complete scenario; never combine partial evidence from two browser surfaces into one pass. Return `blocked` when both surfaces are unavailable.
- For every acceptance run, create a fresh task-dedicated tab for the target application. Never claim or reuse a user's existing tab or a tab from an earlier run. Preserve all unrelated tabs, windows, authenticated sessions, and user state, and never close the Chrome application or a shared window. Keep acceptance tabs and evidence separate from frontend implementation.
- Execute only the supplied acceptance scenario through visible interaction. Observe expected behavior, relevant accessibility or responsive states, and failure behavior named in the packet.
- Capture concise visible evidence and exact reproducible steps. Identify the
  environment, exact revision, and test-data provenance, creation or reset
  method, safe identifiers, and cleanup.
- Remain source-read-only and do not implement fixes or accept conclusions supplied by the implementation owner without observing the behavior.
- Follow shared resource hygiene: close the dedicated task tab before every handoff, whether successful, failed, or blocked, and open a fresh one for every rerun. Never retain the task tab or another owned resource across a browser-acceptance handoff; return `retained_resources: none`. A close failure is `cleanup: partial` and does not authorize closing unrelated browser state. Browser control for the run ends when its task tab is closed; never close the browser application or a shared window to end it.

Return `blocked` when the selected route or, for `auto`, its defined fallback is unavailable, a dedicated tab cannot be opened safely, required access or test data is unavailable, or the scenario would disturb unrelated state or cross a destructive, production, payment, security, privacy, or irreversible boundary.
