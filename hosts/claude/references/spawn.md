# Claude Code spawn adapter

When an execution preset is explicitly selected, use `orchestra-delegate` and
WORKFLOW "Delegated execution presets" to resolve each assignment first. CLI
results use that helper, root results stay in the owning conversation, and
native results use this adapter with their exact resolved model and effort.
A `host` result uses the native matrix below. Do not apply native fallback or
closest-model substitutions to preset CLI assignments.

Use this reference only when the execution host is Claude Code (the `Agent`
and `SendMessage` tools exist). Inside T3 Code, checkout and role transport
follow the orchestra skill's `references/host_t3.md`; this matrix still
assigns every row. Never mix the Claude Code spawn mechanisms
below with Codex `spawn_agent` / `wait_agent` / `close_agent`, Cursor `Task`,
Grok `spawn_subagent`, or Devin `run_subagent`.

## Activation

Orchestra activates only on an explicit invocation: the `orchestra` skill
(direct sync: `/orchestra`; plugin bundle: `/orchestra:orchestra`) or an
unequivocal imperative to start Orchestra. The plugin ships no extra slash
command. Plan mode is a planning-only host mode: observe it and never change
it.

## Host matrix

Read the selected matrix from `orchestra/runtime.md`: installed layouts use
`<runtime>/hosts/claude/roles.toml`; prepared source uses
`<source>/hosts/claude/config/roles.claude.toml`, outside `<source>/codex`.
Never silently fall back to another installed copy.
Assigned tiers are those with complete capability rows. This cut assigns
`minimal`, `standard`, and `critical`. Recommend `standard`. Recommend
`minimal` when the user prioritizes cost or speed for ordinary bounded work.
Recommend `critical` when the brief matches security, credentials, payments,
migrations, destructive actions, or production mutation.

Recommend a root of at least `high` effort on every tier: Sonnet 5.5 `high` on
`minimal` and `standard`, Opus 5.5 `high` on `critical`. Low-effort rows suit
bounded roles, not the root, which owns the approval gates. The user's current
`/model` and `/effort` remain authoritative: Orchestra never changes or
respawns the root.

## Dispatch

For each capability:

1. Resolve `profile`, `subagent_type`, product `model`, and `effort` from
   `tiers.<selected-tier>.<capability>`. `subagent_type` is the registered
   Claude Code agent `<profile>_<effort>`; its frontmatter pins that effort
   because the `Agent` tool accepts no effort argument.
2. Resolve the agent name from the active installation, using the same
   detection signal as `orchestra/runtime.md`:
   - Direct sync (agents under `~/.claude/agents/`): pass the bare name, e.g.
     `subagent_type: "orchestra_analyst_high"`.
   - Plugin bundle (the parent of the skills root contains
     `.claude-plugin/plugin.json`): pass `orchestra:<subagent_type>`, e.g.
     `subagent_type: "orchestra:orchestra_analyst_high"`.
   Do not mix the two forms within one phase cohort. In explicit source mode,
   reading `<source>/hosts/claude/agents/` does not register an agent; verify
   the named agents are available from the selected installation or a
   session `--plugin-dir` at the pinned revision, otherwise report that
   dispatch gap.
3. Launch a **fresh** `Agent` with that `subagent_type` and the `model` alias
   mapped below. Never omit `model`: an omitted model inherits the root's.
   Never pass `isolation: "worktree"`; Orchestra already owns the checkout.
   Never dispatch an Orchestra capability through `general-purpose`,
   `Explore`, `Plan`, or a fork: they do not carry the profile's effort, and
   `Explore` and `Plan` are one-shot and cannot be resumed.
4. The `Agent` tool has no working-directory field. The packet names the
   absolute task checkout; the child runs every command and edit there with
   absolute paths, never in the root's session directory.
5. The prompt is the packet plus: read the `role_skill` path supplied by the
   packet, which is self-contained, then execute only the assigned
   capability. Role mapping:
   `orchestra_analyst` → `orchestra-role-analyst`;
   `orchestra_implementation_worker` → `orchestra-role-implementer`;
   `orchestra_reviewer` → `orchestra-role-reviewer`;
   `orchestra_verifier` → `orchestra-role-verifier`. When the packet supplies
   no explicit `role_skill` path, use
   `~/.claude/skills/orchestra-role-<role>/SKILL.md`.
