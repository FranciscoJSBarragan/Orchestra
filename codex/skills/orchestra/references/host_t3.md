# T3 Code layer

Use this reference when the `t3-code` MCP tools (`delegate_task`,
`t3_worktree_handoff`, `orchestrator_capabilities`) are available. T3 Code
hosts the provider session; the provider remains the Orchestra host and its
matrix assigns every capability except the review pair WORKFLOW defines for
T3. T3 replaces only checkout creation and role transport. Specification,
planning, review policy, commits, and delivery are unchanged.

## Outside T3

An agent outside T3 with an MCP connection to a T3 Code server (the
deployment documents its endpoint) starts Orchestra work there only when the
user asks. It launches each task root as a top-level thread through the T3
section of [host transports](../../orchestra-coordinate/host-transports.md),
and the launched root runs under this reference. `delegate_task` and
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

The checkout is T3-owned. Deliver with `--preserve-task-resources`; the user
releases the worktree and thread from T3, since archiving a thread does not
remove its worktree.

## Role transport

Dispatch each role with `delegate_task`; its child runs in the root's bound
checkout. Map the matrix row onto `target`: the host's `providerInstanceId`,
the row's exact `model` from the live `orchestrator_capabilities` catalog, and
the row's effort in that model's advertised option (`effort` on Claude,
`reasoningEffort` on Codex and Grok). A pair reviewer uses the provider
instance that serves its model, and both start in the same turn. A missing
model or effort blocks; never substitute. On Claude Code this sets effort per dispatch, so the
`<profile>_<effort>` agents are not needed. A selected execution preset's CLI
assignment may use `delegate_task` with the same provider, model, and effort.

- Use `runtimeMode: inherit`; T3 permissions are observed, never raised.
- The packet is the normal role packet plus: do not delegate, launch threads,
  or spawn agents.
- Prefer `mode: async`; the completion notification wakes the root. End the
  turn instead of polling, then read the result once with `task_status`.
- When a phase has an independent gate, start its verifier and the review
  (both of the pair) in the same turn, on the same SHA.
- Every fix round is a fresh `delegate_task` with the fix packet, so its
  completion wakes the root. Continue an implementer's thread with
  `t3_thread_send` only for preview absorption or an unfinished turn; that
  message does not reopen the delegated task, so wait on the thread with one
  long `t3_thread_wait` instead of status messages, then read only the new
  turn with `t3_thread_read`.
- Every review round is a fresh `delegate_task` with a new `clientRequestId`:
  the first carries the full bounded review context, a delta round the
  full-review base, prior dispositions and only the delta.
- `task_status` `providerInstanceId` and `model` are observed evidence; the
  effort is requested only.
- After every return, check Git status and HEAD. A read-only role that changed
  anything other than its declared report blocks, as under WORKFLOW "CLI
  delegation".

Native host spawn stays valid; use one transport per phase cohort. Task roots
for an initiative follow the T3 section of
[host transports](../../orchestra-coordinate/host-transports.md).

## Browser

T3's collaborative browser is the first `auto` surface and the only `in_app`
surface on every provider, with the tab lifecycle WORKFLOW "Test permissions
and browser routing" defines; `delegate_task` children receive its `preview_*`
tools, and each child sees only its own tabs. When it is unavailable, `auto`
falls back to the host mapping. On a Linux host T3's browser needs a one-time
`sudo env "PATH=$PATH" t3 browser setup` (AppArmor); until then `preview_open`
fails with a sandbox error. Orchestra never runs it: tell the user, and an
`in_app` route returns `blocked` naming that command. T3 starts Claude Code without Chrome
integration unless the Claude provider's Launch arguments include `--chrome`;
without the `claude-in-chrome` tools, the Claude Code fallback is `codex-cu`
and `chrome` is `blocked`, so tell the user that setting enables Claude in
Chrome.
