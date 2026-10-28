# T3 Code host

T3 Code is the host of every Orchestra task. Its `t3-code` MCP tools
(`delegate_task`, `t3_worktree_handoff`, `orchestrator_capabilities`) create
the checkout and carry every role, and WORKFLOW "Flow assignment" names each
role's provider, model and effort. When another MCP server exposes the same
tool names, use the `t3-code` server's for every call. A later root on another
model or provider
keeps the assignment recorded in the plan Decisions. Specification, planning,
review policy, commits and delivery follow WORKFLOW.

## Outside T3

An agent outside T3 starts Orchestra work there only when the user asks,
through an MCP connection to the T3 Code server (the deployment documents its
endpoint). It launches each task root as
a top-level thread through
[host transports](../../orchestrator/host-transports.md), and the launched
root runs under this reference. `delegate_task` and
`create_threads` need a caller inside a T3 thread.

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

Dispatch each role with `delegate_task`; its child runs in the root's bound
checkout. Map the resolved row onto `target`: the row's `provider` is the
`providerInstanceId`, never another instance that serves the same model id,
such as an ACP registry instance; its exact
`model` from the live `orchestrator_capabilities` catalog; and its effort in
the effort option that model advertises there, whatever its name (`effort`,
`reasoningEffort` or `reasoning_effort`). A provider whose instance turns
`fastMode` on by default, as Cursor does, gets `fastMode: false`. Both pair
reviewers start in the same turn. A missing model or effort blocks; never
substitute silently.

- Use `runtimeMode: inherit`; T3 permissions are observed, never raised.
- The packet is the normal role packet plus: do not delegate, launch threads,
  or spawn agents.
- Prefer `mode: async`; the completion notification wakes the root. End the
  turn instead of polling, then read the result once with `task_status`.
- Every fix round is a fresh `delegate_task` with the fix packet, so its
  completion wakes the root. Continue an implementer's thread with
  `t3_thread_send` only for preview absorption, a cleanup-only follow-up or
  an unfinished turn; that
  message does not reopen the delegated task, so wait on the thread with one
  long `t3_thread_wait` instead of status messages, then read only the new
  turn with `t3_thread_read`.
- Every review round is a fresh `delegate_task` with a new `clientRequestId`:
  the first carries the full bounded review context, a delta round the
  full-review base, prior dispositions and only the delta.
- `task_status` `providerInstanceId` and `model` are observed evidence; the
  effort is requested only.
- After every return, check Git status and HEAD. A read-only role that changed
  anything other than its declared report blocks, as under WORKFLOW "T3 Code
  host".

Task roots for an initiative follow
[host transports](../../orchestrator/host-transports.md).

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

## Browser

T3's collaborative browser is the first `auto` surface and the only `in_app`
surface on every provider, with the tab steps the browser acceptance playbook
defines; `delegate_task` children receive its `preview_*`
tools, and each child sees only its own tabs. When it is unavailable, `auto`
falls back as WORKFLOW "Test permissions and browser routing" defines. On a Linux host T3's browser needs a one-time
`sudo env "PATH=$PATH" t3 browser setup` (AppArmor); until then `preview_open`
fails with a sandbox error. Orchestra never runs it: tell the user, and an
`in_app` route returns `blocked` naming that command. T3 starts Claude Code without Chrome
integration unless the Claude provider's Launch arguments include `--chrome`;
without the `claude-in-chrome` tools, the Claude Code fallback is `codex-cu`
and `chrome` is `blocked`, so tell the user that setting enables Claude in
Chrome.