6. Resume only the same phase-cohort agent with `SendMessage` to its agent ID
   after it has returned; a resume keeps its original model. Every review,
   including a delta review, is a fresh `Agent` under WORKFLOW "Review
   policy".

| Product model | `Agent` `model` passed |
| --- | --- |
| `claude-sonnet-5-5` | `sonnet` |
| `claude-opus-5-5` | `opus` |

A family alias resolves to the root's exact model when the root runs that
family, otherwise to the host's current model of that family. If the live
`Agent` schema cannot select the row's family, report the missing capability
instead of inheriting another model. The child transcript under
`~/.claude/projects/` records the executed model; the requested alias alone
is not observed evidence.

Apply the phase verification contract before launching an agent. When the
`Independent verification gate` is `none`, do not spawn a verifier; matrix
entries describe available capabilities, not mandatory agents. Spawn one
only for a named browser, service/process, mutable-data, credential,
network/external, repository-policy, critical-tier, or selected
execution-preset gate. Critical phases independently repeat the applicable
deterministic gate already evidenced by the implementation owner.

Every profile sets `disallowedTools: Agent`, so children cannot spawn
children; do not ask them to.

## Wait and cleanup

Claude Code may run an agent in the foreground or the background. Follow
WORKFLOW "Agent waiting": consume the foreground return or the completion
notification for a background agent; never poll its transcript or output.
Background agents surface tool approvals in the root session and cannot ask
the user questions; a denied call is never bypassed. Use `TaskStop` only for a
cancellation authorized under that contract. Explicit CLI delegates use their
launcher process handle, not the Claude Code wait.

Claude Code has no `close_agent`. Require every phase agent to have returned
its result with no active descendant or retained write-capable resource
before commit, matching Codex V2 completed-state evidence.

## Browser

`browser_route: auto | in_app | chrome | codex-cu`. `codex-cu` uses the
codex-cu MCP server as WORKFLOW defines. `auto` and `chrome` map to Claude in
Chrome (the `claude-in-chrome` MCP server, enabled with `--chrome` or
`/chrome`). `in_app` is `blocked` on Claude Code. Inside T3 Code, T3's
collaborative browser is the first `auto` surface and the only `in_app`
surface as WORKFLOW defines; without `--chrome` in the Claude provider's
Launch arguments, the `auto` fallback is `codex-cu` and `chrome` is
`blocked`. An explicit user route is never vetoed or substituted.

Open each scenario in a new task-owned tab; never claim or reuse a user tab.
Save every screenshot to disk and copy it to the required PNG evidence path.
Close only that tab before every handoff. If the extension is not connected,
the session uses API-key authentication, or the tool is denied, return
`blocked`. Do not substitute Playwright, Computer Use, or another browser.

## Permissions

Observe the Claude Code permission mode and rules. Do not write
`~/.claude/settings.json`, project `.claude/settings*.json`, or any agent
`permissionMode`. Plugin agents ignore `permissionMode` by design.

Claude Code reads and edits without prompting only inside its working
directories, and children inherit them. The plugin bundle ships one
`PreToolUse` hook that allows `Read`, `Glob`, and `Grep` only inside the
installed package, so every agent reads its skills, references, and workflow
without a prompt. Read package files with those tools, not with shell
commands. Direct sync has no such hook: ask the user to add its runtime and
skills roots with `/add-dir`, `--add-dir`, or `additionalDirectories`, or to
approve those reads. Never add a directory or permission rule yourself.

## Task checkout

`hybrid` keeps the task in the launch directory. For a `managed` checkout,
after creating or adopting the worktree, call `EnterWorktree` with its `path`
before the first dispatch; the user confirms once, and the session and every
later agent then work and write there. Before cleanup removes that worktree,
call `ExitWorktree` with `action: "keep"`; Orchestra, not Claude Code, removes
it. Never call `EnterWorktree` with `name`: it creates a Claude-owned branch
outside the Orchestra checkout contract.
