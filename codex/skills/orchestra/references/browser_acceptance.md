# Browser acceptance playbook

Use this internal playbook only with the `orchestra_verifier` profile and the explicit `browser_acceptance` capability. Browser acceptance uses the active user-selected tier.

## Contract

- Require `browser_route: auto | in_app | chrome`. An explicit user route,
  relayed by the root or supplied directly in the agent conversation, must be
  attempted even when the scenario is a canary for a previously failing tool,
  and remains fixed unless that instruction also authorizes fallback. Do not
  veto or substitute a user-selected route; return its concrete technical
  blocker when it cannot run.
- For `auto`, explicitly select Codex's in-app Browser first. After its supported connection recovery, fall back to Computer Use with Chrome only when the in-app Browser is unavailable or lacks authentication, extension, native-dialog, browser-specific, or system-integration behavior required by the scenario.
- For `in_app`, use only Codex's in-app Browser. For `chrome`, use only Computer Use with Chrome. Do not substitute the Chrome browser plugin or standalone browser automation.
- A functional failure, application timeout, or selector problem never triggers fallback. For an allowed technical fallback, capture the blocker, close the dedicated in-app tab, open a new Chrome task tab, and repeat the complete scenario; never combine partial evidence from two browser surfaces into one pass.
- Open a task-dedicated tab for the target application and preserve all unrelated tabs, windows, authenticated sessions, and user state. Keep acceptance tabs and evidence separate from frontend implementation.
- Execute only the supplied acceptance scenario through visible interaction. Observe expected behavior, relevant accessibility or responsive states, and failure behavior named in the packet.
- Capture concise visible evidence and exact reproducible steps. Identify the
  environment, exact revision, and test-data provenance, creation or reset
  method, safe identifiers, and cleanup.
- Remain source-read-only and do not implement fixes or accept conclusions supplied by the implementation owner without observing the behavior.
- Follow shared resource hygiene: close the dedicated task tab before every handoff and open a new dedicated tab when a later rerun needs one. Retain it only when the packet explicitly authorizes browser-tab reuse for the phase, and report its exact handle.

Return `blocked` when the selected route or its authorized fallback is unavailable, a dedicated tab cannot be opened safely, required access or test data is unavailable, or the scenario would disturb unrelated state or cross a destructive, production, payment, security, privacy, or irreversible boundary.
