# Task-root transports

WORKFLOW "Initiative coordination" owns the behavior. This reference maps it to
host primitives; it is not a second scheduler or a promise of tool availability.
Inspect the current host tools or CLI help before relying on a transport.
Apply WORKFLOW "Initiative coordination" to investigation-only authority and
continuation. Observe launch, role-tool availability, readable evidence and
continuation separately on the actual host before claiming that route works.

## Codex desktop

For user-requested separate tasks, list projects and select the real project ID.
Use the app's `create_thread` with the approved packet. Its current contract
defaults to `local`; choose the app's `worktree` environment only when the user
explicitly requested it and `isGitRepository` is true. That selection may cover
an approved batch without another question per task. A starting branch/ref also
requires the user's selection. Otherwise launch the authorized local task with
an explicit `managed` checkout override: before any source, plan or task-state
writes, its root creates/adopts the isolated task checkout and thereafter uses
that path exclusively. This avoids parallel writers under an installed hybrid
default. Respect an explicit shared-checkout choice by serializing writes.

Select the task-root Codex model/effort through the app's actual controls only
when explicitly requested, otherwise retain the user's configured default.
The child uses Codex's selected tier/preset for its ordinary roles; Cursor model
slugs do not apply. Record `threadId` and `hostId`; a queued `clientThreadId` is
not a usable task handle. Resolve it through native task state before sending
or waiting. Follow the app's worktree lifecycle and release tools.

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

## Cursor Projects

The parent Project coordinator's model and reasoning remain user-controlled.
The configured task-root selection for this route is **`grok-4.7-xhigh`**, unless
the user explicitly selects another supported assignment. Each child is the
technical root for one full Orchestra task, reports to the parent and launches
its own proportional roles. Its selected tier/preset still determines role
resources; do not derive root resources from `independent_review` or copy the
root's model into every role. An unavailable exact choice blocks dispatch.

Inspect the actual Project coordinator launch tool first. Worker-side evidence
of `Task` does not establish that the coordinator exposes that same tool, and
this mapping does not introduce `CreateAgent` or `SendToAgent`. A worker schema
has exposed `Task` with cloud/local environments, a model slug, remote base ref,
optional Build ID, background and resume. Treat this as a capability to verify
in the current session, not a completed Projects acceptance test.

Where that schema supplies task-root dispatch, a cloud Task creates an isolated
VM from the published `cloud_base_branch`; a local Task is a role in the owning
VM. One cloud task root per independent task is sufficient. The root adopts the
actual checkout under WORKFLOW "Task checkout and branch", compares HEAD with
the approved full product SHA and reconciles host metadata mismatches. A Build ID
pins an environment snapshot, not product or Orchestra identity. Resolve pinned
instructions using [source preparation](../orchestra/references/source_preparation.md);
role packets carry their exact selected source matrix and adapter paths.

Use an exposed specialized type only when appropriate; otherwise `generalPurpose`
with explicit `model: grok-4.7-xhigh` can carry the task-root packet. There is no
separate `effort` field in the reported schema. The root then uses the Cursor
spawn adapter for roles with `environment: local` where supported, sharing its
frozen checkout for review. Another cloud VM sees remote commits, not the current
uncommitted source, so it is not an interchangeable review transport. Actual
local-child tool access, deeper nesting and browser support still need evidence.

WORKFLOW "Agent waiting" chooses foreground roles when this root's background
continuation is unverified. Use background task-root dispatch only when the parent
has a supported completion lifecycle. Keep native cloud identity/URL separate
from the role's resume handle until their relationship is established. Resume
only after confirmed completion/stoppage; an active background task is not a new
assignment. The observed resume schema cannot change model. A required model
change needs a stopped owner and bounded handoff, never a duplicate live writer.
Questions return through the actual blocker/result channel; no extra messaging
API or credit-exhaustion status is assumed. Record requested slug and observed
metadata separately: a reported `grok-4.7` family does not verify xhigh execution.

Before VM release apply the shared retention contract: verify task-branch remote
SHA when push is authorized and accessible reports/screenshots, or the explicitly
selected retained-result route. Do not equate a VM-local absolute path with a
shared Project path. Cloud Builds may provision sources through the consumer's
existing setup; this adapter does not modify builds or install a service.

## Cursor IDE/CLI and Grok

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

## Devin

Devin remains a full Orchestra execution host with its existing role/spawn
adapter. Higher-level native task-root creation, nesting and continuation require
verification on the selected Devin surface; this reference does not claim that
transport from leaf CLI support. Report a precise task-root transport gap when
unavailable. An explicitly selected supported root CLI session can be used with
its verified lifecycle, without routing a full task through the leaf delegate or
silently switching the user's harness.
