# Browser acceptance playbook

Use this internal playbook only with the `verifier` profile and the explicit `browser_acceptance` capability. Browser acceptance is at least standard tier.

## Contract

- Use Computer Use with Chrome as the exclusive browser-control path. Never invoke, probe, or fall back to Codex's in-app Browser.
- Open a new Chrome tab for the target application and preserve all unrelated tabs, windows, authenticated sessions, and user state.
- Execute only the supplied acceptance scenario through visible interaction. Observe expected behavior, relevant accessibility or responsive states, and failure behavior named in the packet.
- Capture concise visible evidence and exact reproducible steps. Identify the environment, test data, and exact revision under test.
- Remain source-read-only and do not implement fixes or accept conclusions supplied by the implementation owner without observing the behavior.

Return `blocked` when Computer Use or Chrome is unavailable, a new isolated tab cannot be opened safely, required access or test data is unavailable, or the scenario would disturb unrelated state or cross a destructive, production, payment, security, privacy, or irreversible boundary. Unavailability must never trigger an in-app Browser fallback.
