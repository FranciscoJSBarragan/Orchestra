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
  wrapper command. It is useful during implementation and does not replace the
  hard gate.

## Forbidden substitutions

- Do not treat an ad-hoc `pytest` invocation as a substitute for the hard gate.
