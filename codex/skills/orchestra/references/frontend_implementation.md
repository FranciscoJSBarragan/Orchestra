# Frontend implementation playbook

Use this internal playbook only with the `implementation_worker` profile and the explicit `frontend_implementation` capability. Named browser acceptance makes a task at least standard; a frontend change may be light only when every light condition holds, including one direct targeted verification.

## Contract

- Own one approved primarily frontend phase within its brief, paths, design system, and existing component conventions.
- Reuse existing components and patterns before adding new abstractions. Cover responsive behavior, accessibility, interaction states, loading, empty, error, and success states that are relevant to acceptance.
- Keep inseparable non-frontend changes within scope only when the packet authorizes them; otherwise return `blocked` so the root can define a separate bounded phase.
- When visual iteration is needed, use Computer Use with Chrome only. Open or reuse only the task's dedicated tab, preserve unrelated tabs and sessions, and never invoke, probe, or fall back to Codex's in-app Browser.
- Visual iteration is implementation evidence, not independent acceptance. Never claim acceptance of your own work; the root dispatches `browser_acceptance` separately when required.

Return `blocked` when the UI or product decision is unresolved, approved paths are insufficient, unrelated work would be overwritten, or Computer Use or Chrome is unavailable when visual iteration is necessary.
