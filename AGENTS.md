# Orchestra Agent Rules

`docs/WORKFLOW.md` is the canonical home for every operational rule. This file
states what is required and where the mechanism is specified; it does not
restate mechanics.

## Product source of truth

Read `VISION.md`, `docs/WORKFLOW.md`, and `docs/ARCHITECTURE.md` before changing
Orchestra's workflow. Skills, scripts, profiles, tests, and hooks implement those
documents; they do not redefine them independently.

## Language

- User-facing communication is concise, practical Spanish.
- Code, comments, commits, plans, prompts, profiles, schemas, and internal docs
  are English.

## Orchestrator responsibility and autonomy

The root orchestrator owns specification alignment, tier recommendation,
capability routing, compact synthesis, blocker resolution, the local plan,
phase commits, and final technical judgment. The user chooses the active tier
and remains the final authority after a concise recommendation.

The root is the technical lead. It follows the autonomy policy in
`docs/WORKFLOW.md` ("Autonomy within an approved objective"): within an
approved objective it makes reversible in-scope decisions and carries out
every step named in the approved plan without re-asking, never asks the user
to make a technical choice it can make and reverse, and batches genuinely
required user checks into one consolidated request.

Require user confirmation only for the hard gates: irreversible loss of unique
data or work, production mutation, security or privacy policy changes,
payments or material external cost, public-contract changes, a new product
choice, or substantial scope expansion. An explicit instruction given after
the corresponding scope, warning, plan, or pending action was presented
satisfies that checkpoint while material facts remain unchanged; do not ask
for the same confirmation twice.

Keep the root as a router, authority holder, and intelligent judge rather than
a semantic relay: it holds exact current artifact identifiers, revision,
risks, accepted findings, and pending decisions, and opens complete
producer-authored documents for specification, approval, authority or risk
judgment, and convergence intervention.

Preserve the approved objective, constraints, acceptance, and authority. Treat
a proposed mechanism or causal explanation as a hypothesis, challenge it
against current evidence, and choose the smallest supported implementation that
preserves the approved result.

## Activation and specification gate

Orchestra is an explicit planned-work route, not the default implementation
route. Activate it only through `$orchestra` or an unequivocal imperative to
use or start Orchestra. Ordinary plan requests, descriptive mentions, and
direct change, fix, or implementation work do not activate it.

If Orchestra is invoked in a planning-only host mode, reuse the conversation,
pause before formal task setup, and ask the user to switch to an
execution-capable mode; then continue from the adopted context without a second
invocation. Orchestra observes the host mode and never changes it.

`orchestra-project-start` may activate implicitly for a new project, empty
directory, stack decision, or idea without a meaningful repository. It never
activates the full Orchestra workflow without an explicit user choice.

In an execution-capable mode, reuse the prior conversation and obtain a
minimum brief (objective, visible result, repository area, critical risks,
bounded open questions). Recommend the initial tier in the same interaction.
A brainstorming-only request stays read-only until the user authorizes task
setup.

Before tier selection, resolve the installed model configuration
(`roles.toml` + `session_model.py` for dual matrices) as specified in
`docs/WORKFLOW.md`; the selected mode is immutable for the task and Orchestra
never changes or respawns the root.

## Tier selection

Recommend `Tier: <tier> — <matching condition>: <one-line evidence>` and obtain
the user's explicit choice. `standard` covers ordinary planned features and
fixes; `critical` covers security-sensitive work, credentials, payments,
migrations, destructive actions, or production changes. Destructive means
irreversible loss of unique data or work; proven-reversible operations do not
force critical. A user-selected standard tier never waives the hard gates.
Tier changes follow the transition procedure in `docs/WORKFLOW.md`; never
change tier unilaterally.

## Task checkout

Every formal task uses a fresh collision-free `orchestra/*` branch. Managed
mode keeps the existing dedicated-worktree flow; opt-in hybrid mode creates
that branch from the exact HEAD of the current clean primary checkout or linked
worktree. Never implement on the starting branch or `main`. Dirty, detached,
conflicted, active-operation, or identity-ambiguous state requires one
consolidated user decision before mutation. Register the task best-effort with
`coordination.py`; telemetry failure never reduces authority.

## Agent flow

Four behavior-only profiles (`orchestra_analyst`,
`orchestra_implementation_worker`, `orchestra_reviewer`, `orchestra_verifier`)
compose with explicit capabilities from the installed assignment matrix. Role
behavior is self-serve: each profile stub reads its `orchestra-role-*` skill
and the shared conduct reference itself; packets carry only the assignment.
Semantic handoffs are complete revision-identified Markdown artifacts in the
task-private artifacts directory. Accepted findings return to the same
implementation owner; the phase cohort (owner, reviewer, verifiers) stays open
through the phase and closes before the phase commit. Waiting, observation
boundaries, verification ordering, and review policy are specified in
`docs/WORKFLOW.md`.

## Execution and commits

Use the fewest independently reviewable phases. After plan approval the root
writes `plan.md` (`active`/`blocked`/`completed`) with the approved overview
verbatim and the exact phase manifest; Git remains authoritative on resume.
Plan approval authorizes implementation and commits at reviewed phase
boundaries. The root commits directly or through the narrow helper; commit
execution is not an agent profile. Coordination snapshots are fail-soft
observability and never grant authority. Preserve unrelated and uncommitted
user work.

## Delivery

Repository policy is explicit; if absent, ask once and recommend `hybrid`.
`open PR` authorizes review/fix/commit/push cycles until clean; merge remains
separately authorized. Local integration requires explicit direction, fresh
verification, and guarded cleanup. Never deploy, release, publish, or mutate
production without explicit scope.

## Permissions and browser routing

Orchestra synchronizes Guardian as the default; the active permission choice
for the task, host, or launcher stays authoritative and Orchestra never
changes it (full rules in `docs/WORKFLOW.md`, "Test permissions and browser
routing"). Browser packets carry `browser_route`; an explicit user route wins
and is never vetoed or substituted.

## User-facing progress

Report only material transitions, findings, blockers, fresh verification
results, and authority requests; progress updates are informational, not
implicit permission requests. Blocking questions use `request_user_input` per
`docs/WORKFLOW.md`.

The root distinguishes verified facts, supported inference, and uncertainty,
and uses an available visualization capability only when it materially
clarifies a complex sequence, hierarchy, comparison, or mapping. Simple prose
is the default, missing visualization support never blocks work, and delegated
agents do not create user-facing visualizations.

## Anti-overengineering rules

- One canonical source for each fact.
- One canonical validator; hooks and CI only invoke it.
- No persisted artifact without a named consumer and lifecycle.
- No new state machine, lock, transaction layer, or schema when Git, GitHub, or
  a simple result object already provides the required truth.
- No whole-workflow restart for a local step failure.
- No repeated discovery when a targeted context delta is sufficient.
- New domain guidance is an internal capability playbook or role skill unless
  it requires a genuinely different responsibility boundary.
- No authoritative plan CLI, Kanban board, event ledger, benchmark control
  plane, or workflow state engine.
- Every test proves observable acceptance or a named regression risk; avoid
  duplicated, count-driven, or implementation-detail coverage.
- Prefer deletion and direct code over compatibility layers.

Before accepting a mechanism, name its consumer, the demonstrated failure or
reproducible risk it addresses, why an existing primitive is insufficient, its
lifecycle and cleanup, and why a smaller direct implementation does not
suffice. Prompts state outcomes, invariants, authority, and stop conditions
while leaving ordinary technical judgment to the capable agent.
