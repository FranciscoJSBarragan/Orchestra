# Core / Tasks separation acceptance

## Reviewed scope

The owner approved extracting the optional task manager after an independent
Opus 5.5 Medium architecture consultation. There are no real active cards to
migrate. Core retains modular skills, the full workflow, Lite, CLI delegation,
initiative coordination, profiles, host execution adapters, local plans and
Git delivery. Orchestra Tasks owns cards, global snapshots, MCP, identity hooks
and Hub clients. See WORKFLOW "Attached Tasks companion" for operational rules.

The local extraction records its baseline and source mapping in Tasks'
`PROVENANCE.md`: Orchestra `1e0720e7e84825f36da758d0f4a3e292996192d1`.
The transferred service/database/MCP and most Hub sources are unchanged. The
extraction does not redesign their schemas or repair completed-card recovery
from another owner. Both distributions have their own source and installers.

## Repeatable acceptance

| Boundary | Evidence |
| --- | --- |
| Core without Tasks | Core validator rejects Task source surfaces; four package variants omit Task helpers, control code, skill, hooks and MCP. Existing local-plan, full-flow, Lite, delegation, review and delivery tests still run. |
| Tasks without core imports | Tasks validator rejects private core imports; relocated bundle CLI runs with isolated data and self-contained preparation instructions. |
| Hook location | Actual Cursor/Devin hook commands run from an unrelated directory after relocation. Missing or conflicting identity stays blocked. |
| Retiring combined sync | Core fixtures retire digest-owned helpers, skill copies, MCP and old identity hooks, preserve data and the new Tasks hook, and block the entire update on drift. |
| Pair installation | Tasks `test_core_pair.py`, with explicit `ORCHESTRA_CORE_SOURCE`, exercises both install orders, updates and removal in disposable homes. Each retains the other's runtime/configuration. A version-only Codex fixture is used. |
| Partial Tasks removal | Distribution tests remove one host while retaining shared skill links for the other selected host, then remove the rest. |
| User configuration | Distribution tests preserve unrelated TOML/JSON, settings and modes, retain the Codex MCP write-approval setting, honor custom Codex homes, reject symlink destinations and protected roots, and restore content/modes after an injected manifest failure. |
| Desktop helper | Swift tests cover selected helper, absent-default fallback and blocked explicit missing helper. Build includes only Tasks sources. |

Run core `python3 codex/scripts/validate_suite.py --full` from its root.
Run Tasks `python3 scripts/validate_suite.py --full` from its root; set
`ORCHESTRA_CORE_SOURCE` to the core checkout to include pair acceptance.
Run `sh hub/menubar/test.sh` and `sh hub/menubar/build.sh` in Tasks on macOS.
Build all four targets in each repository and validate their manifests.
No command in this recipe installs into the real home or starts a model.

The pair regression exposed core inserting its permission block inside the
Tasks marker span when the MCP table was first. Core now prepends its top-level
block; both installers' marked spans remain intact. The independent review also
caught loss of the MCP's explicit write-approval setting and the packaged Cursor
hook's use of a workspace-relative path. Both have direct behavioral coverage.

## Review and observed validation

On 2026-09-26, the same Devin CLI review session (`equal-earl`, Devin 3000.11.3,
observed Claude Opus 5.5 Medium) accepted the implementation after I1/I2 and
bounded advisory corrections. The reviewer used file reads/searches and did
not implement the changes or run the checks. Core conformance and the final
package regeneration remained root-owned acceptance work after that verdict.

Core full conformance passed all 17 checks with exit code 0. All eight final
package manifests passed validation. Tasks full validation passed 88 tests including the optional pair case, plus
54 Hub and 31 TUI tests. Swift tests and app build passed. These counts identify
this local extraction run, not future required test counts.

## Limits and next delivery boundary

These are local source, command, package and fixture checks. They do not prove
live skill discovery through every host, especially Tasks' direct-sync skill
symlinks, including Cursor's `CURSOR_PLUGIN_ROOT` for direct-sync local plugins, or an
actual model's adherence to the missing-companion, stop and
registration instructions. Independent source review assesses those instructions;
a later authorized installation trial must exercise actual host loading and a
bounded card lifecycle. No benchmark or adoption improvement is inferred.

Active installations remain on the earlier combined version until a separately
authorized replacement. Source commits, remote repository creation, push,
publication and installation are separate from this local implementation.
The held-out model-quality comparison remains deferred.
