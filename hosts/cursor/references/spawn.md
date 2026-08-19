# Cursor spawn adapter

Use this reference only when the execution host is Cursor (`Task` exists).
Never mix Cursor Task with Codex `spawn_agent` / `wait_agent` / `close_agent`
or Grok `spawn_subagent`.

## Host matrix

Read `${ORCHESTRA_HOME:-$HOME/.orchestra}/hosts/cursor/roles.toml`. Cursor has
no native/external mode and does not run `session_model.py`. Assigned tiers
are those with complete capability rows. This cut assigns `minimal` and
`standard`. Recommend `standard`. Recommend `minimal` when the user prioritizes
cost or speed for ordinary bounded work. If the user selects `critical`, stop
with `blocked`: Cursor matrix row is not assigned.

## Dispatch

Cursor `Task.subagent_type` is a closed enum. Do not dispatch through custom
`~/.cursor/agents` files. For each capability:

1. Resolve `profile`, `subagent_type`, product `model`, and `effort` from
   `tiers.<selected-tier>.<capability>`.
2. Launch a **fresh** Task with that `subagent_type` (isolated context is the
   independence guarantee). Pass `run_in_background`
   when the owner must remain available. Do not busy-poll.
3. The Task prompt is the packet plus: read
   `${HOME}/.agents/skills/orchestra-role-<role>/SKILL.md` and the shared
   conduct it names, then execute only the assigned capability. Role mapping:
   `orchestra_analyst` → `orchestra-role-analyst`;
   `orchestra_implementation_worker` → `orchestra-role-implementer`;
   `orchestra_reviewer` → `orchestra-role-reviewer`;
   `orchestra_verifier` → `orchestra-role-verifier`.
4. Resume only the same phase-cohort agent id (`resume`). Never `resume: self`
   for a reviewer or any independent gate.

Apply the phase verification contract before launching a Task. When the
`Independent verification gate` is `none`, do not create a verifier Task;
matrix entries describe available capabilities, not mandatory agents. Create a
verifier only for a named browser, service/process, mutable-data, credential,
network/external, repository-policy, or critical-tier gate. Cursor currently
blocks the critical tier, but this rule remains the host contract when that tier
is assigned later.

## Product contract vs live Task slugs

`roles.cursor.toml` records Luna high and Grok 4.6 medium/high/xhigh as the
product contract. Pass those names in the packet. The live Task schema may only
expose nearby workers. Use the closest worker without rewriting the product
contract or inventing a Codex `reasoning_effort` field:

| Product model | Product effort | Task worker actually passed |
| --- | --- | --- |
| `gpt-5.6-luna` | `high` | `luna-worker` (`model` inherit unless a Luna-high slug exists) |
| `cursor-grok-4.6` | `medium` | `grok-worker` (`model` inherit unless a Grok-4.6-medium slug exists) |
| `cursor-grok-4.6` | `high` | `grok-worker` (`model` inherit; the live worker is high-effort) |
| `cursor-grok-4.6` | `xhigh` | `grok-worker` with `model` `cursor-grok-4.6-xhigh` |

If a later Task schema exposes exact slugs, prefer them and document the change
here. Do not silently substitute Sol or Terra.

## Wait and cleanup

Wait with the host wait contract: a background Task plus completion
notification, in non-interruptive ten-minute windows. Timeout is continued
work, not a user-visible transition. After 30 accumulated minutes, assess once
for concrete blocker evidence.

Cursor has no `close_agent`. Require every phase agent to be `completed` with
no active descendant or retained write-capable resource before commit, matching
Codex V2 completed-state evidence.

## Browser

`browser_route: auto | in_app | chrome`. `auto` maps to Playwright. `in_app` is
`blocked` on Cursor. `chrome` remains the dedicated Chrome connector when
available. An explicit user route is never vetoed or substituted.

## Permissions

Observe the Cursor host permission choice. Do not write `settings.json` or
Codex `config.toml`.
