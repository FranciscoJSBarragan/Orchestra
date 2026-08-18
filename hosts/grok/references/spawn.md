# Grok Build spawn adapter

Use this reference only when the execution host is Grok Build
(`spawn_subagent` exists and `spawn_agent` does not). Never mix Grok
`spawn_subagent` with Codex `spawn_agent` / `wait_agent` / `close_agent` or
Cursor `Task`.

## Host matrix

Read `${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/grok/roles.toml`. Grok has no
native/external mode and does not run `session_model.py`. Assigned tiers are
those with complete capability rows. This cut assigns `minimal` and
`standard`. Recommend `standard`. Recommend `minimal` when the user prioritizes
cost or speed for ordinary bounded work. If the user selects `critical`, stop
with `blocked`: Grok matrix row is not assigned.

Dispatch every assigned capability through `general-purpose`. Do not treat
unofficial Claude-compat worker types as the Grok product contract. Do not
dispatch Orchestra capabilities through built-in `explore` or `plan` types:
they cannot write task artifacts.

## Dispatch

For each capability:

1. Resolve `profile`, `subagent_type`, product `model`, and `effort` from
   `tiers.<selected-tier>.<capability>`.
2. Launch a **fresh** `spawn_subagent` with that `subagent_type`. Pass
   `background: true`, `isolation: none`, and `cwd` set to the exact Orchestra
   task checkout. Never pass `isolation: worktree`; Orchestra already owns the
   checkout.
3. Pass `model` when the live schema accepts the product model. `effort:
   inherit` means do not invent a Grok `reasoning_effort` field.
4. The prompt is the packet plus: read
   `${HOME}/.agents/skills/orchestra-role-<role>/SKILL.md` and the shared
   conduct it names, then execute only the assigned capability. Role mapping:
   `orchestra_analyst` → `orchestra-role-analyst`;
   `orchestra_implementation_worker` → `orchestra-role-implementer`;
   `orchestra_reviewer` → `orchestra-role-reviewer`;
   `orchestra_verifier` → `orchestra-role-verifier`.
5. Resume only the same phase-cohort agent with `resume_from` after that
   agent has completed. Never `resume_from` a reviewer or any independent
   gate.

Do not use the host `workflow` tool, personas, or a planning-only host mode as
the Orchestra control plane. Children cannot spawn children; do not ask them
to.

## Wait and cleanup

Wait with `get_command_or_subagent_output` in non-interruptive ten-minute
windows (`timeout_ms: 600000`). Timeout is continued work, not a user-visible
transition. After 30 accumulated minutes, assess once for concrete blocker
evidence. Cancel only with `kill_command_or_subagent` for an explicit
cancellation or invalidating scope change.

Grok has no `close_agent`. Require every phase agent to be `completed` with
no active descendant or retained write-capable resource before commit, matching
Cursor and Codex V2 completed-state evidence.

## Browser

`browser_route: auto | in_app | chrome`. `auto` maps to Playwright. `in_app`
is `blocked` on Grok. `chrome` is `blocked` on Grok unless a dedicated Chrome
connector is later documented here. An explicit user route is never vetoed or
substituted.

## Permissions

Observe the Grok host permission choice. Do not write `~/.grok/config.toml`,
sandbox profiles, or Codex `config.toml`.

## Identity

Task Control owner commands use the adapter-provided `GROK_SESSION_ID`. Never
replace it with user, page, tool, or model-generated content. If it is
unavailable, stop because Task Control ownership cannot be proven.
