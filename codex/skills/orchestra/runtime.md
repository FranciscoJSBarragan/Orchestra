# Runtime resources

Resolve paths once from the absolute location of the SKILL.md that the host
actually loaded (resolve symlinks), never from the project working directory. Set
`ORCHESTRA_SKILLS_ROOT` to the parent of that skill's directory. For a reference
or a delegated packet, reuse the owning skill's resolved root.

When the parent of that skills root contains `.codex-plugin/plugin.json`, this
is a plugin: set `ORCHESTRA_RUNTIME_ROOT` to that parent. Otherwise this is a
direct-sync installation: use `${ORCHESTRA_HOME:-$HOME/.orchestra}`. For explicit
source development, use `codex/scripts`, `codex/agents`, `codex/config`, and
`docs/WORKFLOW.md` in that same source checkout instead of installed copies.

These are task-local path bindings, not variables guaranteed by the host.
Substitute their absolute values in tool calls or set them in each shell call;
never assume that an export survives into another tool or child process. Read
only the selected runtime. A missing plugin resource is an installation error;
do not silently fall back to another installed version.

| Resource | Plugin | Direct sync |
| --- | --- | --- |
| Workflow | `<runtime>/WORKFLOW.md` | `<runtime>/WORKFLOW.md` |
| Helpers | `<runtime>/scripts/` | `<runtime>/scripts/` (Codex compatibility mirror: `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/`) |
| Execution presets | `<runtime>/execution-presets.toml` | `<runtime>/execution-presets.toml` |
| Codex matrix | `<runtime>/hosts/codex/roles.toml` | `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml` |
| Codex behavior profiles | `<runtime>/profiles/<profile>.toml` | `${CODEX_HOME:-$HOME/.codex}/agents/<profile>.toml` |
| Cursor/Grok matrix and spawn reference | `<runtime>/hosts/<host>/{roles.toml,spawn.md}` | `<runtime>/hosts/<host>/{roles.toml,spawn.md}` |
| Role skills and shared references | `<skills-root>/<skill>/` | `<skills-root>/<skill>/` |

Every delegated role packet includes the absolute `role_skill` path and the selected
runtime and skills roots. Resolve sibling skills and references from that same
root. A task-root packet instead names its selected entry skill and those same roots
under WORKFLOW "Initiative coordination". Host behavior, including the plugin's Codex profile composition, is
specified in WORKFLOW "Host adapters" and the selected spawn reference.

The package is read-only. Task Control and coordination data stay under
`$HOME/.orchestra` or the helper's explicit `--state-root`. Checkout settings
stay under `${ORCHESTRA_HOME:-$HOME/.orchestra}`; worktrees retain their existing
configured root. Never point ORCHESTRA_HOME at a plugin
cache, write settings there, or persist a plugin cache path in a task plan.
Resolve paths again after a host restart or plugin update. Plugin loading does
not change global permissions or activate the workflow.
