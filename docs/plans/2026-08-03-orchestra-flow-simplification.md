# Orchestra Flow Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development to
> implement this plan task-by-task (or executing-plans only as a fallback when
> subagents are unavailable). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Orchestra workflow leaner and smarter: self-serve role
skills as the single source of agent behavior, a decide-by-default autonomy
policy for the orchestrator, one canonical home per rule, a thinner
coordination layer, and safer model-config handling — without changing the
product's authority boundaries.

**Architecture:** Six phases, each independently reviewable and committable.
Mechanical script/test hygiene first (de-risks everything after), then the
coordination artifact-locator removal, then the flagship role-skill
restructuring, then the autonomy + documentation consolidation, then
model-config generation and spawn-context hardening. Verified facts from Codex
0.146.0 ground the design: subagents read `$CODEX_HOME` without escalation
under `:workspace`; subagents receive the skills catalog; profile-pinned
models override spawn overrides (so profiles stay behavior-only); V2 spawns
default to `fork_turns: all` (so Orchestra must pass `none`); V1/V2 protocol
split for external models is real and stays.

**Tech Stack:** Python 3 stdlib scripts + `unittest`, TOML configs, Markdown
skills per agentskills.io spec, Codex CLI 0.146 multi-agent runtime.

**Non-goals (explicitly out of scope):** hub client changes (deferred to
`2026-08-03-hub-simplification-notes.md`), deep `sync.py` internal rewrite
(TOML mask / cache-root discovery stay as-is this round), removing the
`session_model.py` gate or the native/external dual concept (validated as a
real Codex protocol constraint), any change to user authority gates for
production/data/security/payments/destructive actions, and model-specific
prompt overlays per assigned model (deferred to
`2026-08-03-model-specific-prompt-overlays.md`).

**Prompting baseline (GPT-5.6):** the orchestrator runs on GPT-5.6 (Sol); the
official GPT-5.6 prompting guide is a design input for every prose change in
this plan, applied model-agnostically to the base skills:

- *Favor leaner prompts / state each instruction once.* Internal evals cited
  by the guide: leaner system prompts improved scores ~10-15% while cutting
  total tokens 41-66%. This is the quantitative rationale for Phase 3
  (shared conduct dedup) and Phase 4 (one canonical home per rule).
- *Define autonomy and approval boundaries as one compact policy.* The guide
  warns that repeating "ask first" / "do not mutate" / "wait for approval"
  causes unnecessary approval requests — the exact over-asking failure
  observed in real Orchestra sessions. Task 4.1 adopts the guide's compact
  policy shape and Task 4.2 removes the repetitions.
- *Rely on intent understanding.* Provide domain context, hard constraints,
  approval boundaries, and success criteria; do not prescribe every step;
  say explicitly when an ambiguity should trigger a question.
- *Concise by default.* GPT-5.6 is more concise than predecessors; broad
  "be concise"/"omit narration" restatements are trimmed where they do not
  encode a product requirement or correct a measured gap.
- Base role skills stay model-agnostic; per-model adaptations are a deferred
  overlay mechanism (see the deferred-overlays note).

---

## Phase 1: Script and test hygiene

Mechanical consolidation. No behavior change. Makes every later phase cheaper
and safer to review.

### Task 1.1: Consolidate shared helpers in `_common.py`

**Files:**
- Modify: `codex/scripts/_common.py`
- Modify: `codex/scripts/commit_phase.py`, `codex/scripts/adopt_worktree.py`,
  `codex/scripts/coordination.py`, `codex/scripts/integrate_local.py`,
  `codex/scripts/policy.py`, `codex/scripts/session_model.py`
- Test: existing suite `codex/tests/` (no new tests; refactor must keep all green)

- [ ] **Step 1: Run the full suite to capture the green baseline**

Run: `python3 -m unittest discover -s codex/tests -v 2>&1 | tail -5`
Expected: all tests pass (baseline; suite currently has ~214 tests).

- [ ] **Step 2: Extend `_common.py` with the consolidated API**

