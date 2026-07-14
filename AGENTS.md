# Orchestra Agent Rules

## Product source of truth

Read `VISION.md`, `docs/WORKFLOW.md`, and `docs/ARCHITECTURE.md` before changing
Orchestra's workflow. Skills, scripts, profiles, tests, and hooks implement those
documents; they do not redefine them independently.

## Language

- User-facing communication is concise, practical Spanish.
- Code, comments, commits, plans, prompts, profiles, schemas, and internal docs
  are English.

## Orchestrator responsibility

The root orchestrator owns problem framing, tier selection, user alignment,
routing, compact synthesis, blocker resolution, and final technical judgment.
It may make reversible in-scope technical decisions needed to complete an
approved objective.

Stop for the user before destructive or irreversible operations, production
mutation, data-loss risk, security/privacy policy changes, public-contract
changes, new product choices, material external cost, or substantial scope
expansion.

## Tier selection

Declare `Tier: light|standard|critical — reason` before execution.

`light` is allowed only when every condition holds:

- one small, fully understood objective;
- localized impact following an established pattern;
- no public API, schema, CLI, persisted-format, dependency, or architecture
  change;
- no auth, security, privacy, payment, migration, production, deployment, or
  destructive risk;
- no unresolved product decision;
- a direct targeted verification exists.

Any doubt makes the task `standard`. Escalate immediately when new coupling,
risk, or scope appears.

`standard` covers normal features, multi-file fixes, new behavior, and work that
needs repository discovery or formal planning.

`critical` covers security-sensitive work, credentials, payments, migrations,
destructive actions, production changes, or other high-impact risk.

## Default agent flow

- Light: `implementation_worker` then independent `reviewer`.
- Standard: bounded `repo_context_explorer`, `planner`,
  `implementation_worker`, one high-signal `reviewer`, and verification.
- Critical: standard flow plus plan audit and a second independent review where
  the risk justifies it.
- Use a detailed phase subplan only when the phase itself is complex.
- Accepted findings return to the same implementation owner.
- Reviewers report; they do not silently implement their own findings.

Fix correctness, security, regression, acceptance, and defect-prone
maintainability findings. Record or reject cosmetic, speculative, or
out-of-scope suggestions without entering a review loop.

## Execution and commits

- Use the fewest independently reviewable phases.
- Plan approval authorizes implementation and automatic commits at successfully
  reviewed phase boundaries unless the user limits that authority.
- For light work without a formal plan, the user's explicit implementation
  request authorizes the reviewed task commit unless the user limits it.
- A lean `phase_committer` stages only the phase scope, creates a structured
  file-based commit message, executes Git commit, verifies the stored commit,
  and returns a compact result.
- Do not create commit journals, replace the Git index, hash the whole worktree,
  or revalidate unchanged authority repeatedly.
- Preserve unrelated and uncommitted user work.

## Delivery

- Repository policy is explicit. If absent, ask the user once and recommend
  `hybrid`; do not infer authorization from CI or repository history.
- `open PR` authorizes PR creation plus review/fix/commit/push cycles until the
  PR is clean.
- Merge remains separately authorized unless the user already said to merge
  when clean.
- Local integration requires explicit user direction, fresh verification,
  clean integration, and branch/worktree cleanup.
- Never deploy, release, publish, or mutate production without explicit scope.

## Browser acceptance

The delegated `browser_acceptance_tester` must not use Codex's in-app Browser;
it is not reliable from subagents. It must use Computer Use to operate Chrome,
open a new tab for the test, preserve unrelated tabs, and report observed
behavior with reproducible steps and evidence.

## Anti-overengineering rules

- One canonical source for each fact.
- One canonical validator; hooks and CI only invoke it.
- No persisted artifact without a named consumer and lifecycle.
- No new state machine, lock, transaction layer, or schema when Git, GitHub, or
  a simple result object already provides the required truth.
- No whole-workflow restart for a local step failure.
- No repeated discovery when a targeted context delta is sufficient.
- No new specialist profile without a distinct recurring responsibility.
- Eleven specialist profiles are a maximum, not a growth target.
- Prefer deletion and direct code over compatibility layers.

Before accepting a mechanism, name its consumer, the demonstrated failure,
explicit requirement, or reproducible risk it addresses, why an existing
primitive is insufficient, its lifecycle, ownership, and cleanup, its
proportional cost, and why a smaller direct implementation does not suffice.
Review only deltas after a finding. If the gate rejects a mechanism, stop and
simplify it. Graphify may provide context, but it is not correctness or policy
evidence.
