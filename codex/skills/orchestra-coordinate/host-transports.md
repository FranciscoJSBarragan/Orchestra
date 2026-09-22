# Task-root transports

WORKFLOW "Initiative coordination" owns the behavior. This reference maps it to
host primitives; it is not a second scheduler or a promise of tool availability.
Inspect the current host tools or CLI help before relying on a transport.

## Codex desktop

For user-requested separate tasks, list projects and select the real project ID.
Use the app's `create_thread` with the approved packet. Inspect
`isGitRepository`: use its managed worktree route for an isolated Git child,
unless the user explicitly selected the saved checkout; use local for a
non-Git project. Pass a starting branch only when explicitly selected. Record
the returned `threadId` and `hostId`; a pending `clientThreadId` is not a usable
task handle. Resolve it through host task state before sending or waiting.

Wait using `wait_threads` for the known targets and previous cursors. Consume
compact completion/attention events; read full task turns only for a named
missing fact or failure. Resume with `send_message_to_thread` to the same task.
Keep native task questions visible to the user; do not answer an unresolved
material choice on their behalf. Opening a panel is not dispatch.

A saved project can include several folders. Resolve Git roots and applicable
instructions separately for each; primary-folder discovery is not evidence that
secondary instructions, skills or configuration were loaded. App worktrees and
PR operations target the selected primary repository, so independent mutable
repositories normally need separate tasks. Remote hosts may have different
project and tool support; inspect rather than infer parity.

The app-created checkout is already isolated. A full Orchestra child adopts
that clean, collision-free owned checkout under WORKFLOW's supplied-checkout
rule, rather than creating a second worktree. Follow that section's explicit
namespace/observability choice and cleanup handoff for retained local refs.
For internal subtasks that are
not user-owned separate tasks, use the available native agent protocol only
when it supports the required responsibility and lifecycle; do not create
sidebar tasks merely to emulate leaf subagents.

## Cursor and Grok

Use a native isolated task/session when the actual interface exposes persistent
handles, continuation, completion and the child capabilities. Otherwise an
explicitly selected CLI can host a separate root conversation in an owned
checkout. Verify its catalog, help and required tools first. A native leaf Task
that cannot itself delegate cannot execute a full Orchestra child; choose a
supported root session or report that limitation, without changing the route.

The root conversation uses the CLI directly, not `delegate.py`: that helper
deliberately enforces leaf-role authority, unchanged HEAD and no further agents.
Keep prompts and event output at private paths outside the checkout, retain the
process handle, and let the native session own its history. For current CLIs,
the relevant primitives are:

| Host | Start in the owned checkout | Exact continuation |
| --- | --- | --- |
| Cursor | `cursor-agent --print --output-format stream-json --workspace <checkout> --model <supported-model> <packet>` | Add `--resume <observed-chat-id>` with only the current delta. |
| Grok | `grok --cwd <checkout> --model <supported-model> --reasoning-effort <supported-effort> --output-format streaming-json --prompt-file <private-packet>` | Add `--resume <observed-session-id>` with a new delta prompt file. |

These are argument shapes, not shell interpolation templates. Use an argv API
or safely quoted arguments; never interpolate a prompt into shell code. Do not
pass leaf-only `--no-subagents` to a child that needs role agents. Do not add
`--force`, `--yolo`, bypass permissions, trust or sandbox overrides merely to
make the run finish. Preserve the user's actual permission authority; a CLI
that needs unavailable interactive approval returns a blocker. Browser evidence
still uses the selected host's supported browser route.

Use structured events to obtain the exact session handle and terminal response;
do not treat log silence or file modifications as progress. A process handle
supports completion-aware waiting; a lost handle calls for session inspection,
not a duplicate launch. Diagnose only the relevant tail on a protocol failure.
Resume only after the host confirms no active writer remains. If the transport
cannot establish whether dispatch took effect, stop that child for explicit
reconciliation while independent children may continue.

An interactive terminal is useful when the selected CLI requires interaction;
it is not inherently cheaper or a remedy for polling. Prefer the host's
completion signal and compact terminal result in either mode. Do not install
a PTY monitor, status daemon or repeated diff reader.
