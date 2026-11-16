# T3 Code host

T3 Code is the host when the session has the `t3-code` MCP tools; when another
MCP server exposes the same tool names, use the `t3-code` server's for every
call. Each task root is a T3 thread on a provider whose `orchestra` entry
skill is installed (Claude Code, Codex, Cursor or Grok today), and every
provider T3 runs is an executor, not a host. This reference maps WORKFLOW
"Host" onto T3; specification, planning, review policy, commits and delivery
follow WORKFLOW.

## Primitives

| Primitive | T3 Code |
| --- | --- |
| `launch_task_root` | `t3_thread_launch` with an explicit workspace strategy |
| `report_to_parent` | `t3_thread_send` in queue mode to the parent thread; a silent child is found with `t3_thread_list` |
| `dispatch_role` | `delegate_task` in async mode, read once with `task_status` |
| `continue_session` | `t3_thread_send`, one long `t3_thread_wait`, then `t3_thread_read` |
| `model_catalog` | `orchestrator_capabilities` |
| `task_checkout` | `t3_worktree_status` and `t3_worktree_handoff` |
| `watch_pr` | `watch_pull_request`, released with `unwatch_pull_request` |
| `browser_surface` | T3's collaborative browser through `preview_open`, `t3_preview_close` and `t3_preview_list`; Claude in Chrome; `codex-cu` |
| `user_preview` | No T3 tool: the preview pack's run steps |
| `ask_user` | `AskUserQuestion` in Claude Code, `request_user_input` in Codex |
| `permissions` | `runtimeMode` inherit |
| `dispatcher_parent` | A Hermes thread |

## Runtime

Install the bundle once for each provider used as a task root, as the
packaging README describes; a second install of the same provider duplicates
skills. The Claude Code bundle's only hook allows read-only tools inside its
installed package, so a Claude child can read its role skill. Settings and flow
overrides live under `${ORCHESTRA_HOME:-$HOME/.orchestra}`.

An agent outside T3 starts Orchestra work there only when the user asks,
through an MCP connection to the T3 Code server (the deployment documents its
endpoint) or T3's local CLI on the same machine. It launches each task root as
"Task roots" defines, and the launched root runs under this reference.
`delegate_task` and `create_threads` need a caller inside a T3 thread.

## Flow rows

A row's `provider` is the `providerInstanceId`, never another instance that
serves the same model id, such as an ACP registry instance; its `model` is the
exact id from the live `orchestrator_capabilities` catalog; and its effort goes
in the effort option that model advertises there, whatever its name
(`effort`, `reasoningEffort` or `reasoning_effort`). A provider whose
instance turns `fastMode` on by default, as Cursor does, gets `fastMode:
false`. A missing model or effort blocks; never substitute silently.
`task_status` `providerInstanceId` and `model` are observed evidence; the
effort is requested only. A later root on another model or provider keeps the
assignment recorded in the plan Decisions.

## Checkout

Call `t3_worktree_status` before task setup.

- Attached: adopt that worktree as the task checkout under WORKFLOW "Task
  checkout and branch" or "Child root setup".
