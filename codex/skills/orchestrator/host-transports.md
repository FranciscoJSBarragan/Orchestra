# Task-root transports

WORKFLOW "Initiative coordination" owns the behavior. This reference maps it to
host primitives; it is not a second scheduler or a promise of tool availability.
Inspect the current host tools or CLI help before relying on a transport.
Apply WORKFLOW "Initiative coordination" to investigation-only authority and
continuation. Observe launch, role-tool availability, readable evidence and
continuation separately on the actual host before claiming that route works.

## T3 Code

T3 Code hosts provider sessions behind one UI and exposes app-owned
orchestration through its `t3-code` MCP tools. Each task root runs on a provider
whose `orchestra` entry skill is installed; a Hermes parent under WORKFLOW
"Hermes dispatcher", or any other thread, can launch children but is not itself
an Orchestra root.
Read `orchestrator_capabilities` before launch for the live provider, model and
option catalog. A parent outside T3 uses the same tools through an MCP
connection to the server: it passes `projectId`, since it has no project to
inherit, and the connection's approved access caps each root's modes. Without
`delegate_task`, it runs a leaf role such as a verifier as its own thread on a
`worktree` at the exact revision, with the role packet.

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
which starts an idle parent and waits behind an active turn. The parent therefore ends its turn after dispatch and
stays available to the user, using `t3_thread_wait` only when the current turn
cannot proceed without that child. A parent outside T3 has no thread to wake
and waits instead. A root on another T3 server sends that report through an
MCP connection to the parent's server whose token comes from an OAuth
`full-access` approval: a `t3 auth session issue` token stays
`approval-required`, and T3 rejects its write to a `full-access` thread with
`runtime_mode_escalation_denied`. A child that stops without reporting is
found through `t3_thread_list` when the parent next resumes, not by a watcher;
the one exception is a root on another server without that connection, whose
status alone, never its transcript, the parent may also check at low
frequency as a safety net. Read details
with `t3_thread_read` from the last known position rather than rereading the
whole timeline. `t3_thread_send` continues the same provider
session with its context intact, so it carries accepted fixes and deltas; use a
stable `clientRequestId`. A task root watches only its own PR, as the
[T3 Code](../orchestra/references/host_t3.md) reference defines; a parent never
watches a child's PR, which would bind the parent thread to that PR's state.

`delegate_task` is a leaf transport, not a task root. Its child runs in the
caller's checkout with no workspace option. From a parent in a shared checkout
it is limited to source-read-only roles (`interactionMode: plan`,
`runtimeMode: approval-required`); a task root bound to its own worktree uses
it for every role, including resumption and review rounds, under
[T3 Code](../orchestra/references/host_t3.md). Verify the checkout with Git
after it returns.

Archiving a thread does not remove its worktree or branch. Release them through
the child's cleanup handoff after the accepted revision is preserved.

