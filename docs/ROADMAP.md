# Orchestra Roadmap

## Status

This roadmap is non-canonical. It does not override `VISION.md`,
`docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, or `AGENTS.md`.

The native workflow packages from canonical sources into relocatable bundles.
Shared engineering guidance now supports conditional design, regression,
state, performance, and verification practices through the existing roles.
Conformance and package checks establish integration, not improved generated
code quality. Plugin installation is an alternative to direct sync; it does
not create a second runtime.

### Engineering baseline before the Tasks split

Implementation through `f47b08bf49ce98ed632de8a47195f45d639c44c9` includes
decision evidence and Lite v2 handoffs, useful verification, decision authority,
conversation continuity, reproducible source preparation, and the authorization
pilot corrections. The latest correction received an accepted independent Opus
5.5 medium review and passed full conformance (17 checks).

On 2026-09-25, the owner's active Codex, Cursor, Grok and Devin plugin
installations were updated to that implementation baseline. Installed content
was compared with the generated bundles (94, 96, 94 and 100 files respectively),
and user configuration was preserved. This completed personal installation
update is distinct from broader host adoption, public distribution and proof
of agent behavior. Git branch refs and commit history record source integration;
an installed candidate alone does not establish delivery to `main`.

The new held-out authority/continuity case, including intermediate questions
and resumption, is deferred at the owner's request on 2026-09-26. No new live
evaluation is part of this documentation and integration closure. Matched
quality/model evaluation also remains pending; the recorded pilot is a bounded
observation. No release or public marketplace publication is claimed.

### Tasks separation

The source split kept engineering skills, full execution, delegation,
initiative coordination and local plan/Git helpers in Orchestra. The separate
Orchestra Tasks repository owns cards, global snapshots, MCP, identity hooks and
Hub clients. Direct tracking is explicit opt-in. Each has its own package and
installer; core-only use has no Tasks dependency.

The [separation acceptance record](evaluation/TASKS_SPLIT_ACCEPTANCE.md) records
the independent Opus 5.5 Medium review, source and package checks, publication
to both repositories' `main` branches, and the owner's authorized plugin
replacement on 2026-09-26. Both repositories are public; public marketplace
publication remains separate. Installed package parity and bounded runtime
checks passed. The prior model-driven host trials below describe the combined
baseline, not live workflow acceptance of this split.
The held-out model-quality evaluation remains deferred.

## Distribution

Local plugin packaging is supported. Public marketplace publication remains a
separate explicit delivery decision after host acceptance and real-project
workflow evidence. This roadmap does not prescribe an implementation design.

Bridge integration is deferred. Native adapters and CLI delegation remain in
Orchestra. Task Control and Hub belong to the separate Orchestra Tasks companion.

## Plugin adoption evidence

The engineering guidance and native/plugin source changes received independent
review. Clean isolated Codex, Cursor, and Grok CLI installations completed a
bounded task through planning, process restart/resume, native implementation,
independent verification and review, phase commit, and agent cleanup.
[Packaging documentation](../packaging/README.md) records host versions,
actual dispatch, lifecycle caveats, delivery coverage, and a repeatable recipe.

The sync-to-plugin migration rehearsal preserved unrelated configuration,
task data, and worktrees without duplicate direct-sync skills. Codex cached
updates and removal were checked; Grok's stale local update required explicit
remove/install. Cursor used a session-local bundle. The `Plugin bundles` CI
workflow validates canonical sources and produces versioned downloadable
candidates and checksums, without creating a release or marketplace entry.

The remaining adoption work is broader real-project evidence, including
managed worktrees and remote PR delivery through installed plugins. The owner's
completed plugin update is recorded in the delivery snapshot above; migration
of other installations and public publication remain separate delivery decisions.

Task Control and Hub remain optional. Additional harnesses and comparative model
benchmarks follow these adoption checks. This list records follow-up work; it
does not itself authorize publication or a change to the active installation.

## Deferred quality and model evaluation

After the bounded plugin acceptance above, compare the baseline and revised
engineering guidance on matched tasks, models, reasoning effort, budgets, and
environments. Include regression fixes, contract changes with indirect
consumers, stateful recovery, and a user journey. Use repeated paired runs and
independent assessment of executable acceptance and resulting changes;
correctness and regressions precede maintainability, latency, and token cost.
Keep this a bounded evaluation, separate from changes to model assignments.
No quality improvement is established by conformance checks alone.

The approved capability matrix is the initial runtime contract. A comparative
benchmark is deferred until the four profiles, capability playbooks, local plan
resume flow, and conformance suite work end to end. Bootstrap and installation
work must not invoke Orchestra to evaluate Orchestra.

After that boundary, representative canary tasks may compare the approved model
assignments using correctness, defects found by independent review, verification
reliability, latency, and token use. The benchmark informs a later explicit
product decision; it does not silently rewrite assignments, add a benchmarking
profile, persist workflow telemetry, or require a benchmark control plane.

### Candidates from gentle-ai awaiting a measured case

Reviewed on 2026-10-15 against gentle-ai `4acaf42`, whose project reports
measuring both in its own bench. Neither is adopted until an Orchestra
evaluation shows a gain:

- **Differential check.** Before handoff, the implementer runs existing
  commands or endpoints that share the changed code with the new input against
  a scratch copy of the base revision and against the change; an unrequested
  difference is a regression to fix and pin with a test. It needs an
  evaluation case with a known regression of existing behavior that review
  missed; none is recorded yet.
- **Risk-gated review pair.** Run the review pair only when the change touches
  a named high-risk item (stored data or irreversible effects, security,
  consumed contracts, concurrency, delivery or environment, or no test that
  would catch a regression) and one reviewer otherwise. Every recorded pair
  gain came from such tasks; single-reviewer recall on ordinary changes is
  unmeasured.

### Rejected ideas

Reviewed and not adopted, with the reason, so a later review starts from this
evidence instead of reopening the question. Evidence that removes the reason
reopens the idea.

From gentle-ai `4acaf42` and pstack `99743e9`, reviewed on 2026-10-15:

- **Comment-removal agent** (pstack `/no-comments`): Orchestra-produced
  NeniTPV merges since 2026-10-05, about 3,000 added lines, contained no
  explanatory comments or suppressions; the source-comment policy holds
  without another agent.
- **Inline work by default** (gentle): the root is the expensive model in the
  hybrid design, and delegating volume to cheaper models is the point.
- **Reviewer-side severity floor or narrowed counterexamples**: the root's
  triage already owns the floor, and adding reviewer instructions lowered
  cheap-model recall in Orchestra evaluations while cutting them raised it.
- **Fixed diff-size reference in plans** (about 400 lines): it invites
  compressed code or dropped tests to meet the number, and the owner rejected
  it as complicating the plan.
- **RDD runtime** (gentle): a binary with transactions and authority lineage,
  enabled by default, that supports two of Orchestra's five hosts. Its useful
  rules (risk-based review, one correction, blocking only on serious findings
  caused by the change) already live in root triage.
- **Engram memory** (gentle): agent-written memory behind MCP whose tracker
  reports unpruned growth past 98k tokens per request. Orchestra promotes
  verified, non-obvious repository knowledge to tracked `.agent/` files or docs
  at the durable knowledge checkpoint.
- **Chained PRs** (gentle): worthwhile only when tasks routinely produce
  oversized PRs; the largest recent pilot task was rescoped to 1,175 lines.

From Orchestra evaluations between 2026-10-08 and 2026-10-12:

- **Adversarial third review round**: it helped one case, but anchored on
  earlier dismissals and missed both remaining defects of another.
- **Third parallel reviewer**: it found nothing beyond the two-reviewer pair.
- **Origin and visibility fields plus a context block in the review packet**:
  no fewer review loops and fewer real defects found.
- **Triage rule "reject a finding that was not reproduced"**: it lost two
  real defects in four of four runs; a constructive check replaced it.

From mattpocock/skills `5beb35b`, reviewed on 2026-10-20:

- **Issue tracker as workflow state** (`to-spec`, `to-tickets`, `triage`,
  `wayfinder`): a second state store beside the local plan and Git; the Tasks
  companion owns cards.
- **Parallel implementers over a ready frontier** (`implement-spec`): its
  users report file and naming collisions and a four-hour review-fix loop;
  Orchestra keeps one writer per checkout.
- **Code-smell catalogue in the reviewer** (`code-review`): it contradicts the
  reviewer-instruction result above and feeds the non-converging reviews its
  users report.
- **Git command blocking hook** (`git-guardrails-claude-code`): it blocks
  every push, including authorized delivery; protection from destructive
  commands belongs to host permissions, which Orchestra does not change.
- **Fixed pre-commit stack** (`setup-pre-commit`, Husky and Prettier):
  repository readiness sets gates that fit the project's stack.
- **Mandatory domain glossary and deep-module vocabulary** (`domain-modeling`,
  `codebase-design`): no recorded failure comes from vocabulary, and the design
  substance is already in shared guidance. Revisit if reviews keep finding two
  names for one concept.
- **Learning workspace** (`teach`): a multi-session course of lessons and
  quizzes rather than development; explaining to a person is already covered.
- **Handoff document** (`handoff`): the local plan, conversation continuity
  and host compaction already carry the work forward.

From pstack `13f7ad1`, reviewed on 2026-10-21 and measured on 2026-10-22:

- **Formal verification skills** (`create-formal-verification-skill`,
  `maintain-formal-verification-skill`): on NeniTPV before its cash-drawer
  race fix, one blind run of each with the same model, a TLA+ model with
  real-code reproduction and a plain investigation reproducing with ordered
  threads, found the same two of three known defects and missed the same
  PostgreSQL-only one. The plain run found more, scoped them by entry route
  and took 11 instead of 19 minutes. Revisit for a protocol designed before
  runnable code exists or for interleavings that real-code reproduction
  cannot reach.
- **Prompt sharpening** (`/sharpen`): asking what an expert would add that the
  user did not request widens scope, as an exhaustive specification did before
  the owner narrowed it to routine use; primary sources and an outside check
  already belong to research and verification.
- **Brand from a type guard instead of `as`** (TypeScript): the compiler checks
  a type predicate no more than the cast it replaces; creating brands only in
  a parse function already gives the guarantee.

## Modular workflow acceptance

Reusable engineering and project-verification entries plus an explicit parent
coordinator compose with full Orchestra task roots. Standalone and explicitly
selected custom work remain modular uses.
[Modular acceptance](evaluation/MODULAR_ACCEPTANCE.md) separates source/routing
checks, the two-repository integration canary, live host trials and matched
quality evaluation. Host-provided checkouts are retained for host cleanup after
authorized delivery. The same four roles and seven internal playbooks remain.

Broader live parent/child acceptance and public distribution remain pending.
Further installation changes require their own authority. Current source tests do not prove
that every host discovers a skill, that cloud resume works in all environments,
or that generated code improves. Keep comparative evaluation after bounded
plugin acceptance and preserve the pending distribution and Bridge work above.

### Persistent project coordination

The source now extends the existing coordinator with one persistent Markdown
register, independent task-root resources and same-repository parallel checkout
ownership. Codex task chats and Cursor Projects have separate native mappings;
the latter selects `grok-4.7-xhigh` for task roots while the parent remains
user-controlled and role matrices remain unchanged. Prepared-source paths are
explicit across hosts. Pending isolated tasks can receive a reviewed exact-base
refresh before normal authorized delivery. This adds no Tasks dependency, service,
public role, report schema or automatic installation migration.

[Project coordination acceptance](evaluation/MODULAR_ACCEPTANCE.md#project-coordination-and-base-refresh)
separates helper/routing/package checks from still-pending live Codex and Cursor
Projects trials. Actual Project coordinator launch tools, nested tool inheritance,
background continuation and browser access remain host-specific acceptance gaps;
a worker's schema report is not a successful run. Active-package replacement
and remote Project pin changes are separate delivery steps. Preserve the deferred authority/continuity and
matched-quality trials, Bridge and public distribution boundaries above.

### One coordinated execution workflow

Coordinated children use full Orchestra; investigation-only authority makes the
existing discovery usable before implementation approval. The parent explains
that evidence and resumes the same root when supported, without repeating settled
approval. Ordinary roles and engineering remain available independently.
Lite has been removed, including its public kickoff/result contract, exclusive
validator and fixtures. There is no transitional route or automatic fallback.
Conditional cross-environment acceptance uses existing review/verifier roles.

The next live trial must exercise the parent, investigation-only child,
approval continuation, local roles,
retrievable evidence and cleanup on the actual host. That trial remains pending;
removal does not establish nested execution or quality improvement. Remote Project
preferences must point to the updated pinned source; local package updates cannot
change those preferences. Preserve the deferred evaluations listed above.

## Preventive engineering and maintenance

The maintenance entry extends modular engineering with evidence-backed diagnosis
and authorized repair of harmful code, documentation, rules and examples. Folder
reorganization is excluded. Shared guidance owns the source-comment policy and
prevention ladder; enforcement, personal adoption and real-project outcomes are
separate acceptance classes in the modular evaluation recipe.

After source/package validation, verify personal global-rule adoption and fresh
root/worker behavior on the supported hosts. Then select the real pilot repository
and area, preserve its baseline, prove a reusable journey and review a bounded
repair. Matched quality evaluation retains the plugin acceptance prerequisite.
No source test demonstrates universal instruction inheritance or improved code.
Event intake, scheduled gardener jobs, automatic feature-map maintenance, formal
verification and dashboards remain deferred. Existing distribution, coordinator
host acceptance and Bridge work above retain their separate boundaries.

## Decision evidence and cross-environment acceptance

Shared decision evidence and conditional parent-side reproduction apply through
one coordinated workflow. Retired Lite delivery observations remain in the pilot
record; its kickoff/result contract and distribution are removed. Conformance
proves source routing and structure, not agent compliance.

The remaining bounded
[three-case pilot](evaluation/MODULAR_ACCEPTANCE.md#decision-evidence-pilot)
uses decision mapping and independent review together, holding resources fixed,
after the existing plugin acceptance boundary. Its new live cases are deferred
as recorded above.
The external coordinator supplies verified case bases and hidden expected
outcomes. Only isolate the two effects if the combined pilot reveals a question
that warrants the extra runs. Keep correctness and regressions ahead of cost or
speed, and preserve all earlier distribution, adoption and Bridge follow-ups.

## Decision quality and useful verification

The shared criteria now cover risk-specific decisions, bounded pre-code review,
necessary scope, affected documentation and behavioral test quality across full
Orchestra and standalone work. Test-suite diagnosis and repair extend repository
maintenance; no new role, result schema or E2E-only policy is introduced.
Coordinators reconcile required checks and reject inconsistent success reports;
source conformance still does not establish live report acceptance.

The [refund pilot](evaluation/MODULAR_ACCEPTANCE.md#recorded-refund-pilot-2026-09-28)
adds evidence about technical premises frozen into plan acceptance, prior-operation
fixtures and root exposure to another candidate. The correction separates binding
outcomes from technical plan choices, checks new authoritative uses and reachable
writers, and clarifies Grok dispatch recovery. The real state-transition journey,
fresh root-and-role evaluation and live host recovery remain pending; source
validation does not complete them or update active installations.

Use the [pilot follow-up](evaluation/MODULAR_ACCEPTANCE.md#decision-quality-and-useful-test-follow-up)
to evaluate correctness and maintainability separately from diff size, test
counts or speed. Preserve known-answer regressions and include a held-out case
under matched resources. A real test-cleanup pilot needs an explicitly selected
repository/area; source changes do not authorize deletion in consumer projects.
Broader adoption, future installation changes, public distribution and Bridge
retain their existing sequencing and authority boundaries.

## Authority and conversation continuity

Shared decision evidence now separates observed facts, authorized behavior,
recommendations and unresolved policy. Bounded decision review covers material
choices even when an analyst labels them settled. Coordinator synthesis consumes
the relevant producer report before attributing a failure or accepting work.
Conversation continuity preserves the active objective and native handles across
user questions, worker commentary and interruption, without new workflow state.

The shipped source-preparation helper verifies one full revision and refuses to
replace existing work. Consumer environments may prebuild that checkout or load
a verified package; Cursor Cloud environment configuration remains consumer-owned.
The deferred [authority and continuity pilot](evaluation/MODULAR_ACCEPTANCE.md#authority-synthesis-and-continuity-follow-up)
specifies an ambiguous case, its authorized-policy variant and a held-out
continuation case. The recorded observations below do not complete that sequence.
Host behavior and broader quality improvement remain unproven by structural
checks alone. Future integration, release labels, installation changes and public
distribution retain their existing explicit delivery boundaries.

The [recorded authorization pilot](evaluation/MODULAR_ACCEPTANCE.md#recorded-authorization-pilot-2026-09-25)
separates production, test and documentation deltas and preserves selected fault
checks, human interventions and verification limits. Follow-up focuses on
negative-test preconditions, changed-test review and proportional planning for
settled caller/server changes. These corrections do not establish model savings;
held-out and matched quality evaluation retain their existing prerequisites.