- Not attached, `hybrid`: use the bound checkout as usual.
- Not attached, `managed`: right after specification confirmation, call
  `t3_worktree_handoff` instead of `git worktree add`, with `branch`
  `orchestra/<task-slug>`, `baseRef` the intended base, `startFromOrigin`
  `true` for the fetched upstream or `false` for an explicit local base, a
  `path` under the configured worktree root, and no `continuationPrompt`:
  for Claude and Cursor sessions T3 holds a continuation queued behind a
  handoff instead of starting it (T3 Code issue #15136). Only committed
  base content reaches the new checkout. The handoff ends the turn, so first
  tell the user to send any message to continue in the new checkout. On
  resume, verify path, branch, and HEAD, then run the WORKFLOW canary write.
  Starting the thread in a T3 worktree avoids the handoff entirely.

A T3 worktree, attached or handed off, is T3-owned. Deliver it in managed
mode with `--preserve-task-resources`; the user
releases the worktree and thread from T3, since archiving a thread does not
remove its worktree.

## Role transport

- Dispatch each role with `delegate_task` and `runtimeMode: inherit`, mapped
  from its flow row as "Flow rows" defines; its child runs in the root's bound
  checkout. Prefer `mode: async`: the completion notification wakes the
  root, so end the turn instead of polling, then read the result once with
  `task_status`. Both pair reviewers start in the same turn.
- The packet is the normal role packet plus: do not delegate, launch threads,
  or spawn agents.
- Every fix round is a fresh `delegate_task` with the fix packet, so its
  completion wakes the root. Continue an implementer's thread with
  `t3_thread_send` only for preview absorption or an unfinished turn; that
  message does not reopen the delegated task, so wait on the thread with one
  long `t3_thread_wait` instead of status messages, then read only the new
  turn with `t3_thread_read`.
- Every review round is a fresh `delegate_task` with a new `clientRequestId`:
  the first carries the full bounded review context, a delta round the
  full-review base, prior dispositions and only the delta.

## Task roots

Each task root runs on a provider whose `orchestra` entry skill is installed;
a Hermes parent, or any other thread, can launch children but is not itself an
Orchestra root. A Hermes thread is the dispatcher parent of WORKFLOW
"Dispatcher parent"; how the user reaches Hermes and what it remembers belong
to the user's Hermes configuration. Read `orchestrator_capabilities` before
launch for the live provider, model and option catalog. A parent outside T3
uses the same tools through an MCP connection to the server: it passes
`projectId`, since it has no project to inherit, and the connection's approved
access caps each root's modes. Without `delegate_task`, it runs a leaf role
such as a verifier as its own thread on a `worktree` at the exact revision,
with the role packet.

For a task root, use `t3_thread_launch` with an explicit `workspaceStrategy`:
`worktree` with the approved `baseRef`, an owned `branch` and
`startFromOrigin: false` for local commits. T3 then owns checkout creation and
binds the thread to it; the child adopts that checkout under WORKFLOW "Child
root setup" and never runs `git worktree add` itself. Pass explicit
`modelSelection` and `runtimeMode`: an omitted runtime mode inherits the
caller's, which may be `full-access`. Record the returned `threadId`.

The packet names the parent's `threadId`, and its server when it differs. At
handoff, or at a blocker that needs the parent, the child sends a compact
report naming its own `threadId` through `t3_thread_send` in `queue` mode,
which starts an idle parent and waits behind an active turn. The parent
therefore ends its turn after dispatch and stays available to the user, using
`t3_thread_wait` only when the current turn cannot proceed without that child.
A parent outside T3 has no thread to wake and waits instead. A root on another
T3 server sends that report through an MCP connection to the parent's server
whose token comes from an OAuth `full-access` approval: a `t3 auth session
issue` token stays `approval-required`, and T3 rejects its write to a
`full-access` thread with `runtime_mode_escalation_denied`. A child that stops
without reporting is found through `t3_thread_list` when the parent next
resumes, not by a watcher; the one exception is a root on another server
without that connection, whose status alone, never its transcript, the parent
may also check at low frequency as a safety net. Read details with
`t3_thread_read` from the last known position rather than rereading the whole
timeline. `t3_thread_send` continues the same provider session with its
context intact, so it carries accepted fixes and deltas; use a stable
`clientRequestId`. A task root watches only its own PR, as "Pull requests"
defines; a parent never watches a child's PR, which would bind the parent
thread to that PR's state.

`delegate_task` is a leaf transport, not a task root. Its child runs in the
caller's checkout with no workspace option. From a parent in a shared checkout
it is limited to source-read-only roles (`interactionMode: plan`,
`runtimeMode: approval-required`); a task root bound to its own worktree uses
it for every role, including resumption and review rounds, under "Role
transport". Verify the checkout with Git after it returns.

Archiving a thread does not remove its worktree or branch. Release them through
the child's cleanup handoff after the accepted revision is preserved.

## Pull requests

The task root that opens a PR watches it with T3's pull request watcher
(`watch_pull_request`) after handling the feedback already present, then ends
its turn: T3 wakes it when a check fails, the required checks pass, someone
comments or reviews, or the branch conflicts. A wake is news, not a clean
result; observe the PR again under WORKFLOW "PR path". Only the root that owns
the PR watches it, never a `delegate_task` child or a parent. Call
`unwatch_pull_request` before a handoff or a question so the thread leaves
Working for the user's inbox. T3 does not wake a thread when its PR merges, so
the merging root reports the merge.

## Browser and preview

The root copies the route and tab lines below that a browser packet needs into
that packet; roles never read this reference.

- `auto`: T3's collaborative browser. When it is unavailable, including a
  `preview_open` sandbox or setup error, a Claude child started with
  `--chrome` uses Claude in Chrome and any other child uses `codex-cu`.
- `in_app`: T3's browser only.
- `chrome`: Claude in Chrome only, for a Claude child started with
  `--chrome`; otherwise `blocked`.
- `codex-cu`: the codex-cu MCP server, Codex's computer-use engine driving
  Chrome; the optional server is
  [codex-cu](https://github.com/FranciscoJSBarragan/codex-cu-mcp). Return
  `blocked` when the server, the ChatGPT app or its Chrome extension is
  unavailable. It cannot write files, so copy each screenshot from the path its
  result reports and convert it to the required PNG evidence path.

T3 tab steps: `delegate_task` children receive the `preview_*` tools, and
each child sees only its own tabs. Open with `preview_open`
(`reuseExistingTab: false`, `open: false`, `profileId: incognito` unless
the recipe needs a signed-in profile) and pass its `tabId` on every call; read
page state from one snapshot and save the screenshot with another (`save:
true` returns only its path), copying the file to the PNG evidence path; after
every open attempt, including a failed one, close each task-owned tab with
`t3_preview_close` and confirm with `t3_preview_list` that none remains,
reporting a tab that cannot be closed as retained.

On a Linux host T3's browser needs a one-time
`sudo env "PATH=$PATH" t3 browser setup` (AppArmor); until then `preview_open`
fails with a sandbox error. Orchestra never runs it: tell the user, and an
`in_app` route returns `blocked` naming that command. T3 starts Claude Code
without Chrome integration unless the Claude provider's Launch arguments
include `--chrome`; without the `claude-in-chrome` tools, the Claude Code
fallback is `codex-cu` and `chrome` is `blocked`, so tell the user that
setting enables Claude in Chrome.

User preview adds no T3 tool: the preview pack carries the run steps WORKFLOW
"User preview" defines.

## Questions and gates

A question the user must answer uses `AskUserQuestion` in Claude Code or
`request_user_input` without `autoResolutionMs` in Codex, so the T3 thread
shows that it waits. Call `unwatch_pull_request` first when the root watches
a PR. A task root a Hermes thread launched sends its question to that thread
with `t3_thread_send` instead.
