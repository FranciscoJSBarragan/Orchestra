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

Read the selected matrix from `orchestra/runtime.md`: installed layouts use
`<runtime>/hosts/grok/roles.toml`; prepared source uses
`<source>/hosts/grok/config/roles.grok.toml`, outside `<source>/codex`.
Never silently fall back to another installed copy.
Assigned tiers are those with complete capability rows. This cut assigns `standard` and
`critical`. The live catalog row is `grok-4.7-build-fast` (Grok 4.7 Fast) at
effort `xhigh` and one cost, so there is no cheaper assigned tier. Recommend
`standard`. Recommend `critical` when the brief matches security, credentials,
payments, migrations, destructive actions, or production mutation. If the user
selects `minimal`, stop with `blocked`: Grok matrix row is not assigned.
`critical` uses the same spawn rows as `standard`; it raises root scrutiny and
does not change model or reasoning.

Dispatch every assigned capability through `general-purpose`. Do not treat
unofficial Claude-compat worker types as the Grok product contract. Do not
dispatch Orchestra capabilities through built-in `explore` or `plan` types:
they cannot write task artifacts.

## Dispatch

For each capability:

1. Resolve `profile`, `subagent_type`, product `model`, and `effort` from
   `tiers.<selected-tier>.<capability>`.
   Scope runtime discovery to the host model catalog, live dispatch schema and
   records for the exact current root and dispatched child IDs. Do not search
   unrelated sessions or memory, or recursively search host directories, to
   infer an assignment. Unavailable execution evidence follows step 3; it
   does not authorize broader discovery or a model substitution.
2. Launch a **fresh** subagent. Prefer `spawn_subagent` when its live schema
   can express the assignment, or documented host resolution establishes the
   same assignment without explicit fields. Before relying on inheritance,
   verify the parent model and effort match the row and no applicable per-type,
   role or persona override changes them. Matching the parent alone does not
   establish the child's configured defaults. If the live schema omits
   `subagent_type`, confirm the host's implicit type is `general-purpose`.
   Pass only supported fields; for the schema exposing them use
   `background: true`, `isolation: none`, and `cwd` set to the task checkout.
   Never pass `isolation: worktree` (or `isolation_worktree: true`);
   Orchestra already owns the checkout.
   If native spawn is absent or cannot resolve the assignment, use the host
   `workflow` transport only when it supports one `agent()` call with the
   exact model, effort and `agent_type`. `agent()` has no `cwd`: the root's
   working directory must already be the task checkout. Do not seek a missing
   `spawn_subagent` through `use_tool` or force fields rejected by the catalog.
3. Before accepting the result, compare host-recorded child model and effort
   with the assigned row, whether dispatch was explicit or inherited. Requested
   arguments and a child's self-reported label are not execution evidence.
   An unknown or mismatched assignment blocks acceptance: preserve and reconcile
   any changes and live resources. Another dispatch requires evidence that the
   supported resolution now meets the row; do not repeat an unchanged mismatched
   launch. Do not change global settings or substitute a model to make it succeed.
4. The prompt is the packet plus: read
   `${ORCHESTRA_SKILLS_ROOT}/orchestra-role-<role>/SKILL.md`, which is
   self-contained, then execute only the assigned capability. Role mapping:
   `orchestra_analyst` → `orchestra-role-analyst`;
   `orchestra_implementation_worker` → `orchestra-role-implementer`;
   `orchestra_reviewer` → `orchestra-role-reviewer`;
   `orchestra_verifier` → `orchestra-role-verifier`.
5. Resume only the same phase-cohort agent with `resume_from` after that
   agent has completed. A reviewer's first review of a phase is always a
   fresh spawn; delta reviews within the same phase resume that same
   reviewer, matching the open phase cohort on Codex. A complementary review
   under WORKFLOW "Review policy" uses a fresh reviewer.

An explicit rejection before a child starts permits one corrected dispatch
through a supported route with the same assignment. Confirm no child started;
an active child or ambiguous launch instead follows WORKFLOW "Agent waiting"
and "Conversation continuity". Do not retry, duplicate, or silently omit its
work. If the workflow permits direct root context gathering instead of the
failed analyst, disclose that change and retain its evidence. The root never
substitutes for a required independent role.

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
windows (`timeout_ms: 600000`) when supported by the active host. WORKFLOW
"Agent waiting" owns completion and diagnosis. Explicit CLI delegates use
their launcher process handle. Use `kill_command_or_subagent` only for a
cancellation authorized under that contract.

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
