# Policy: Orchestra source verification

## Scope

Applies to changes under this repository that affect Orchestra's workflow
contract, skills, helpers, tests, or delivery checks. `orchestra.toml`
`[[checks]]` already runs the same `--full` command at merge and local
integration; that delivery boundary does not replace the phase hard gate.

## Hard gate

- Command: `python3 codex/scripts/validate_suite.py --full`
- Working directory: repository root
- Any implementation that touches this repository is complete only when that
  command exits 0.

## Diagnostic only

- `python3 codex/scripts/validate_suite.py --quick` is the versioned pre-commit
  wrapper command (the hook additionally selects `--comment-target staged`). It is useful during implementation and does not replace the
  hard gate.

## Forbidden substitutions

- Do not treat an ad-hoc `pytest` invocation as a substitute for the hard gate.

## Source comment checks

The canonical validator also checks introduced Python comments/docstrings against
`HEAD` by default; `--comment-base SHA` selects another available revision.
The hook selects the staged snapshot, excluding unrelated unstaged text. CI uses
`--comment-base ci` with fetched history; the validator resolves the event base.
An unavailable base is actionable failure, never an empty check. A new branch
uses its default-branch merge base; only an initial commit uses an empty tree.
A first default-branch push containing several commits requires an explicit
reviewed base rather than comparing HEAD to itself. Recognized functional
exceptions cover current Python consumers; a new documentation/runtime consumer
requires evidence and a bounded checker update, not an unused waiver API.

`--comment-full-scan` is diagnostic for exports without Git and legacy inventory.
Only `--comment-full-scan --comment-enforce-full-scan` declares the entire source
scope repaired and gates that inventory. Neither mode rewrites source. Other
languages require their native checks or review; Python coverage is not universal
policy enforcement. Shared engineering guidance owns allowed source content.
