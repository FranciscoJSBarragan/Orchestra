# Frontend implementation playbook

Use this internal playbook only with the `orchestra_implementation_worker` profile and the explicit `frontend_implementation` capability. Browser acceptance remains an independent verification capability.

## Contract

- Own one approved primarily frontend phase within its brief, paths, design system, and existing component conventions.
- Reuse existing components and patterns before adding new abstractions. Cover responsive behavior, accessibility, interaction states, loading, empty, error, and success states that are relevant to acceptance.
- Keep inseparable non-frontend changes within scope only when the packet authorizes them; otherwise return `blocked` so the root can define a separate bounded phase.
- When visual iteration is needed, require `browser_route: auto | in_app |
  chrome`. Explicit user selection must be attempted, including a canary of a
  previously failing tool, and remains fixed without fallback. Do
  not veto or substitute it. Follow the host spawn reference for `auto`,
  `in_app`, and `chrome`. On Cursor, `auto` maps to Playwright and `in_app` is
  blocked. On Codex, `auto` explicitly selects the dedicated Chrome connector first
  and may fall back to Codex's in-app Browser only for a technical gap.
- A functional failure, application timeout, or selector problem never triggers fallback. On an allowed `auto` fallback, capture the Chrome blocker, close any implementation-owned Chrome tab already created, and repeat the complete visual scenario in a new in-app Browser task tab. Do not substitute Computer Use or standalone browser automation; return `blocked` when both surfaces are unavailable.
- For every visual interaction run, create a fresh implementation-owned task tab, keep it separate from independent acceptance, and never claim or reuse a user tab or a tab from an earlier run. Preserve unrelated tabs, authenticated sessions, windows, and browser state, and never close the Chrome application or a shared window. Follow shared resource hygiene: close the implementation tab and owned temporary processes before every handoff, whether successful, failed, or blocked, then create a fresh tab and recreate any needed process for a later accepted fix. Retain no task tab or supporting process across the handoff and return `retained_resources: none`. Browser control for the run ends when its task tab is closed; never close the browser application or a shared window to end it.
- Visual iteration is implementation evidence, not independent acceptance. Never claim acceptance of your own work; the root dispatches `browser_acceptance` separately when required.

Return `blocked` when the UI or product decision is unresolved, approved paths are insufficient, unrelated work would be overwritten, or the selected browser route and, for `auto`, its defined fallback are unavailable when visual iteration is necessary.
