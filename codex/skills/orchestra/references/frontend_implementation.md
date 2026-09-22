# Frontend implementation playbook

For direct role use, apply WORKFLOW "Standalone tools": keep the engineering
guidance below, but omit phase-only transport, artifact IDs, and formal plan
bundles. Return inline evidence or an explicitly requested output path.

For a delegated capability assignment, use this playbook with the `orchestra_implementation_worker` profile and the explicit `frontend_implementation` capability. Browser acceptance remains an independent verification capability.

Technical techniques may also be consulted in the caller's current workflow
under WORKFLOW "Modular engineering". Assignment-specific role limits, phase
artifacts and independent-gate rules apply when that assignment is selected;
reading this reference does not itself dispatch a role or grant authority.

## Contract

- Own one approved primarily frontend phase within its brief, paths, design system, and existing component conventions.
- When materially shaping visual or interaction design, use `frontentskill`
  when installed. It contains the unified frontend design guidance; preserve
  the repository's existing design system. Ordinary small edits need no
  additional design skill.
- Reuse existing components and patterns before adding new abstractions. Cover responsive behavior, accessibility, interaction states, loading, empty, error, and success states that are relevant to acceptance.
- Keep inseparable non-frontend changes within scope only when the packet authorizes them; otherwise return `blocked` so the root can define a separate bounded phase.
- When visual iteration is needed, require `browser_route: auto | in_app |
  chrome`. Explicit user selection must be attempted, including a canary of a
  previously failing tool, and remains fixed without fallback. Do
  not veto or substitute it. Follow the host spawn reference for `auto`,
  `in_app`, and `chrome`. On Cursor, `auto` and `chrome` map to Browser Use and
  `in_app` is blocked. On Codex, `auto` explicitly selects the dedicated Chrome
  connector first and may fall back to Codex's in-app Browser only for a
  technical gap. On Grok, `auto` maps to Playwright.
- On Cursor, drive Browser Use MCP with `new_tab` then `wait_for_load`. If the
  MCP process client is not registered, authenticate once and retry; if it still
  cannot run, or Chrome remote-debugging Allow is missing, return `blocked`. Do
  not substitute the Cursor IDE browser or the Browser Use CLI.
- A functional failure, application timeout, or selector problem never triggers fallback. On an allowed `auto` fallback, capture the Chrome blocker, close any implementation-owned Chrome tab already created, and repeat the complete visual scenario in a new in-app Browser task tab. Do not substitute Computer Use or standalone browser automation; return `blocked` when both surfaces are unavailable.
- Use an implementation-owned task tab, separate from independent acceptance.
  Preserve user tabs, authenticated sessions, shared windows and applications.
  Follow WORKFLOW `Phase teardown` for cleanup and explicitly authorized
  preview-process retention. Close task tabs at handoff; do not claim that all
  resources were cleaned when a permitted preview process remains active.
- Any phase that changes a user-visible surface requires at least one visual run before handoff whenever a local run recipe exists: render the changed surface in its relevant states, write PNG screenshot files into the exact task-private artifacts directory as `<NN>-implementation-report-shot-<k>.png`, and cite those exact filenames in the `implementation-report`. When no runnable surface exists, record that reason in the report instead of inventing screenshots; the root treats uncited screenshots on a surface-changing phase as missing evidence.
- Visual iteration is implementation evidence, not independent acceptance and not user preview. Never claim acceptance of your own work; the root dispatches `browser_acceptance` separately when required. User preview, when the phase line is `required`, is a root-owned pause after this handoff.

Return `blocked` when the UI or product decision is unresolved, approved paths are insufficient, unrelated work would be overwritten, or the selected browser route and, for `auto`, its defined fallback are unavailable when visual iteration is necessary.
