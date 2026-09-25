# Runtime resources

Resolve paths once from the absolute location of the SKILL.md that the host
actually loaded (resolve symlinks), never from the project working directory. Set
`ORCHESTRA_SKILLS_ROOT` to the parent of that skill's directory. For a reference
or a delegated packet, reuse the owning skill's resolved root.

When the parent of that skills root contains `.codex-plugin/plugin.json` or a
host plugin manifest such as `.devin-plugin/plugin.json`, this is a plugin:
set `ORCHESTRA_RUNTIME_ROOT` to that parent. Otherwise this is a
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
| Devin agent profiles | `<runtime>/agents/<profile>.md` | `~/.config/devin/agents/<profile>.md` |
| Cursor/Grok/Devin matrix and spawn reference | `<runtime>/hosts/<host>/{roles.toml,spawn.md}` | `<runtime>/hosts/<host>/{roles.toml,spawn.md}` |
| Role skills and shared references | `<skills-root>/<skill>/` | `<skills-root>/<skill>/` |

Under a Devin direct-sync installation the skills root is
`~/.config/devin/skills`; under the Devin plugin bundle it is
`<runtime>/skills`.

Every delegated role packet includes the absolute `role_skill` path and the selected
runtime and skills roots. Resolve sibling skills and references from that same
root. Implementation packets and mutable task-root handoffs also name the
absolute shared engineering guidance path and its `#source-comments` section.
A root's global instruction file is not evidence that another host received it. A task-root packet instead names its selected entry skill and those same roots
under WORKFLOW "Initiative coordination". Host behavior, including the plugin's Codex profile composition, is
specified in WORKFLOW "Host adapters" and the selected spawn reference.

The package is read-only. Task Control and coordination data stay under
`$HOME/.orchestra` or the helper's explicit `--state-root`. Checkout settings
stay under `${ORCHESTRA_HOME:-$HOME/.orchestra}`; worktrees retain their existing
configured root. Never point ORCHESTRA_HOME at a plugin
cache, write settings there, or persist a plugin cache path in a task plan.
Resolve paths again after a host restart or plugin update. Plugin loading does
not change global permissions or activate the workflow.

## Conversation continuity

At the start of substantive work, read "Conversation continuity" in the selected
WORKFLOW for follow-ups, worker progress and interruption recovery. It applies
to ordinary skill use as well as the full workflow, without activating it or
creating task state. Reuse that loaded guidance when a casual message arrives;
the message alone does not require resolving or rereading the runtime.

## Prepared remote source

An external coordinator or environment setup may use the shipped
`scripts/prepare_source.py` (source: `codex/scripts/prepare_source.py`) to prepare
or verify a source checkout at an approved full commit SHA. Use the shared
[source preparation recipe](references/source_preparation.md), included with
the skills in every installation mode. Its returned roots select source mode
above; the `workflow` path is explicit because it lives
outside `codex/`. Task workers consume those roots without installing another
runtime. A cache mismatch requires reconciliation, not fallback to a moving ref.
