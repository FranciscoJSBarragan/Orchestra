# Grok Build spawn adapter

When an execution preset is explicitly selected, use `orchestra-delegate` and
WORKFLOW "Delegated execution presets" to resolve each assignment first. CLI
results use that helper, root results stay in the owning conversation, and
native results use this adapter with their exact resolved model and effort.
A `host` result uses the native matrix below. Do not apply native fallback or
closest-model substitutions to preset CLI assignments.

Use this reference only when the execution host is Grok Build (the Grok TUI
session, where Codex `spawn_agent` and Cursor `Task` do not exist). Never mix
the Grok spawn mechanisms below with Codex `spawn_agent` / `wait_agent` /
`close_agent` or Cursor `Task`.

## Host matrix

Read `${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/hosts/grok/roles.toml` directly.
Assigned tiers are those with complete capability rows. This cut assigns `standard` and
`critical`. The live catalog is `grok-4.6` at one cost, so there is no
cheaper assigned tier. Recommend `standard`. Recommend `critical` when the
brief matches security, credentials, payments, migrations, destructive
actions, or production mutation. If the user selects `minimal`, stop with
`blocked`: Grok matrix row is not assigned. `critical` uses the same spawn
rows as `standard`; it raises root scrutiny and does not change model or
reasoning. Do not invent a per-dispatch `reasoning_effort` field.

Dispatch every assigned capability through `general-purpose`. Do not treat
unofficial Claude-compat worker types as the Grok product contract. Do not
dispatch Orchestra capabilities through built-in `explore` or `plan` types:
they cannot write task artifacts.

## Dispatch

For each capability:

1. Resolve `profile`, `subagent_type`, product `model`, and `effort` from
   `tiers.<selected-tier>.<capability>`.
2. Launch a **fresh** subagent with that `subagent_type`. Use
   `spawn_subagent` when the live session schema offers it. Some Grok
   sessions omit it (and it is not reachable through `use_tool`); there,
   dispatch through the host `workflow` script tool with an `agent()` call
   carrying the same fields. Either way pass `background: true`,
   `isolation: none`, and `cwd` set to the exact Orchestra task checkout.
   Never pass `isolation: worktree` (or `isolation_worktree: true`);
   Orchestra already owns the checkout.
3. Pass `model` `grok-4.6` when the live schema accepts it; inheriting the
   parent `grok-4.6` session also satisfies the contract. `effort: inherit`
   means do not invent a Grok `reasoning_effort` field. Do not treat a child's
   self-reported worker label as the assignment.
4. The prompt is the packet plus: read
   `${ORCHESTRA_SKILLS_ROOT}/orchestra-role-<role>/SKILL.md` and the shared
   conduct it names, then execute only the assigned capability. Role mapping:
   `orchestra_analyst` → `orchestra-role-analyst`;
   `orchestra_implementation_worker` → `orchestra-role-implementer`;
   `orchestra_reviewer` → `orchestra-role-reviewer`;
   `orchestra_verifier` → `orchestra-role-verifier`.
5. Resume only the same phase-cohort agent with `resume_from` after that
   agent has completed. A reviewer's first review of a phase is always a
   fresh spawn; delta reviews within the same phase resume that same
   reviewer, matching the open phase cohort on Codex. A second critical
   review, when required, uses a fresh reviewer.

Apply the phase verification contract before launching a subagent. When the
`Independent verification gate` is `none`, do not spawn a verifier; matrix
entries describe available capabilities, not mandatory agents. Spawn one only
for a named browser, service/process, mutable-data, credential,
network/external, repository-policy, critical-tier, or selected execution-preset gate. Critical phases
independently repeat the applicable deterministic gate already evidenced by
the implementation owner.

The host `workflow` tool is only a spawn transport: one `agent()` call per
dispatch. Do not use workflow scripts, personas, or a planning-only host mode
as the Orchestra control plane, and do not encode phases, retries, or gates in
a workflow script. Children cannot spawn children; do not ask them to.

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

Task Control owner commands, including `task acknowledge-stop`, use the
adapter-provided `GROK_SESSION_ID`. Never
replace it with user, page, tool, or model-generated content. If it is
unavailable, stop because Task Control ownership cannot be proven.
