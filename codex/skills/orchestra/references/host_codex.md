# Codex spawn adapter

When an execution preset is explicitly selected, use `orchestra-delegate` and
WORKFLOW "Delegated execution presets" to resolve each assignment first. CLI
results use that helper, root results stay in the owning conversation, and
native results use this adapter with their exact resolved model and effort.
A `host` result uses the native matrix below. Do not apply native fallback or
closest-model substitutions to preset CLI assignments.

Use this reference only when the execution host is Codex (`spawn_agent` and
`wait_agent` exist). Never mix Codex spawn with Cursor `Task` or Grok `spawn_subagent`.

Resolve the Codex matrix and behavior profiles through
[runtime resources](../runtime.md). Read `tiers.<tier>.<capability>` directly;
each row supplies `profile`, `model`, and `reasoning_effort`. Read the matching
behavior profile and apply WORKFLOW "Host adapters" to choose the native agent
type. Include the exact role skill path and explicit model and effort in the
capability packet. The recommended root is Astra low; availability comes from
the live host catalog. For unsupported rows or a plan from the retired external
integration, follow WORKFLOW "Tier flows and models".

Set `fork_turns: none` on each native spawn. Provider mode detection and
external-model aliases are outside this adapter.

Apply the phase verification contract before resolving a verifier assignment.
When the `Independent verification gate` is `none`, do not spawn
`runtime_verification` or `browser_acceptance`; matrix entries describe
available capabilities, not mandatory agents. Spawn a verifier only for a
named browser, service/process, mutable-data, credential, network/external,
repository-policy, critical-tier, or selected execution-preset gate. Critical phases independently repeat
the applicable deterministic gate already evidenced by the implementation
owner.

Wait for live agents with `wait_agent` in non-interruptive ten-minute windows
(`timeout_ms: 600000`) when the active host supports that duration. Follow
WORKFLOW "Agent waiting" for completion, shorter host limits and diagnosis.
Explicit CLI delegates use their launcher process handle, not `wait_agent`.

After owner cleanup, retire the cohort using completed agents with no live
children or retained resources. Follow WORKFLOW "Phase teardown" for exceptions.

Browser packets use `browser_route: auto | in_app | chrome`. `auto` prefers the
dedicated Chrome connector and may use Codex's in-app Browser only for a
technical availability or capability gap that the in-app Browser can satisfy.
`chrome` and `in_app` remain strict.

Direct sync configures Guardian (`:workspace`, `on-request`, and Auto-review)
as the default. The active permission choice for the task, host, or launcher
remains authoritative.

Task Control owner commands, including `task acknowledge-stop`, use the exact
adapter-provided `CODEX_THREAD_ID`. Never replace it with generated content.
