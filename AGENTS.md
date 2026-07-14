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
  one phase implementation owner, one high-signal `reviewer`, and verification.
- Critical: standard flow plus plan audit and a second independent review where
  the risk justifies it.
- Use a detailed phase subplan only when the phase itself is complex.
- Accepted findings return to the same implementation owner.
- Reviewers report; they do not silently implement their own findings.

For each standard or critical phase, use `frontend_implementation_worker`
instead of `implementation_worker` when the phase is primarily frontend. Never
dispatch both for the same phase or in parallel collaboration. Split mixed work
into frontend and non-frontend phases with one implementation owner each. Light
work continues to use `implementation_worker`.

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

The delegated `browser_acceptance_tester` uses Computer Use with Chrome as its
exclusive browser path. It must never invoke, probe, or fall back to Codex's
in-app Browser. It opens a new Chrome tab, preserves unrelated tabs and sessions,
and reports observed behavior with reproducible steps and evidence. It returns
blocked when Computer Use or Chrome is unavailable. The root may use the in-app
Browser separately.

## Anti-overengineering rules

- One canonical source for each fact.
- One canonical validator; hooks and CI only invoke it.
- No persisted artifact without a named consumer and lifecycle.
- No new state machine, lock, transaction layer, or schema when Git, GitHub, or
  a simple result object already provides the required truth.
- No whole-workflow restart for a local step failure.
- No repeated discovery when a targeted context delta is sufficient.
- No new specialist profile without a distinct recurring responsibility.
- Twelve specialist profiles are a maximum, not a growth target.
- Prefer deletion and direct code over compatibility layers.

Before accepting a mechanism, name its consumer, the demonstrated failure,
explicit requirement, or reproducible risk it addresses, why an existing
primitive is insufficient, its lifecycle, ownership, and cleanup, its
proportional cost, and why a smaller direct implementation does not suffice.
Review only deltas after a finding. If the gate rejects a mechanism, stop and
simplify it. Graphify may provide context, but it is not correctness or policy
evidence.
