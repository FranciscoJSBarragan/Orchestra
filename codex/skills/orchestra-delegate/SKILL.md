---
name: orchestra-delegate
description: Delegate a bounded assignment through Codex, Cursor, or Grok Build CLI, or resolve an explicitly selected execution preset. Supports standalone work without activating Orchestra.
---

# Delegate one capability

Keep scope, routing, acceptance, and delivery in the owning conversation. Read
`Standalone tools` and `CLI delegation` in
`${ORCHESTRA_HOME:-$HOME/.orchestra}/WORKFLOW.md` (source fallback:
[WORKFLOW](../../../docs/WORKFLOW.md)). Those sections own the policy. Use
the applicable [role and capability](../orchestra/SKILL.md) router's
contract; do not forward the full workflow or conversation to the CLI.

## Prepare the assignment

When a preset is selected, read WORKFLOW `Delegated execution presets` and
resolve its assignment before the steps below. Example (no process starts):

```sh
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/delegate.py" \
  --preset standard-delegate --host codex --tier standard \
  --capability general_implementation --resolve-only
```

Use the actual owning `--host`. For planning, pass the observed `--root-model`
to reuse a matching root without changing its effort; add
`--independent-planning` only for a named independent investigation or missing
context. CLI results use the execution command below with `--preset` and
`--host` instead of `--executor`, `--model`, and `--effort`. `root` stays in the
conversation; `native` uses the owning Codex adapter with the exact returned
profile/model/effort and fresh context; `host` uses that host's browser matrix.
Verify native model/protocol availability rather than falling back to CLI.

Use `--attempt 2` or `--attempt 3` only after the root admits the corresponding
recovery under WORKFLOW. The helper never retries or decides an attempt failed.
Carry forward the evidence and current edits; the third attempt uses a fresh
Codex session. A user-supplied `--presets-file` selects customized assignments
without overwriting the managed file. Keep independent review fresh regardless
of who implemented the change.

1. Resolve the requested executor, exact model, supported effort, checkout,
   capability, scope, acceptance, and permission authority. Infer already
   established facts; do not re-ask for granted permissions. Inspect
   `cursor-agent models` / `grok models` and the selected CLI's `--help` when
   availability or flags are not current. Never substitute a model silently.
   For Codex, use `codex exec --help` and the configured model catalog;
   `--effort` maps to `model_reasoning_effort`. Codex is a valid worker for a
   Cursor or Grok root. Keep browser acceptance in the owning host; Codex CLI
   cannot provide the Desktop browser and does not accept that capability.
2. Inspect current HEAD and dirty paths. Bound ownership before launching
   another writer. Create the prompt and a unique event-log path in a private
   directory outside the repository. The prompt names the role skill,
   objective, allowed paths, evidence, acceptance, constraints, and expected
   output. Approved phases also supply their exact artifact IDs and required
   reports; direct assignments use inline results.
3. Start a fresh independent reviewer session. Resume an existing session only
   for the same logical assignment, with the current revision and a focused
   delta. Never resume an implementer as its own independent reviewer.

## Execute and inspect

Run the shared helper (source fallback: `codex/scripts/delegate.py`):

```sh
python3 "${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/delegate.py" \
  --repo <checkout> --executor <codex|cursor|grok> --capability <capability> \
  --model <exact-cli-model> --expected-head <current-sha> \
  --prompt-file <private-prompt> --log-file <new-private-log> \
  --permissions <default|trusted> --timeout <seconds>
```

For Codex or Grok, add `--effort <supported-effort>` when selected. For a continuation,
add `--resume <exact-session-id>` and choose a new log path. Trusted execution
requires the user's permission authority. Analysts/reviewers retain native
read-only mode; verifiers use execution mode for authorized checks and remain
source-read-only under the role and content checks. CLI permissions do not
constitute an OS sandbox or authorize delivery. The helper does not modify
global permission settings.
Codex resume requires a UUID. Read the helper's observed session and terminal
result; an unknown observed model is not evidence of a different model.

For verification that writes a report inside the checkout, declare each new
untracked output file with `--output-path <repo-relative-file>`. This cannot
authorize tracked source changes. Ordinary ignored build outputs are outside
the Git content comparison; inspect relevant evidence separately. Prefer a
private output directory outside source for runtime reports.

Read the complete compact JSON result, including status, session, terminal
evidence, HEAD, changed paths, and diagnostic log. Do not load all raw events
by default. Inspect the actual diff and required checks before acceptance.
An `ok` execution is not an independent review or proof of quality. On a
partial or blocked result, inspect any edits before choosing an explicit
resume; never replay a mutating prompt automatically. Authentication, quota,
permission, and unsupported model failures stay with the selected executor.

Return the actual result and remaining limitation to the owning conversation.
Remove prompt files when no longer needed; retain private logs only through
the assignment's review/recovery lifecycle. Continue review and authorized
delivery through the existing role and delivery tools.
