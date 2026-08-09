# Frontend implementation playbook

Use this internal playbook only with the `orchestra_implementation_worker` profile and the explicit `frontend_implementation` capability. Browser acceptance remains an independent verification capability.

## Contract

- Own one approved primarily frontend phase within its brief, paths, design system, and existing component conventions.
- Reuse existing components and patterns before adding new abstractions. Cover responsive behavior, accessibility, interaction states, loading, empty, error, and success states that are relevant to acceptance.
- Keep inseparable non-frontend changes within scope only when the packet authorizes them; otherwise return `blocked` so the root can define a separate bounded phase.
- When visual iteration is needed, require `browser_route: auto | in_app |
  chrome`. Explicit user selection must be attempted, including a canary of a
  previously failing tool, and remains fixed unless fallback is authorized. Do
  not veto or substitute it. `auto` explicitly selects Codex's in-app Browser
  first and may fall back to Computer Use with Chrome only for a technical
  availability or required-capability gap. `in_app` and `chrome` use only their
  selected surface.
- A functional failure, application timeout, or selector problem never triggers fallback. On an allowed technical fallback, close the in-app task tab and repeat the complete visual scenario in a new Chrome task tab. Do not substitute the Chrome browser plugin or standalone automation.
- Open or reuse only the implementation owner's task-dedicated tab, keep it separate from independent acceptance, and preserve unrelated tabs and sessions. Follow shared resource hygiene: close the implementation tab and owned temporary processes before every handoff, then recreate them when a later accepted fix needs them. Retain a tab or process only when the packet explicitly authorizes its category for phase reuse, and report its exact handle.
- Visual iteration is implementation evidence, not independent acceptance. Never claim acceptance of your own work; the root dispatches `browser_acceptance` separately when required.

Return `blocked` when the UI or product decision is unresolved, approved paths are insufficient, unrelated work would be overwritten, or the selected browser route and any authorized fallback are unavailable when visual iteration is necessary.
