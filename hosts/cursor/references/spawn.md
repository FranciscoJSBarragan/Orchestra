# Cursor spawn adapter

When an execution preset is explicitly selected, use `orchestra-delegate` and
WORKFLOW "Delegated execution presets" to resolve each assignment first. CLI
results use that helper, root results stay in the owning conversation, and
native results use this adapter with their exact resolved model and effort.
A `host` result uses the native matrix below. Do not apply native fallback or
closest-model substitutions to preset CLI assignments.

Use this reference only when the execution host is Cursor (`Task` exists).
Never mix Cursor Task with Codex `spawn_agent` / `wait_agent` / `close_agent`
or Grok `spawn_subagent`.

## Host matrix

Resolve the selected matrix through `orchestra/runtime.md`: installed layouts
use `<runtime>/hosts/cursor/roles.toml`; prepared source uses
`<source>/hosts/cursor/config/roles.cursor.toml`, outside `<source>/codex`.
Read that exact matrix directly, without installed-copy fallback.
Assigned tiers are those with complete capability rows. This cut assigns `minimal`, `standard`,
and `critical`. Recommend `standard`. Recommend `minimal` when the user
prioritizes cost or speed for ordinary bounded work. Recommend `critical` for
matching high-impact risk.

## Dispatch

Cursor `Task.subagent_type` is a closed enum. Do not dispatch through custom
`~/.cursor/agents` files. For each capability:

1. Resolve `profile`, `subagent_type`, product `model`, and `effort` from
   `tiers.<selected-tier>.<capability>`.
2. Resolve a permitted type and model slug using the live-schema rules below,
   then launch a **fresh** Task (isolated context is the independence guarantee).
   Where `environment` is supported, role agents use `local` in the owning task
   checkout. Choose foreground/background through WORKFLOW "Agent waiting";
   set `run_in_background` only for that supported lifecycle. Do not assume a
   Task-launched root has background continuation. Do not poll.
3. The Task prompt is the packet plus: read
   `${ORCHESTRA_SKILLS_ROOT}/orchestra-role-<role>/SKILL.md`, which is
   self-contained, then execute only the assigned capability. Role mapping:
   `orchestra_analyst` → `orchestra-role-analyst`;
   `orchestra_implementation_worker` → `orchestra-role-implementer`;
   `orchestra_reviewer` → `orchestra-role-reviewer`;
   `orchestra_verifier` → `orchestra-role-verifier`.
4. Resume only the same phase-cohort agent id (`resume`). Never `resume: self`
   for a reviewer or any independent gate. A reviewer's first review of a
   phase is a fresh Task; delta reviews within the same phase resume that same
   reviewer.

Apply the phase verification contract before launching a Task. When the
`Independent verification gate` is `none`, do not create a verifier Task;
matrix entries describe available capabilities, not mandatory agents. Create a
verifier only for a named browser, service/process, mutable-data, credential,
network/external, repository-policy, critical-tier, or selected execution-preset gate.

## Product contract vs live Task slugs

`roles.cursor.toml` records Composer 2.5 Fast, Luna high/xhigh, Grok 4.6
high/xhigh, Grok 4.7 high/xhigh, Fable 5.1 medium, and Sol 5 high as the
product contract.
Pass those names in the packet. The live Task schema may only expose nearby
workers. For matrix defaults use the mapping below without rewriting the product contract or
inventing a Codex `reasoning_effort` field:

| Product model | Product effort | Task worker actually passed |
| --- | --- | --- |
| `composer-2.5-fast` | `fast` | `composer-fast-worker` with `model` `composer-2.5-fast` |
| `gpt-5.6-luna` | `high` | `luna-worker` (`model` inherit unless a Luna-high slug exists) |
| `gpt-5.6-luna` | `xhigh` | `luna-worker` with `model` `gpt-5.6-luna-xhigh` |
| `cursor-grok-4.6` | `high` | `grok-worker` with `model` `cursor-grok-4.6-high` |
| `cursor-grok-4.6` | `xhigh` | `grok-worker` with `model` `cursor-grok-4.6-xhigh` |
| `grok-4.7` | `high` | `grok-worker` with `model` `grok-4.7-high` |
| `grok-4.7` | `xhigh` | `grok-worker` with `model` `grok-4.7-xhigh` |
| `claude-fable-5-1` | `medium` | `generalPurpose` with `model` `claude-fable-5-1-thinking-medium` |
| `gpt-5.6-sol` | `high` | `sol-worker` with `model` `gpt-5.6-sol-high` |

If inherit would select an unintended variant, pass the exact effort slug instead
of inherit. If a later Task schema exposes exact slugs, prefer them and document
the change here. Never substitute `gpt-5.6-luna-low` for Luna xhigh. Never
substitute a different model family for an assigned row; when the exact
effort slug is missing from the live schema, use the same family's closest
effort without rewriting the product contract. This adaptation applies only to
matrix defaults, never an exact user-selected model/effort or preset override;
a missing exact user choice blocks. Record the actual selected slug and any
unverified variant, not an unsupported claim of an exact assignment.

Some CLI and Projects sessions lack the specialized types but expose
`generalPurpose`. In that schema, use a fresh `generalPurpose` Task with the assigned family's explicit
model slug and the same role packet. For example, the observed Grok high slug
`cursor-grok-4.6-high-fast` preserves the family and effort when
`cursor-grok-4.6-high` is absent. The same rule applies to Grok 4.7:
`grok-4.7-high-fast` preserves the family and effort when `grok-4.7-high` is
absent. Record the actual worker and model fields;
the product matrix stays unchanged. If the live schema cannot select the
assigned family, report the missing capability instead of using an inherited
model of another family. Do not copy a specialized worker's `inherit` into a
generic worker under a different parent model. Role behavior, permitted type and
model slug are separate choices. Use only actual schema fields, not an invented
effort argument. Task-root selection belongs to `orchestra-coordinate/host-transports.md`,
not this leaf-role matrix.

## Wait and cleanup

Use foreground completion or supported background notification according to the
owning root's verified lifecycle. WORKFLOW "Agent waiting" owns intervals, completion and diagnosis.
Explicit CLI delegates use their launcher process handle, not the Task wait.

Cursor has no `close_agent`. Require every phase agent to be `completed` with
no active descendant or retained write-capable resource before commit, matching
Codex V2 completed-state evidence.

## Browser

`browser_route: auto | in_app | chrome`. `auto` and `chrome` map to Browser Use
MCP (`plugin-browser-use-browser-use`). `in_app` is `blocked` on Cursor. An
explicit user route is never vetoed or substituted.

Open the scenario with `new_tab` then `wait_for_load`. Never claim or reuse a
user tab. If CallMcpTool fails because the MCP process client is not
registered, call `mcp_auth` once and retry; if it still fails, or Chrome lacks
remote-debugging Allow, return `blocked`. Do not substitute Playwright, the
Cursor IDE browser, Computer Use, or the Browser Use CLI.

Close only the task tab before every handoff. After a browser run, the producer
cites screenshot PNG files in the report; the root opens those exact paths when
consuming the report. Frontend iteration and independent acceptance use
separate tabs and evidence.

## Permissions

Observe the Cursor host permission choice. Do not write `settings.json` or
Codex `config.toml`.