```python
"""Shared helpers for Orchestra scripts."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# One pattern for 40-char (SHA-1) and 64-char (SHA-256) object names.
SHA_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def git(repo: Path, *args: str, literal_pathspecs: bool = True) -> subprocess.CompletedProcess:
    prefix = ["git"]
    if literal_pathspecs:
        prefix.append("--literal-pathspecs")
    return run([*prefix, "-C", str(repo), *args])


def git_value(repo: Path, *args: str) -> str | None:
    proc = git(repo, *args)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def emit(payload: dict) -> None:
    json.dump(payload, sys.stdout, sort_keys=True)
    sys.stdout.write("\n")


def blocked(reason: str, **details) -> None:
    emit({"status": "blocked", "reason": reason, **details})
    raise SystemExit(1)
```

Preserve the existing exported names (`SHA_PATTERN`, `_git`, `_run`) as thin
aliases so current importers keep working during the migration, then migrate
each script and delete the aliases at the end of this task.

- [ ] **Step 3: Migrate each script to the consolidated helpers**

In order (each is a small diff): `commit_phase.py` (drop local `_git`),
`adopt_worktree.py` (drop local `_git`, keep its `literal_pathspecs=False`
call sites via the keyword), `integrate_local.py` (drop inline `_git`),
`coordination.py` (drop its private `SHA_PATTERN` and `_git_value`; import
from `_common`), `policy.py` and `session_model.py` (drop duplicate
`blocked()` implementations). Do not change any emitted `status` values or
CLI arguments.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m unittest discover -s codex/tests 2>&1 | tail -3`
Expected: identical pass count to the Step 1 baseline.

- [ ] **Step 5: Commit** — via the `commitbot` skill (never raw `git commit`)

### Task 1.2: Make tests assert behavior, not wording

**Files:**
- Modify: `codex/tests/test_commit_phase.py`, `codex/tests/test_pr_flow.py`,
  `codex/tests/test_session_model.py`, `codex/tests/test_validate_suite.py`
  (~20 asserts total)

- [ ] **Step 1: Replace exact-message asserts with status/reason-category asserts**

Pattern for every occurrence:

```python
# Before
self.assertIn("does not permit the PR lane", payload["reason"])
# After
self.assertEqual(payload["status"], "blocked")
self.assertIn("reason", payload)
```

Keep asserting the *category* only where the test's purpose is to distinguish
two different block causes (use a short stable keyword like `"policy"` or
`"authorization"`, never a full sentence).

- [ ] **Step 2: Run the full suite**

Run: `python3 -m unittest discover -s codex/tests 2>&1 | tail -3`
Expected: all pass.

- [ ] **Step 3: Commit** — via `commitbot`

---

## Phase 2: Coordination artifact-locator removal

The `artifacts` SQLite table duplicates the filesystem: content already lives
at `git rev-parse --git-path orchestra/artifacts` and the plan manifest
already records exact IDs and private paths. `tasks` and `activities` stay
(the hub consumes them).

### Task 2.1: Verify the hub does not consume the artifacts table

**Files:** read-only check

- [ ] **Step 1: Grep the hub for artifact queries**

Run: `rg -n "artifacts" hub/orchestra_hub hub/tui hub/menubar --glob '!*.venv*'`
Expected: no SQL against an `artifacts` table. If any hit exists, stop and
re-scope this phase before deleting anything.

### Task 2.2: Remove the `artifact` command from `coordination.py`

**Files:**
- Modify: `codex/scripts/coordination.py`
- Modify: `codex/tests/test_coordination.py`

- [ ] **Step 1: Update tests first**

Delete `artifact put/list/get` test cases. Add one regression test that an
old database containing an `artifacts` table still serves `task` and
`activity` commands (tolerate, never migrate or drop):

```python
def test_legacy_artifacts_table_is_ignored(self):
    # create db via current schema, then add a legacy artifacts table
    conn = sqlite3.connect(self.db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS artifacts (id TEXT PRIMARY KEY)")
    conn.commit(); conn.close()
    result = self._run_coordination("task", "list")
    self.assertEqual(result["status"], "ok")
```

- [ ] **Step 2: Remove the `artifacts` table DDL, the `artifact` subcommand,
  and its validation helpers from `coordination.py`**

Keep `SCHEMA_VERSION` handling; new databases simply create two tables. Do
not add a migration that drops the table from existing databases.

- [ ] **Step 3: Run coordination tests**

Run: `python3 -m unittest codex.tests.test_coordination 2>&1 | tail -3`
Expected: pass.

- [ ] **Step 4: Commit** — via `commitbot`

### Task 2.3: Move artifact publication to a plain filesystem convention

**Files:**
- Modify: `codex/skills/orchestra/SKILL.md` (artifact instructions)
- Modify: `codex/skills/orchestra/references/*.md` (each `artifact put` mention)
- Modify: `codex/agents/*.toml` (coordination paragraphs; superseded fully in
  Phase 3, so here only replace the `artifact put` sentences)
- Modify: `docs/WORKFLOW.md`, `docs/ARCHITECTURE.md` (artifact sections)

- [ ] **Step 1: Define the convention (single paragraph, canonical in WORKFLOW.md)**

```markdown
Agents write each semantic handoff directly as UTF-8 Markdown under the
task-private directory `git rev-parse --git-path orchestra/artifacts`, named
`<NN>-<kind>[-p<phase>].md` with a zero-padded creation ordinal (for example
`03-plan-phase-p2.md`). The file name is the artifact identifier. Packets and
the plan manifest reference these exact file names; no database locator
exists. Kind conventions and immutability rules are unchanged.
```

- [ ] **Step 2: Replace every `coordination.py artifact put` instruction with
  "write the file per the artifact convention and return its exact name"**

The fail-soft language simplifies to: "If the artifacts directory cannot be
created or written, return the complete report inline."

- [ ] **Step 3: Run the repo validator and fix any doc-consistency checks it
  raises that reference `artifact put`**

Run: `python3 codex/scripts/validate_suite.py`
Expected: `ok` (adjust `validate_suite.py` checks that assert the old wording;
keep structural checks).

- [ ] **Step 4: Run full suite, then commit** — via `commitbot`

---

## Phase 3: Self-serve role skills (flagship)

One skill per role becomes the single source of behavior. Profiles become
minimal stubs that point the spawned agent at its role skill. Capability
playbooks stay as references inside the main orchestra skill. Verified: under
`:workspace` a subagent reads `$CODEX_HOME` without escalation, and subagents
receive the skills catalog, so the skills are also directly usable outside
Orchestra (the user's explicit goal).

Skill-authoring rules applied throughout (per writing-skills best practices):
`description` starts with "Use when…", triggers only, never a workflow
summary; verb-first naming avoided here in favor of the stable
`orchestra-role-*` namespace for discoverability; body target under 500 words
per skill; no duplicated content — shared conduct is one referenced file.

### Task 3.1: Create the shared conduct reference

**Files:**
- Create: `codex/skills/orchestra/references/shared_conduct.md`

- [ ] **Step 1: Write the file (this is the deduplicated content currently
  repeated ~4x in the profiles)**

```markdown
# Shared agent conduct

Applies to every Orchestra role. The packet is the only assignment: execute
exactly one named capability; never choose or combine capabilities, select a
model or reasoning effort, route work, spawn agents, or claim product
authority.

Output contract, in order: outcome/status first, then capability, produced
artifact file names, revision identity, blockers, material risks, and
decisions requested. Revision identity names the committed revision or
HEAD/base and, when uncommitted changes are in scope, the dirty diff state and
affected paths. Omit packet replay, process narration, praise, and unchanged
context. Never omit security, privacy, authentication, payment,
destructive/irreversible, blocker, exact-error, reviewer-finding, ambiguity,
verification, or remaining-risk information. Redact secrets, credentials,
tokens, personal data, and payment data, stating the redaction and a safe
locator.

Coordination (`coordination.py activity set`) records only material start,
final, or blocker updates and is fail-soft telemetry: on `invalid` or
`unavailable`, continue and return the complete result inline; never
retry-loop or report a workflow blocker for telemetry failure.

Stop rather than guess when the capability is missing or not singular, the
required reference or evidence is unavailable, scope is unbounded, canonical
sources conflict, or the action would cross the packet's authority.
```

- [ ] **Step 2: Commit** — via `commitbot`

### Task 3.2: Create the four role skills

**Files:**
- Create: `codex/skills/orchestra-role-analyst/SKILL.md`
- Create: `codex/skills/orchestra-role-implementer/SKILL.md`
- Create: `codex/skills/orchestra-role-reviewer/SKILL.md`
- Create: `codex/skills/orchestra-role-verifier/SKILL.md`

Content: move each profile's current `developer_instructions` body into its
role skill, restructured and deduplicated against `shared_conduct.md`. The
reviewer skill in full (the other three follow the same shape, preserving
their current Responsibility / Input / Output / Stop-conditions semantics):

- [ ] **Step 1: Write `orchestra-role-reviewer/SKILL.md`**

```markdown
---
name: orchestra-role-reviewer
description: Use when independently reviewing a bounded plan, architecture, code revision, meaningful delta, or PR feedback packet — inside an Orchestra task or as a standalone review.
---

# Orchestra Reviewer Role

Read [shared conduct](../orchestra/references/shared_conduct.md) first; it
defines the packet, output, telemetry, and stop rules for every role.

## Responsibility

Independently examine the bounded target named in the packet. First pass:
cover the complete bounded target and return all known material findings
together. Later passes: only the meaningful delta and its affected
interactions, naming the full-review base and prior finding dispositions.
Review against objective, evidence, scope, acceptance, authority boundaries,
correctness, regressions, safety, and defect-prone maintainability. Treat
complexity as a finding only when an unsupported consumer, requirement, or
reproducible risk makes it defect-prone; size or novelty alone is not a
finding. Remain read-only and report-only: findings return to the owner; never
implement them silently.

## Input

Exact review target and artifact file names, revision identity, review
authority, and stop conditions. A plan review requires the complete candidate
bundle; an implementation review requires overview, phase, implementation
report, and verification reports; a PR review treats GitHub as external truth.
Never substitute another agent's conclusion for direct inspection of source,
diff, and evidence.

## Output

Publish `plan-review`, `implementation-review`, or `pr-review` per the
artifact convention. Every actionable finding has a stable identifier,
severity, causal rationale, evidence locator, and correction rationale.
Separate non-blocking observations from actionable defects.

## Fix policy (what is worth a finding)

Fix-worthy: incorrect behavior or unmet acceptance; security/privacy/data
integrity; likely regression; unsafe error handling or concurrency; a
maintainability defect likely to cause future incorrect behavior; missing
verification for important behavior. Not fix-worthy: style covered by
formatters, speculative architecture without a concrete failure mode,
unrelated cleanup, scope expansion disguised as review, restating a rejected
suggestion.
```

- [ ] **Step 2: Write the other three role skills**

Same structure. Sources to move (not rewrite): analyst from
`codex/agents/orchestra_analyst.toml`, implementer from
`codex/agents/orchestra_implementation_worker.toml` (keep the execution-readiness checks,
Guardian paragraph replaced by a one-line reference to WORKFLOW.md, browser
route requirement, phase-teardown duties), verifier from
`codex/agents/orchestra_verifier.toml` (keep evidence discipline and
product-vs-environment failure distinction). Descriptions:

```yaml
# analyst
description: Use when gathering bounded repository evidence, researching, planning, analyzing architecture, or diagnosing a difficult failure as a read-only one-shot assignment.
# implementer
description: Use when implementing scoped code and test changes for one approved packet, including accepted review fixes within the same phase.
# verifier
description: Use when running source-read-only runtime checks, targeted tests, or browser acceptance and reporting observed evidence for one revision.
```

- [ ] **Step 3: Word-count check (skill best practice)**

Run: `wc -w codex/skills/orchestra-role-*/SKILL.md`
Expected: each body ≤ ~500 words (shared conduct holds the common weight).

- [ ] **Step 4: Commit** — via `commitbot`

### Task 3.3: Reduce the four profiles to stubs

**Files:**
- Modify: `codex/agents/orchestra_analyst.toml`,
  `codex/agents/orchestra_implementation_worker.toml`,
  `codex/agents/orchestra_reviewer.toml`, `codex/agents/orchestra_verifier.toml`

- [ ] **Step 1: Replace each `developer_instructions` with the stub (reviewer shown; others identical except the skill name)**

```toml
name = "orchestra_reviewer"
description = "Independently review one explicitly assigned bounded target."
developer_instructions = """
You perform exactly one Orchestra capability assigned by your packet. Before
acting, read your role skill at
`${CODEX_HOME:-$HOME/.codex}/skills/orchestra-role-reviewer/SKILL.md` and any
capability reference named in the packet, then execute the packet under those
contracts. If the role skill cannot be read, stop and return `blocked` with
the exact path. Do not choose capabilities, route work, or spawn agents.
"""
```

Profiles must stay behavior-only: never add `model` or
`model_reasoning_effort` (verified: profile-pinned models override spawn-time
overrides and would break matrix routing).

- [ ] **Step 2: Commit** — via `commitbot`

### Task 3.4: Register the new skills in sync and the validator

**Files:**
- Modify: `codex/scripts/sync.py` (SKILLS inventory list, manifest)
- Modify: `codex/scripts/validate_suite.py` (skill inventory checks)
- Modify: `codex/tests/test_sync.py`, `codex/tests/test_validate_suite.py`

- [ ] **Step 1: Add the four `orchestra-role-*` skill folders to sync's
  installed-skills inventory and to validate_suite's expected inventory**

- [ ] **Step 2: Update the orchestra SKILL.md routing table**

In `codex/skills/orchestra/SKILL.md`, the assignment table's "Internal
reference" column becomes "Role skill + capability reference": the packet
names the capability; behavior comes from the role skill the profile stub
already reads. Root packets no longer restate role behavior.

- [ ] **Step 3: Run validator and full suite**

Run: `python3 codex/scripts/validate_suite.py && python3 -m unittest discover -s codex/tests 2>&1 | tail -3`
Expected: `ok` + all pass.

- [ ] **Step 4: Commit** — via `commitbot`

---

## Phase 4: Orchestrator autonomy and documentation consolidation

### Task 4.1: Add the decide-by-default autonomy policy

**Files:**
- Modify: `AGENTS.md` (replace the "Orchestrator responsibility" stop-list
  framing), `codex/skills/orchestra/SKILL.md` (routing + reporting sections),
  `docs/WORKFLOW.md` ("Orchestrator behavior"), `VISION.md` ("Bounded
  autonomy" — align, keep principle-level)

- [ ] **Step 1: Insert the canonical policy text in WORKFLOW.md ("Orchestrator
  behavior") and reference it from the other files**

The shape follows the GPT-5.6 guide's compact autonomy policy: authorization
tiers stated once, safe local actions named explicitly, hard gates as one
closed list.

```markdown
## Autonomy within an approved objective

The root is the technical lead: it receives the objective, hard constraints,
and success criteria, and decides the steps itself.

For requests to answer, explain, review, diagnose, or plan: inspect the
relevant materials and report the result; implement nothing.

Within an approved objective or plan: make in-scope reversible decisions and
carry out every step named in the plan without asking again — technical
choices, tool and configuration details, file and directory locations,
dependency and environment fixes, changed-approach retries, and
non-destructive validation. A step named in the approved plan is authorized
by that approval. Never ask the user to make a technical choice the root can
make and reverse (a folder name, a port, a config location, which of two
equivalent tools); record notable choices in plan Decisions instead.

Safe local actions never need confirmation: reading files and logs, editing
in-scope code, running tests and linters, and starting or stopping local
processes the task owns.

Require user confirmation only for: irreversible loss of unique data or
work, production mutation, security or privacy policy changes, payments or
material external cost, public-contract changes, a new product choice, or
substantial scope expansion — or when the plan's intent itself has become
ambiguous.

When user participation is genuinely required — physical observation,
another device, an account or approval only the user holds — batch every
needed check into one consolidated request with expected results, instead of
sequential single questions.
```

- [ ] **Step 1b: In the same edit, delete redundant "ask first" / "stop" /
  "never" restatements from the files this policy replaces**

Per the GPT-5.6 guide, repeated approval-seeking instructions cause
unnecessary approval requests. The hard-gate list survives exactly once in
WORKFLOW.md (plus the one-line reference in AGENTS.md); scattered
restatements elsewhere are removed, not rephrased.

- [ ] **Step 2: Align the activation/brief flow with the same principle**

In `codex/skills/orchestra/SKILL.md`: merge the brief and tier
recommendation into one user interaction where possible ("Tier: … — evidence"
plus the open brief questions in the same message), and state that
post-approval progress reports are informational, not implicit permission
requests.

- [ ] **Step 3: Commit** — via `commitbot`

### Task 4.2: One canonical home per rule

**Files:**
- Modify: `docs/WORKFLOW.md` (becomes canonical for: Guardian/permissions,
  browser routing, wait windows, tier transition, teardown, artifact
  convention)
- Modify: `AGENTS.md`, `VISION.md`, `docs/ARCHITECTURE.md`,
  `codex/skills/orchestra/SKILL.md`,
  `codex/skills/orchestra/references/runtime_verification.md`,
  `codex/skills/orchestra-project-start/SKILL.md`,
  `codex/runtime/AGENTS.orchestra.md`
- Modify: `codex/scripts/validate_suite.py` + `codex/tests/test_validate_suite.py`
  (checks that assert duplicated wording)

- [ ] **Step 1: For each rule currently duplicated verbatim (Guardian
  paragraph ×9, browser_route ×8, ten-minute waits ×8, tier transition ×4),
  keep the full text only in WORKFLOW.md and replace every other occurrence
  with one reference line**

Replacement pattern:

```markdown
Permissions follow the synchronized Guardian defaults; the active choice for
the task, host, or launcher stays authoritative (see WORKFLOW.md, "Test
permissions and browser routing").
```

Exception: role skills and `runtime_verification.md` keep the one-line
operative form (an agent must not need to open WORKFLOW.md mid-task for its
own conduct), never the full restated paragraph.

- [ ] **Step 2: Slim AGENTS.md to: source-of-truth pointers, language rules,
  activation gate, autonomy policy reference, hard gates, tier summary,
  delivery summary**

Target: ≤ 150 lines. Mechanics live in WORKFLOW.md; AGENTS.md states *what*
is required and *where* the mechanism is specified.

- [ ] **Step 2b: Trim broad brevity/omission restatements**

GPT-5.6 is concise by default. Keep one output contract in
`shared_conduct.md` (it encodes a product requirement: outcome-first,
evidence preserved, secrets redacted); remove generic "be concise" / "omit
narration" / "no praise" repetitions everywhere else. Keep any instruction
that corrects a measured gap; drop the rest.

- [ ] **Step 3: Update validate_suite checks that pinned the duplicated
  wording; keep structural checks (files exist, matrices complete, statuses
  closed-set)**

- [ ] **Step 4: Run validator + full suite, then commit** — via `commitbot`

Run: `python3 codex/scripts/validate_suite.py && python3 -m unittest discover -s codex/tests 2>&1 | tail -3`

---

## Phase 5: Model configuration and spawn-context hardening

### Task 5.1: Generate the dual matrix at sync time

**Files:**
- Modify: `codex/scripts/sync.py`
- Delete: `codex/config/roles.dual.toml`
- Modify: `codex/tests/test_sync.py`, `codex/scripts/validate_suite.py`

- [ ] **Step 1: Add a composing function to sync.py and use it when
  `--modelconfig dual` is selected**

```python
def _compose_dual_matrix(native_text: str, external_text: str) -> str:
    """Compose the installed dual matrix from the two source matrices.

    Wraps each source's top-level `tiers` tables under
    `modes.native.tiers` / `modes.external.tiers` by textual section rewrite,
    preserving entry order and comments.
    """
    def _wrap(text: str, mode: str) -> str:
        return text.replace("[tiers.", f"[modes.{mode}.tiers.")
    return _wrap(native_text, "native") + "\n" + _wrap(external_text, "external")
```

The installed artifact at `$CODEX_HOME/orchestra/roles.toml` is byte-stable
for a given pair of sources; add a test that composes the current sources and
asserts equality with the previously installed dual content (guards against
regressions during the switch).

- [ ] **Step 2: Delete `codex/config/roles.dual.toml`; update sync inventory,
  manifest expectations, validator, and tests**

Note: the external source already uses `orchestra-v1/` aliases for native
models, so composition is purely structural — verify with the equality test,
not by hand.

- [ ] **Step 3: Run validator + full suite, then commit** — via `commitbot`

### Task 5.2: Explicit clean spawn context (`fork_turns: none`)

**Files:**
- Modify: `codex/skills/orchestra/SKILL.md` ("Route standard and critical
  work" intro), `docs/WORKFLOW.md` ("Orchestrator behavior")

- [ ] **Step 1: Add the canonical instruction (WORKFLOW.md) and a one-line
  operative form in SKILL.md**

```markdown
Every Orchestra dispatch starts from a clean context: the packet and named
artifacts carry the assignment. Under multi-agent V2, pass `fork_turns: none`
explicitly on every spawn (the V2 default forks the full root history, which
multiplies token cost and destroys reviewer independence). Under V1, never
set `fork_context: true` for an Orchestra dispatch.
```

- [ ] **Step 2: Record the verified alias pitfalls as an operational note**

Append to `docs/ARCHITECTURE.md` "Model and reasoning configuration" (3
lines): alias catalog metadata must stay synchronized with native metadata
(the context-window entry controls compaction), `ultra` effort is not used on
V1 aliases, and encrypted compaction blobs are not portable across
alias/native routes.

- [ ] **Step 3: Run validator, then commit** — via `commitbot`

---

## Phase 6: Final verification and canary

### Task 6.1: Full verification

- [ ] **Step 1: Run everything**

Run: `python3 codex/scripts/validate_suite.py && python3 -m unittest discover -s codex/tests 2>&1 | tail -3`
Expected: `ok` + all pass.

- [ ] **Step 2: Sync to the live Codex home and run a smoke canary**

Run: `python3 codex/scripts/sync.py install --modelconfig dual` (or the
repo's documented sync invocation; confirm exact flags from `sync.py --help`
before running).
Then a read-only canary: spawn one `orchestra_reviewer`-profiled agent with a
trivial bounded review packet and confirm it (a) reads its role skill from
`$CODEX_HOME/skills/orchestra-role-reviewer/SKILL.md` without an escalation
prompt, and (b) returns the outcome-first output contract.

- [ ] **Step 3: Commit any canary-driven fixes** — via `commitbot`

### Task 6.2: Self-review against the goals

- [ ] Confirm: every rule has exactly one canonical home (spot-check Guardian,
  browser_route, waits with `rg -c`); role skills ≤ ~500 words each; profiles
  contain no behavior beyond the stub; `AGENTS.md` ≤ 150 lines; coordination
  has two tables; no test asserts full error sentences; `roles.dual.toml`
  gone from source but byte-identical when composed.

---

## Design decisions locked by this plan

1. **Role skills are the single source of agent behavior.** Profiles are
   stubs; packets carry assignment, authority, and pointers — never behavior.
2. **Profiles never pin models** (Codex: profile model overrides spawn
   overrides; would break matrix routing).
3. **The session gate and the native/external dual concept stay** (real V1/V2
   protocol constraint, verified against Codex 0.146 source).
4. **Autonomy is decide-by-default within an approved objective**; hard gates
   are unchanged and explicit; user interactions are batched.
5. **The filesystem is the artifact store**; SQLite keeps only what the hub
   renders (tasks, activities).
6. **Hub client work is deferred**, documented separately.
7. **Base role skills are model-agnostic.** GPT-5.6 prompting guidance is
   applied only where it is model-neutral (leaner prompts, compact autonomy
   policy, intent-based instructions). Per-model prompt adaptations — e.g.
   for the native tier's Sol/Terra or the external tier's Grok/GLM/Composer
   assignments — are a deferred overlay mechanism documented in
   `docs/plans/2026-08-03-model-specific-prompt-overlays.md`; they must never
   fork the canonical role behavior.
