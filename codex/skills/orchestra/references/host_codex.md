# Codex spawn adapter

Use this reference only when the execution host is Codex (`spawn_agent` and
`wait_agent` exist). Never mix Codex spawn with Cursor `Task` or Grok `spawn_subagent`.

Use `${CODEX_HOME:-$HOME/.codex}` as the installed Codex root and
`${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml` as the Codex assignment
matrix. For a dual matrix resolve exactly
`modes.<modelconfig>.tiers.<tier>.<capability>` using the immutable mode from
`session_model.py`. For a legacy matrix resolve exactly
`tiers.<tier>.<capability>`. Require every selected entry to contain only
`profile`, `model`, and `reasoning_effort`. Load
`${CODEX_HOME:-$HOME/.codex}/agents/<profile>.toml`, pass the capability in the
packet, and use the assignment's explicit model and reasoning overrides when
spawning. A profile never selects its capability or assignment.

Always attempt the installed assignment first. Only when a
`repository_context` spawn is rejected before execution because the internal
subagent runtime does not support the assigned model, retry that same
`orchestra_analyst` packet internally with Luna and reasoning `high` only for a
legacy matrix or the dual `external` mode. The dual external retry uses the
installed Orchestra V1 Luna alias; legacy mode uses its existing Luna entry.
The dual `native` mode blocks instead of crossing protocol versions. Record the
substitution only in root memory for the live task when it is permitted. Do not
create a visible Codex task, persist fallback state, edit the source or
installed matrix, or use this fallback for another capability. If any other
capability's assigned model is unsupported, return `blocked`.

Every dispatch starts from a clean context: under multi-agent V2 pass
`fork_turns: none` explicitly on every spawn; under V1 never set
`fork_context: true`.

Wait for live agents with `wait_agent` in non-interruptive ten-minute windows
(`timeout_ms: 600000`). Completion wakes the root immediately; `timed_out`
means continue waiting without `send_input` or `interrupt: true`. A normal
timeout is not a user-visible transition. After 30 accumulated minutes, assess
once only for concrete blocker evidence.

Under V1, call `close_agent` on every phase agent after owner cleanup so
descendants close as well. Under V2, where no true close operation is exposed,
require every phase agent to be `completed` with no active descendant or
retained resource.

Browser packets use `browser_route: auto | in_app | chrome`. `auto` prefers the
dedicated Chrome connector and may use Codex's in-app Browser only for a
technical availability or capability gap that the in-app Browser can satisfy.
`chrome` and `in_app` remain strict.

Orchestra synchronizes Guardian (`:workspace`, `on-request`, and Auto-review)
as the default. The active permission choice for the task, host, or launcher
remains authoritative.
