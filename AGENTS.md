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
routing, compact synthesis, blocker resolution, the advisory Graphify
lifecycle, and final technical judgment. It may make reversible in-scope
technical decisions needed to complete an approved objective.

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

- Orchestra has four base profiles: `analyst`, `implementation_worker`,
  `reviewer`, and `verifier`.
- The root composes each dispatch with a capability and the exact tier
  assignment in `docs/WORKFLOW.md`; profiles do not select their own model.
- Light: general implementation, independent review, and runtime verification.
- Standard: bounded analysis and root-owned planning, implementation, one
  high-signal independent review, and verification.
- Critical: standard flow plus plan audit or a second independent review only
  for a named measurable risk and detectable defect class.
- Use a detailed phase subplan only when the phase itself is complex.
- Accepted findings return to the same implementation owner.
- Reviewers report; they do not silently implement their own findings.

Frontend implementation composes `implementation_worker`; browser acceptance
composes `verifier`. They remain independent, and either capability makes a task
at least standard. No Orchestra assignment uses Sol xhigh. The user selects the
root's Sol medium or Sol high session outside Orchestra.

Fix correctness, security, regression, acceptance, and defect-prone
maintainability findings. Record or reject cosmetic, speculative, or
out-of-scope suggestions without entering a review loop.

## Execution and commits

- Use the fewest independently reviewable phases.
- For standard and critical work, the root owns one unversioned local plan at
  `git rev-parse --git-path orchestra/plan.md`; Git is authoritative on resume.
- Plan approval authorizes implementation and automatic commits at successfully
  reviewed phase boundaries unless the user limits that authority.
- For light work without a formal plan, the user's explicit implementation
  request authorizes the reviewed task commit unless the user limits it.
- The root commits each reviewed phase directly or through the narrow commit
  helper; commit execution is not an agent profile.
- Do not create commit journals, replace the Git index, hash the whole worktree,
  or revalidate unchanged authority repeatedly.
- Preserve unrelated and uncommitted user work.

## Graphify lifecycle

- Graphify is advisory, non-blocking, and default-on only for standard and
  critical planned repositories. Light never auto-adopts it.
- Before planning, check Graphify configuration read-only: command available;
  exactly `graph.json`, `graph.html`, and `GRAPH_REPORT.md` tracked under
  `graphify-out/`; `manifest.json`, `cost.json`, and all other generated paths
  ignored. Before hook status, canonicalize `git rev-parse --git-dir` and
  `git rev-parse --git-common-dir`. If they differ, this linked worktree is
  hook automation is `partial`: preserve common hooks and do not run status,
  install, reinstall, or uninstall hooks, add a wrapper or alternate hook, or
  bootstrap solely for hooks. When the command exists, continue with relevant
  Git delta, pending evidence, and query smoke; a graph proven fresh at HEAD
  remains usable and is reported usable to `repository_context`, otherwise use
  source. When the command is missing, add the bootstrap and use source because
  query cannot run. Artifact configuration may still authorize that bootstrap,
  with its hook step skipped. Only an eligible non-linked worktree with the command
  available executes `graphify hook status` exactly once per detection pass:
  valid installed status continues; valid absence adds bootstrap only when
  safely repairable; failure or uninterpretable output is `partial` source
  fallback without bootstrap.
- After hook configuration passes, check the relevant Git delta and pending
  evidence before query smoke/use; do not call hook status again. Stale or
  pending evidence or execution failure is `partial` source fallback, never
  repeated bootstrap. Persist none of these labels.
- Read-only detection and query may run before approval. Do not install, build,
  edit ignore rules, install hooks, or mutate Git before plan approval.
- Approval authorizes one complete initial build, repository ignore/versioning
  changes, `uv tool install --upgrade graphifyy`, and `graphify hook install`.
  External API credentials or material cost require separate user authority.
  Never run `graphify codex install`.
- Review, verify, and commit the initial bootstrap snapshot before running
  `graphify hook install`; then rerun active detection. This avoids a redundant
  post-commit rebuild of the initial snapshot.
- Before hook installation, resolve Git's actual hooks destination including
  `core.hooksPath`, after proving the worktree is non-linked. A linked worktree
  preserves existing hooks, records hook automation as `partial`, and skips
  installation; its graph-use decision still follows freshness checks. Use
  source when a non-linked destination is inside the tracked worktree or
  installation would modify a tracked hook. Add no wrapper or alternate hook
  mechanism.
- Native hooks structurally refresh after commits only in eligible non-linked
  worktrees. Before later phase context, linked worktrees continue past skipped
  hook operations to freshness and query checks; stale or pending evidence and
  failed hook/query execution fall back to source without bootstrap.
- After functional phases and before plan completion, run semantic
  `graphify . --update` at most once. Commit changed tracked outputs in one
  separate graph-only commit; return `nothing_to_commit` when unchanged.
- Treat every Graphify failure as `partial`. Source, Git, project tests, runtime
  evidence, and independent review remain authoritative and functional work
  continues.
- Treat hooks as clone-local and unversioned only after the resolved destination
  proves it. Reinstall safely after cloning or hook removal and use
  `graphify hook uninstall` for deliberate safe cleanup. The root owns the
  lifecycle directly; add no profile, capability, helper, playbook, wrapper,
  schema, lock, transaction, state machine, or policy gate.

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

The delegated `verifier` with `browser_acceptance` uses Computer Use with Chrome
as its exclusive browser path. It must never invoke, probe, or fall back to
Codex's in-app Browser. It opens a new Chrome tab, preserves unrelated tabs and
sessions, and reports observed behavior with reproducible steps and evidence.
It returns blocked when Computer Use or Chrome is unavailable. The root may use
the in-app Browser separately.

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
simplify it. Graphify may provide context, but it is not correctness or policy
evidence.
