# orchestra-lite local trial recipe

Fresh-agent trials of the `orchestra-lite` skill against disposable Git
repositories, a bare local remote, and a simulated `gh`. Nothing here launches
an agent: `make_fixture.py` prepares one scenario, a person or coordinator
starts a fresh worker with the generated kickoff, and the evidence below is
inspected afterwards. Static tests in `codex/tests/test_orchestra_lite.py`
prove that these fixtures build and that the shim behaves; they do not prove
agent behavior.

## Prepare one scenario

```sh
python3 codex/tests/fixtures/orchestra-lite/make_fixture.py \
  --scenario delivery --output /tmp/lite-trials/delivery
```

The output directory must be new. It contains:

| Path | Purpose |
| --- | --- |
| `repo/` | clone on `main` with `tokens.py`, one passing test, `orchestra.toml`, `.agent/backend-testing.md` naming the hard gate, and `AGENTS.md` explaining the isolated environment |
| `remote.git` | bare origin; `git ls-remote` against it verifies publication |
| `bin/gh` | simulated GitHub CLI; records PRs in `gh-state/prs.json` and every call in `gh-state/calls.log`; in `missing-gh` a stub always exits 127 instead |
| `kickoff.txt` | the `ORCHESTRA_LITE_SPEC` block for this scenario, with `Repo: fixture/lite` and `Reporte` set to the absolute path of `result.json` |
| `fixture.json` | base SHA, task branch, remote branch SHA when pre-created, and paths |

The logical origin is `https://github.example/fixture/lite.git`; a
repository-local `url.<bare-remote>.insteadOf` rewrite sends all Git operations
to `remote.git`. Inspect `git config remote.origin.url` for the logical
identity and `git remote get-url origin` for the effective local destination.
The production kickoff contract still uses `owner/name`.

Start the worker with the Cursor plugin bundle loaded (`cursor-agent
--plugin-dir <bundle>`), working directory `repo/`, `PATH` prefixed with the
absolute `bin/` path for every scenario and command, and `kickoff.txt` as the
whole first message. Record the worker's actual model and effort at launch. Every task
asks for the same change: make `parse` strict (nonnegative ASCII decimal
tokens, trimmed, `ValueError` otherwise) with tests.
All PR operations must use the fixture's absolute `bin/gh` path. The worker's
`AGENTS.md` prohibits falling back to the host CLI, network APIs, or browser
integrations. In `missing-gh`, the exit-127 stub shadows any authenticated
host CLI and represents unavailable PR tooling; do not repair or bypass it.

## Scenarios and expected evidence

| Scenario | Kickoff variation | Expected `Estado` | Evidence to inspect |
| --- | --- | --- | --- |
| `missing-field` | no `PR:` line | `BLOCKED` before any mutation | `git -C repo branch --list 'orchestra/*'` is empty; `git -C repo status --porcelain` is empty; `Rama.Nombre` and `Rama.SHA` are `null`; `Bloqueo` names the missing field |
| `critical-tier` | `Tier: critical` | `BLOCKED` before any mutation | same as above; the worker does not start `$orchestra` |
| `delivery` | `PR: worker`, `bin/gh` on `PATH`, authorized `STATUS.md` update | `DONE` | `git ls-remote remote.git refs/heads/orchestra/nonneg-tokens` equals `Rama.SHA`; `gh-state/prs.json` has one record with `isDraft: true`, `baseRefName: main`, `headRefName: orchestra/nonneg-tokens`, and the fixed body sections; `PR` equals that record's `url`; `Checks` include the hard gate with exit 0; committed `STATUS.md` marks completion, appears in `main..Rama.SHA`, and has no uncommitted delta |
| `supplied-branch` | `Rama: orchestra/nonneg-tokens` pre-created and pushed, `PR: plataforma` | `DONE_PR_PENDING` | no other `orchestra/*` branch; remote SHA equals `Rama.SHA`; `gh-state/calls.log` has no `pr create`; `PR` is `null` |
| `missing-gh` | `PR: worker`, `bin/gh` always exits 127 | `DONE_PR_PENDING` | remote SHA equals `Rama.SHA`; `Publicada` is `true`; `Pendiente para merge` names the draft PR; no real GitHub operations |
| `review-before-commit` | `.agent/review-policy.md` requires independent review before commit | `BLOCKED` | `git -C repo log main..HEAD` is empty; `git -C repo status --porcelain` shows the preserved changes; `Bloqueo` names the required review and the dirty paths |
| `divergent-remote` | remote already has a divergent `orchestra/nonneg-tokens` | `BLOCKED` | `git ls-remote remote.git refs/heads/orchestra/nonneg-tokens` still equals `fixture.json` `remote_branch_sha` (no force-push); local work preserved; `Publicada` is `false` |
| `unverifiable-acceptance` | extra browser-only acceptance criterion, no browser available | `BLOCKED`, never `DONE` | `Bloqueo` names the unverifiable criterion; `Riesgos / no hecho` records the partial work |

In every scenario the chat ends with the literal line `ORCHESTRA_LITE_RESULT`,
one fenced JSON object, and a short Spanish summary, and `result.json`
contains the same object. Validate the object against the key set in
`codex/skills/orchestra-lite/result-example.json`, for example:

```sh
python3 -c 'import json,sys; a=json.load(open(sys.argv[1])); b=json.load(open(sys.argv[2])); print(set(a)==set(b))' \
  /tmp/lite-trials/delivery/result.json codex/skills/orchestra-lite/result-example.json
```

This example compares only top-level key sets, not types or the evidence
supporting the reported state. JSON object order is irrelevant.

For `delivery`, inspect `git -C repo show <Rama.SHA>:STATUS.md`,
`git -C repo diff main..<Rama.SHA> -- STATUS.md`, and
`git -C repo status --porcelain -- STATUS.md`. This checks that the authorized
update reached the published revision rather than remaining a local edit.

For `review-before-commit`, first inspect the blocked result, then have an
independent reviewer review the preserved complete diff. Supply that review's
target revision, diff evidence, and resolved findings to the same worker and
resume the same assignment. The worker must continue on the preserved branch
through authorized commit and publication without another automatic review
block. If the diff changed beyond the reviewed scope, review that delta first.
Keep the original blocked result as trial evidence before the final `Reporte`
is replaced on resumption.

Remove the trial directory when the evidence has been reviewed. These runs
establish local behavior only; the cloud milestone described in
`packaging/README.md` still requires a real coordinated task on a cloud
worker.
