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

## Authorized source delivery and personal installation

On 2026-09-26, the owner explicitly authorized commit, push and installation
updates. Core commit `98ebcd6ff36f0602663a875c49c0c1470236c30a` was integrated
by fast-forward into [Orchestra main](https://github.com/FranciscoJSBarragan/Orchestra).
Tasks commit `99450ba88a2504d6442ab5a0f73e984990d732c3` initialized the public
[OrchestraTasks repository](https://github.com/FranciscoJSBarragan/OrchestraTasks).
Both implementation commits passed their GitHub Actions checks.

The owner's existing plugin route was preserved across Codex, Cursor, Grok and
Devin. Each now has separate core and Tasks bundles. Installed files matched
generated sources: core 84/84/84/88 and Tasks 19/21/19/21 files respectively,
excluding bytecode caches and the Codex reinstall cachebuster. Grok's updater
reported a live local source while its installed copy was stale; native removal
and installation restored verified parity. Grok and Devin discovery each
reported 19 core skills and one companion skill, without duplicate Task entries.
Codex's plugin manager confirmed both installs; Cursor's local bundle contents
were verified without starting a model session.

Existing Codex and Cursor MCP registrations now select Tasks helpers. Their
configured commands passed MCP initialization and eight-tool discovery.
Unrelated configuration and the existing Codex server approval settings were
preserved. The Hub launch agent now uses the Tasks checkout; the macOS app was
rebuilt and installed from Tasks, with a working bundled helper. Both launch
agents were running and the Hub health endpoint reported `ok`. The obsolete
owned helper symlink was retired into the private installation backup.

Configurations, plugin roots, the app and SQLite databases were backed up before
replacement. Both databases passed integrity checks; logical content hashes
were unchanged after installation and read-only smoke checks. No schema or
card migration was performed. Existing sessions need a fresh host/plugin load
to consume the new skill set and MCP configuration.

Updating an existing checkout can leave ignored bytecode, local virtualenvs
and generated screenshots in the retired `codex/control` and `hub` directories.
These local artifacts were preserved in the private backup after confirming
that no tracked source or active service depended on those directories. Core
conformance requires the retired component directories to be absent.

## Remaining acceptance limits

These source, package, fixture and bounded installed-runtime checks do not prove
model-driven workflow behavior or live discovery through every route, especially Tasks' direct-sync skill
symlinks, including Cursor's `CURSOR_PLUGIN_ROOT` for direct-sync local plugins, or an
actual model's adherence to the missing-companion, stop and
registration instructions. Independent source review assesses those instructions;
a later authorized workflow trial must exercise actual host loading and a
bounded card lifecycle. No benchmark or adoption improvement is inferred.

The authorized personal installation replacement is complete. Broader host
adoption, public marketplace distribution and the held-out model-quality
comparison remain deferred; no release or new model evaluation was run.
