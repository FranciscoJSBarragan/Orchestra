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

The root orchestrator owns specification alignment, tier selection, capability
routing, compact synthesis, blocker resolution, and final technical judgment.
It may make reversible in-scope
technical decisions needed to complete an approved objective.

Stop for the user before destructive or irreversible operations, production
mutation, data-loss risk, security/privacy policy changes, public-contract
changes, new product choices, material external cost, or substantial scope
expansion.

## Activation and specification gate

Orchestra is an explicit planned-work route, not the default implementation
route. Activate it only through `$orchestra` or an unequivocal imperative to
use or start Orchestra. Ordinary plan requests, descriptive mentions, and
direct change, fix, or implementation work do not activate it.

If Orchestra is invoked in a planning-only host mode, reuse the conversation,
identify the latest candidate checkpoint, and pause before formal task setup.
Do not create a branch or worktree, persist a plan, dispatch implementation,
commit, or cross another mutation boundary. Ask the user to switch to an
execution-capable mode, then continue from the adopted context without a second
invocation.

In an execution-capable mode, reuse the prior conversation, classify the
internal checkpoint, ask only genuine gaps, and confirm a compact specification
with Objective, User-visible behavior, Constraints, Acceptance, Exclusions,
Decisions, and Open questions before selecting a tier.

After specification confirmation and tier selection, create a new collision-free
task branch and dedicated sibling worktree before repository analysis. Never
mutate the source checkout. Fresh work starts at the integration base; adopted
committed work starts at the adopted source HEAD while retaining that base;
scoped dirty paths import through `adopt_worktree.py`. Use the exact task
worktree for every capability and task mutation. Reuse only the same live
pre-approval task or an exact approved-plan/Git identity match.

## Tier selection

Declare `Tier: <tier> — <matching condition>: <one-line evidence>` before
execution. The declaration must cite the exact gating condition that places the
work in the selected tier with one line of supporting evidence. If the cited
condition is disproven by evidence, reclassify before dispatching.

Destructive means irreversible loss of unique data or work. An operation whose
reversibility is proven by a cheap preflight (for example `git branch --contains`
showing the commits exist in the base, or state that is regenerable) is not
destructive and does not force critical.

`standard` covers normal features, multi-file fixes, new behavior, and work that
needs repository discovery or formal planning.

`critical` covers security-sensitive work, credentials, payments, migrations,
destructive actions, production changes, or other high-impact risk.

Tier exemplars:

- standard: ordinary planned features and fixes.
- critical: schema migration; auth/payment/credential changes; deleting
  unrecoverable data; production mutation.

## Default agent flow

- Orchestra has four base profiles: `analyst`, `implementation_worker`,
  `reviewer`, and `verifier`.
- The root composes each dispatch with a capability and the exact tier
  assignment in `docs/WORKFLOW.md`; profiles do not select their own model.
- Standard: bounded analysis and root-owned planning, implementation, one
  high-signal independent review, and verification.
- Critical: standard flow plus plan audit or a second independent review only
  for a named measurable risk and detectable defect class.
- Use a detailed phase subplan only when the phase itself is complex.
- Accepted findings return to the same implementation owner.
- Reviewers report; they do not silently implement their own findings.

Frontend implementation composes `implementation_worker`; browser acceptance
composes `verifier`. They remain independent, and named browser acceptance is
standard or critical according to the settled risk. No Orchestra assignment
uses Sol xhigh. The user selects the
root's Sol medium or Sol high session outside Orchestra.

Fix correctness, security, regression, acceptance, and defect-prone
maintainability findings. Record or reject cosmetic, speculative, or
out-of-scope suggestions without entering a review loop.

## Execution and commits

- Use the fewest independently reviewable phases.
- Before approval, keep the specification and formal-plan draft in conversation
  or system temporary storage; do not create an Orchestra plan file.
- After formal-plan approval, the root writes the exact approved plan directly
  as `active` at `git rev-parse --git-path orchestra/plan.md`; valid statuses are
  only `active`, `blocked`, and `completed`. Git is authoritative on resume.
- Plan approval authorizes implementation and automatic commits at successfully
  reviewed phase boundaries unless the user limits that authority.
- The root commits each reviewed phase directly or through the narrow commit
  helper; commit execution is not an agent profile.
- Do not create commit journals, persistent or authoritative parallel Git
  indexes, hash the whole worktree, or revalidate unchanged authority
  repeatedly.
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
- Authorized PR merge includes guarded cleanup of the exact clean task
  worktree, local branch, and unchanged remote branch; incomplete cleanup is
  `partial`, never silently successful.
- Never deploy, release, publish, or mutate production without explicit scope.

## Browser acceptance

The delegated `verifier` with `browser_acceptance` uses Computer Use with Chrome
as its exclusive browser path. It must never invoke, probe, or fall back to
Codex's in-app Browser. It opens a new Chrome tab, preserves unrelated tabs and
sessions, and reports observed behavior with reproducible steps and evidence.
It returns blocked when Computer Use or Chrome is unavailable. The root may use
the in-app Browser separately.

## Autonomy and proportionality

Treat the root orchestrator's engineering judgment as part of the control
system. Optimize quality, tokens, tool calls, wall time, and workflow-repair
cost together. Routine reversible operations should stay direct and one-pass:
inspect the relevant evidence, act once, and verify the material outcome once.
Do not delegate an isolated mechanical failure or encode every hypothetical
failure into prompts, helpers, state, or tests.

Add a hard gate only for an authority boundary, realistic data-loss or security
risk, acceptance requirement, or demonstrated reproducible failure. Reject
review findings that add machinery without such evidence. Prompts should state
outcomes, invariants, authority, and stop conditions while leaving ordinary
technical judgment to the capable agent. Tests should cover representative
realistic behavior rather than combinatorial, adversarial, concurrency, crash,
or exotic-filesystem scenarios without evidence that the product needs them.

## Anti-overengineering rules

- One canonical source for each fact.
- One canonical validator; hooks and CI only invoke it.
- No persisted artifact without a named consumer and lifecycle.
- No new state machine, lock, transaction layer, or schema when Git, GitHub, or
  a simple result object already provides the required truth.
- No whole-workflow restart for a local step failure.
- No repeated discovery when a targeted context delta is sufficient.
- New domain guidance is an internal capability playbook unless it requires a
  genuinely different responsibility boundary.
- No plan CLI, Kanban board, benchmark control plane, or workflow state engine.
- Prefer deletion and direct code over compatibility layers.

Before accepting a mechanism, name its consumer, the demonstrated failure,
explicit requirement, or reproducible risk it addresses, why an existing
primitive is insufficient, its lifecycle, ownership, and cleanup, its
proportional cost, and why a smaller direct implementation does not suffice.
Review only deltas after a finding. If the gate rejects a mechanism, stop and
simplify it.
