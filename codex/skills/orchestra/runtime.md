# Runtime resources

Resolve paths once from the absolute location of the SKILL.md that the provider
actually loaded (resolve symlinks), never from the project working directory.
Set `ORCHESTRA_SKILLS_ROOT` to the parent of that skill's directory. For a
reference or a delegated packet, reuse the owning skill's resolved root.

When the parent of that skills root contains `.codex-plugin/plugin.json` or a
provider plugin manifest such as `.claude-plugin/plugin.json` or
`.cursor-plugin/plugin.json`, this is a plugin: set `ORCHESTRA_RUNTIME_ROOT` to
that parent. Otherwise this is explicit source mode: bind `source_root` to the
prepared checkout, runtime to `<source>/codex` and skills to
`<source>/codex/skills`, and use the source map in
[source preparation](references/source_preparation.md) instead of installed
copies.

These are task-local path bindings, not variables guaranteed by the provider.
Substitute their absolute values in tool calls or set them in each shell call;
never assume that an export survives into another tool or child process. Read
only the selected runtime. A missing package resource is an installation error;
do not silently fall back to another installed version.

| Resource | Package path |
| --- | --- |
| Workflow | `<runtime>/WORKFLOW.md` |
| Helpers | `<runtime>/scripts/` |
| Flow assignment | `<runtime>/flow.toml`, overridden by `${ORCHESTRA_HOME:-$HOME/.orchestra}/flow.toml` |
| Role skills and shared references | `<skills-root>/<skill>/` |

Every delegated role packet includes the absolute `role_skill` path and the
selected runtime and skills roots. Resolve sibling skills and references from
that same root. Implementation packets and mutable task-root handoffs also name
the absolute shared engineering guidance path and its `#source-comments`
section. A root's global instruction file is not evidence that another provider
received it. A task-root packet instead names its selected entry skill and
those same roots under WORKFLOW "Initiative coordination". Dispatch is
specified in WORKFLOW "T3 Code host" and the [T3 Code](references/host_t3.md)
reference.

The package is read-only. Checkout settings and flow overrides stay under
`${ORCHESTRA_HOME:-$HOME/.orchestra}`; worktrees retain their existing
configured root. Never point ORCHESTRA_HOME at a plugin cache, write settings
there, or persist a plugin cache path in a task plan. Resolve paths again after
a provider restart or plugin update. Plugin loading does not change global
permissions or activate the workflow.

## Conversation continuity

At the start of substantive work, read "Conversation continuity" in the selected
WORKFLOW for follow-ups, worker progress and interruption recovery. It applies
to ordinary skill use as well as the full workflow, without activating it or
creating task state. Reuse that loaded guidance when a casual message arrives;
the message alone does not require resolving or rereading the runtime.
