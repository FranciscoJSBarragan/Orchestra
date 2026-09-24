# Devin spawn adapter

When an execution preset is explicitly selected, use `orchestra-delegate` and
WORKFLOW "Delegated execution presets" to resolve each assignment first. CLI
results use that helper, root results stay in the owning conversation, and
native results use this adapter with their exact resolved model and effort.
A `host` result uses the native matrix below. Do not apply native fallback or
closest-model substitutions to preset CLI assignments.

Use this reference only when the execution host is Devin (the Devin session,
where `run_subagent` and `read_subagent` exist). Never mix the Devin spawn
mechanisms below with Codex `spawn_agent` / `wait_agent` / `close_agent`,
Cursor `Task`, or Grok `spawn_subagent`.

## Activation

Orchestra activates only on an explicit invocation: the `orchestra` skill
(direct-sync: `/orchestra`; plugin bundle: `/orchestra:orchestra`) or an
unequivocal imperative to start Orchestra. Devin plugins do not contribute a
host slash-command of their own the way Cursor ships
`commands/orchestra.md`; that omission is deliberate. The host mode
(planning-only vs. full workflow) is observed and never changed by this
adapter.

## Host matrix

Read `${ORCHESTRA_RUNTIME_ROOT:-${ORCHESTRA_HOME:-$HOME/.orchestra}}/hosts/devin/roles.toml` directly.
Assigned tiers are those with complete capability rows. This cut assigns
`standard` and `critical`. Every capability pins to `swe-2-max` at the same
reasoning depth (the slug already encodes max reasoning), so there is no
cheaper assigned tier. Recommend `standard`. Recommend `critical` when the
brief matches security, credentials, payments, migrations, destructive
actions, or production mutation. If the user selects `minimal`, stop with
`blocked`: Devin matrix row is not assigned. `critical` uses the same spawn
rows as `standard`; it raises root scrutiny and does not change model or
reasoning.

## Dispatch

For each capability:

1. Resolve `profile`, `subagent_type`, product `model`, and `effort` from
   `tiers.<selected-tier>.<capability>`. `subagent_type` is the Devin custom
   profile name (`orchestra_analyst`, `orchestra_implementation_worker`,
   `orchestra_reviewer`, `orchestra_verifier`); `profile` equals
   `subagent_type` in every row.
2. Resolve the exact `profile` value to pass to `run_subagent` from the
   active installation, using the same detection signal as
   `codex/skills/orchestra/runtime.md` (which names `.codex-plugin` for Codex;
   the Devin analogue is `.devin-plugin`):
   - Direct-sync installation (skills root's parent has no
     `.devin-plugin/plugin.json`): pass `profile = "<subagent_type>"` bare,
     e.g. `run_subagent(profile="orchestra_analyst", ...)`.
   - Plugin bundle installation (the parent of the skills root contains
     `.devin-plugin/plugin.json`, so the runtime root is that plugin
     directory and profiles are namespaced under `orchestra:`): pass
     `profile = "orchestra:<subagent_type>"`, e.g.
     `run_subagent(profile="orchestra:orchestra_analyst", ...)`.
   Record which form was used; do not mix the two within one phase cohort.
3. Launch a **fresh** subagent with `run_subagent` carrying the `profile`
   resolved in step 2. Use foreground by default so the user sees tool
   approvals and the result returns inline. Use background only when the
   owner must remain available and every tool the subagent will call is
   pre-approved; a background subagent auto-denies any tool that is not
   pre-approved and notifies on completion (`read_subagent`). Do not
   busy-poll; consume the completion notification then `read_subagent`.
4. `run_subagent` does not accept a per-dispatch `model` field. The model is
   pinned in the profile frontmatter as `swe-2-max`; `effort: inherit` means
   do not invent a Devin reasoning field. If a matrix row names a model other
   than `swe-2-max`, report the gap without substituting; never rewrite the
   product contract or pin a different family in the profile.
5. The prompt is the packet plus: read the `role_skill` path supplied by the
   packet and the shared conduct it names, then execute only the assigned
   capability. Role mapping:
   `orchestra_analyst` → `orchestra-role-analyst`;
   `orchestra_implementation_worker` → `orchestra-role-implementer`;
   `orchestra_reviewer` → `orchestra-role-reviewer`;
   `orchestra_verifier` → `orchestra-role-verifier`. When the packet supplies
   no explicit `role_skill` path, use
   `~/.config/devin/skills/orchestra-role-<role>/SKILL.md`.
6. Resume only the same phase-cohort subagent after it has completed or
   failed; a resume always runs in foreground and reuses the same `profile`
   form (bare or `orchestra:`-namespaced) used for the original spawn. A
   reviewer's first review of a phase is always a fresh spawn; delta reviews
   within the same phase resume that same reviewer, matching the open phase
   cohort on Codex. A second critical review, when required, uses a fresh
   reviewer.

Apply the phase verification contract before launching a subagent. When the
`Independent verification gate` is `none`, do not spawn a verifier; matrix
entries describe available capabilities, not mandatory agents. Spawn one
only for a named browser, service/process, mutable-data, credential,
network/external, repository-policy, critical-tier, or selected
execution-preset gate. Critical phases independently repeat the applicable
deterministic gate already evidenced by the implementation owner.

Children cannot spawn children; do not ask them to. There is no
`close_agent`; require every phase subagent to be `completed` with no active
descendant or retained write-capable resource before commit, matching Codex
V2 completed-state evidence.

## Wait and cleanup

Foreground dispatch returns the result inline; the owner stays blocked until
the subagent finishes. Background dispatch plus the completion notification
plus `read_subagent` is the wait contract; do not busy-poll. Explicit CLI
delegates use their launcher process handle, not the Devin wait.

Devin has no `close_agent`. Treat the `read_subagent` result (or the
foreground return) as the evidence of completion; require it before commit.

## Browser

`browser_route: auto | in_app | chrome`. Devin has no native browser surface.
`auto` is `blocked` (no built-in browser to drive). `in_app` is `blocked`
(no in-app preview surface). `chrome` is `blocked` unless a dedicated Chrome
connector is later documented here. An explicit user route that names an
installed browser MCP is never vetoed or substituted; pass that MCP through
unchanged. An explicit Codex CLI Chrome handoff uses `orchestra-delegate`
under WORKFLOW "CLI delegation", for example with `--executor codex --model
gpt-6-luna --effort max --capability browser_acceptance --browser-route chrome`
when that exact assignment is selected. Verify the CLI model and Chrome connector
are available; do not substitute another model or browser. Without a supported
handoff, required browser acceptance stays blocked. User preview is not a
replacement for the independent gate.

## Permissions

Observe the Devin host permission choice (`--permission-mode` and the host
config). Do not write `~/.config/devin/config.json` or any Devin permission
profile. Background subagents auto-deny tools that are not pre-approved;
foreground subagents surface approvals to the user.

## Identity

Task Control owner commands, including `task acknowledge-stop`, use the
adapter-provided `ORCHESTRA_DEVIN_THREAD_ID` supplied by the `SessionStart`
hook (installed by the plugin or the managed `config.json` merge) from the
stable `session_id`. Never replace it with
user, page, tool, or model-generated content. If it is unavailable, stop
because Task Control ownership cannot be proven.
