# Orchestra Workflow

## End-to-end flow

```mermaid
flowchart TD
    U["Normal chat"] --> Q{"User intent"}
    Q -->|"Direct change, plan, or implementation"| DX["Ordinary direct execution outside Orchestra"]
    Q -->|"Explicit $orchestra or use/start Orchestra"| B["Minimum task brief"]
    POM["Planning-only host mode"] --> WAIT["Reuse context, pause mutation, continue when execution-capable"]
    B --> FA["Resolve the flow assignment"]
    FA --> E["Read-only Git and readiness preflight"]
    E --> RC["Focused repository context: root-direct or analyst"]
    RC --> C["Evidence-grounded final specification"]
    C --> CM{"Managed or hybrid checkout"}
    CM -->|"Managed"| OW["Create task branch and portable worktree"]
    CM -->|"Hybrid"| HB["Create task branch in current clean checkout"]
    HB --> P
    OW --> P["Plan overview plus one document per phase"]
    P --> PJ{"Root decides whether plan review is proportionate"}
    PJ -->|"Review"| PRV["Reviewer reads exact bundle; planner replaces affected documents"]
    PRV --> P
    PJ -->|"Ready"| A
    A["User approves exact bundle"] --> W["Write overview and phase manifest as active"]
    W --> F["Execute the next phase"]
    F --> PV{"User preview?"}
    PV -->|"none"| R["Review and verify"]
    PV -->|"required"| UP["blocked user_preview"]
    UP --> AB["Absorb and freeze"]
    AB --> R
    R -->|"Material finding"| F
    R -->|"Accepted"| X["Confirm cleanup and retire phase agents"]
    X --> M["Root commits the phase"]
    M --> N{"More phases?"}
    N -->|"Yes"| F
    N -->|"No"| D["Delivery-ready implementation"]
    D --> H{"User or prior delivery instruction"}
    H -->|"Hold"| HX["Committed branch/worktree ready"]
    H -->|"Local integration"| LI["Verify, integrate, clean worktree and branch"]
    H -->|"PR"| PR["Open PR, review/fix/push until clean"]
    PR --> PMG["Merge only when separately authorized"]
```

## Orchestrator behavior

Orchestra is an explicit planned-work route. It activates only through
`$orchestra` or an unequivocal imperative to use or start Orchestra. Ordinary
plan requests, descriptive mentions, and direct change, fix, or implementation
work remain outside Orchestra.

If Orchestra is invoked in a planning-only host mode, reuse the conversation,
identify the latest candidate checkpoint, and pause before branch, worktree,
plan persistence, implementation, or commit mutations. Ask the user to switch
to an execution-capable mode, then continue without a second invocation.
Orchestra observes the host mode; it never changes the host into a
planning-only mode.

Every agent writes in the user's language: messages to the user, packets,
reports, plans, overviews and task-private artifacts, so no artifact mixes
languages. The user's language is the one their instructions set, otherwise
the language they write in. Literal keys, status values, markers and
identifiers Orchestra names stay verbatim. Tracked repository artifacts
(code, comments, commits, PRs and docs) follow the repository's convention.

Every dispatch starts from a clean context: the packet and named artifacts
carry the assignment, dispatched under "T3 Code host". A closed owner or
reviewer is recorded unavailable and replaced with the same logical assignment
and exact approved artifact IDs; a replacement reviewer is always fresh and
independent.

## T3 Code host

The full workflow runs inside T3 Code. The task root is a T3 thread on a
provider whose `orchestra` entry skill is installed (Claude Code, Codex,
Cursor or Grok today), and the `t3-code` MCP tools are its host: T3 owns
threads, worktrees, role transport, the browser and pull request watching, and
the T3 Code reference `host_t3.md` defines the exact calls. Without those
tools the root says that the full workflow needs T3 Code and offers the
standalone skills instead.

Every provider T3 runs is an executor, not a host. "Flow assignment" names the
provider instance, model and effort of each role, and `delegate_task` carries
it. Supporting another provider needs only its row and one role check against
the live `orchestrator_capabilities` catalog: the child reads its role skill by
absolute path, publishes its report, and keeps a read-only assignment
read-only.

Every dispatch is a fresh `delegate_task` child; each fix round and each review
round starts a new one. The root continues a child's thread only for preview
absorption or an unfinished turn, and waits under "Agent waiting". The child's
returned result is the completed-state evidence before commit. After every
return the root checks Git status and HEAD; a read-only role that changed
anything beyond its declared report blocks.

Resolve executable resources through `orchestra/runtime.md`. An installed
plugin keeps skills, helpers, the flow assignment and WORKFLOW in one
relocatable package; explicit source mode uses a prepared checkout. Settings
and the user's flow overrides stay outside the package under
`${ORCHESTRA_HOME:-$HOME/.orchestra}`. Installing or loading the plugin does
not activate Orchestra or grant delivery authority; install it once per
provider to avoid duplicate skills.

T3's runtime mode and each provider's permission choice are observed, never
written or raised: children use `runtimeMode: inherit`, and a denial is never
bypassed. The Claude Code plugin's only hook allows read-only tools inside its
installed package, so a Claude child can read its role skill.

The orchestrator keeps the main objective while adapting safely to facts
found during execution: it does not stop for routine technical choices or
follow a stale step when a reversible correction is clearly needed, reports
meaningful scope or design changes, and owns capability routing, the local
plan, phase commits, direct PR observation and final judgment.

## Standalone tools

The role skills and `orchestra-phase-commit` also support direct user requests
outside the planned workflow. Calling one never activates `$orchestra`.
The same role boundaries apply: analysts and reviewers are read-only,
implementers own bounded edits, and verifiers inspect behavior without editing
source. The direct request supplies intent, scope, target checkout or revision,
available evidence, and authority; ask only for information that cannot be
inferred safely. Return a concise inline result unless a named consumer needs
a file. Standalone work requires no flow assignment, phase IDs,
plan persistence, or fabricated Orchestra artifacts.

Capability playbooks retain their substantive engineering guidance in direct
use. Their phase-specific transport, artifact naming, preview decisions, and
plan bundle requirements apply only inside an activated Orchestra task.
Standalone planning returns a proportional proposal without writing a formal
plan bundle; visual work still supplies inspectable evidence through the
available host. Repository checks and authority boundaries apply in either
route. A standalone commit requires explicit commit authority and honest
verification/review status; it does not certify independent review. Within
Orchestra, a phase commit still requires the approved plan and all current
review and verification gates.

The PR and local-integration skills remain specialized delivery tools with
their existing policy, task identity, authority, and freshness requirements;
standalone role use does not waive those contracts. They do not require legacy
`commitbot`, `prbot`, `openprbot`, or `prmerge`. Direct code or PR analysis may
use the reviewer role without creating Orchestra delivery state.

## Modular engineering

Orchestra supplies reusable engineering capabilities as well as an explicitly
selected planned workflow. `orchestra-engineering` can be discovered for an
ordinary investigation, explanation, design, implementation or evidence task;
it preserves that task's outcome, authority and chosen flow. It does not
resolve the flow assignment, create task state, dispatch agents, require phase reports or activate
`$orchestra`. `orchestra-project-verification` maintains and executes reusable
project verification knowledge under the lifecycle below. Installed metadata
makes skills discoverable, not guaranteed to run; hosts without automatic skill
routing can invoke the same skill explicitly or link it from an authorized
project instruction. Never claim universal enforcement from installation.

Route by the required result, not by a list of mandatory activities. An
implementation can investigate, try a bounded experiment, change code and test
it within its existing authority. A read-only question stays read-only. A
simple edit does not acquire an architect, research pass or verification map.
Use independent roles when their responsibility or evidence independence is
needed. A selected role keeps its limits; reading a playbook's engineering
technique does not make an implementer an independent reviewer or grant an
analyst write authority. Existing custom workflows may consume these resources
without producing Orchestra artifacts.

The substantive criteria, including the mandatory source-comment policy for
authored source, live in `architecture_guidance.md`; capability
playbooks add domain technique, and role skills define bounded assignments.
Orchestra's own workflow rules, role boundaries and engineering conventions
are revisable design choices. Within authorized scope, propose and review a
better mechanism at its canonical source; an existing rule is a current
constraint, not an immutable product decision or a reason to reject a viable
improvement. Evaluate Orchestra changes against VISION.md "Success criteria"
and "Quality per token". Distinguish a proposed benefit from observed
improvement and generalization evidence. Changes to authority or delivery
policy follow their respective authority boundaries; rule changes do not
themselves grant task or host permissions. Until an
authorized change is accepted, do not silently ignore normative instructions.
New rules must address the demonstrated cause rather than accumulate
prohibitions after every failure.

## Repository readiness

`orchestra-repo-readiness` is the explicit entry that prepares an existing
repository so agents can work in it reliably: it diagnoses the repository
against its target state, repairs what a grant names, cleans the test suite and
maintains `.agent/` conventions. The target state lives only in that skill. It
composes with ordinary engineering and full Orchestra without activating the
workflow, creating task state or adding a mandatory audit stage. Every
source-writing entry consumes the comment policy directly.

Diagnosis needs only the brief's execution authority and never edits. It
reports each item with observed evidence and coverage; sampled inspection never
certifies the whole repository. A repair grant names the area or items and
covers in-scope investigation and reversible fixes without a second approval
per candidate. Material product, public-contract, data, security or normative
policy changes remain proposals. "Repository conventions" owns policy writes;
never relax a rule to authorize the operation it blocks.

Repairs prefer structure, then mechanical checks, then text. One implementation
owner carries each problem across code, docs and tests; parallel writers need
disjoint paths. The root resolves overlap and policy edits and preserves
independent implementation review through the selected route, using the
existing completion-aware waiting policy. No health score, backlog service or
report schema is introduced. Folder reorganization, aesthetic renames,
formatting sweeps, major dependency upgrades and unrelated behavior changes are
out of scope. Recurring mistakes are repaired through that skill.

## Project verification

`orchestra-project-verification` supports four operations: prepare a useful
feature map, run selected journeys, refresh affected knowledge, or audit a named
map. The direct brief or approved phase supplies authority; no separate
plan, report schema or global install is required. Reuse maintained repository
documentation and tests. If no entry exists, `.agent/verification/README.md`
may index short feature recipes and existing commands. Keep helpers with the
repository's test tooling and retain them only for a recurring interaction the
current tools cannot express cheaply. Do not wrap adequate tools for symmetry.

Preparation discovers real commands, entry points, supported test data and
runtime prerequisites. Start with the most useful three to five journeys (or
fewer for a smaller product), then prove one end to end when execution is
within scope. This is a starting set, not a coverage claim or universal quota.
A read-only preparation produces a proposed map and unexecuted recipes; it
never claims that a runnable application was observed. Recipe content and proof
standards are in shared engineering guidance, "Verification recipes".

A run uses the selected recipes against the actual instance and revision. The
executor verifies readiness, performs the named behavior, inspects its effects,
and retains evidence outside disposable runtime data before cleanup. A cold
agent should be able to follow the entry without prior conversation: provide
only the prerequisites and references needed for that journey. Authentication
requirements name credential categories and safe provisioning, never values.
Missing credentials, unsafe reset or unavailable interaction capabilities are
explicit gaps, not permission to bypass them.

Refresh follows affected behavior and dependencies. An explicit full audit
covers every entry in the named map, including blocked/unexecuted ones; it does
not silently expand ordinary maintenance to the whole application. Classify a
failure as recipe drift, insufficient interaction tooling or a product defect
using current evidence. Correct an authorized stale command or helper and
re-exercise it; never change the expected result merely to fit a regression.
Record draft versus demonstrated recipes and their relevant revision/environment
without appending a history of every run. A feature list is not test evidence.

An authorized implementation may maintain affected descriptive recipes and
necessary test helpers in its named scope, including operational `.agent/`
paths. A planner names those paths when a phase needs them. Normative policy
(hard gates, product expectations, required architecture or prohibitions) still
follows "Repository conventions"; moving policy into a recipe never evades its
authority. Per-run screenshots, logs and task progress belong to existing task
reports/private evidence, not the reusable knowledge store or plugin cache.
The normal review/check loop assesses meaningful recipe changes with the code.

## Initiative coordination

`orchestrator` is an explicit route for an initiative with genuinely
independent project, repository, acceptance or task-root boundaries; it never
activates from a multi-file edit and needs no Bridge.
Ordinary work stays one task with proportional phases. An initiative may span
concurrent tasks in one repository, several repositories or projects on
different hosts; resolve actual Git roots, instructions and execution
environments rather than treating a project name or folder as the scope.

The parent owns shared intent, contracts, dependency ordering, resource
choices within the user's selection, cross-child decisions and combined
acceptance. Each child owns its plan, implementation, review, verification and
permitted delivery as a full Orchestra root with proportional phases and the
normal role agents, carrying explicit activation in its packet; task size and
repository count never select another workflow. A child root is a T3 thread,
not a leaf `delegate_task` role. A user's explicit custom or standalone
selection stays available under "Standalone tools", identified as such,
never presented as Orchestra execution or used as an automatic fallback. If the host cannot execute a root
responsibility, report that gap. One parent coordinates independent children;
children create no further hierarchy or sibling tasks.

Before dispatch, the approved initiative identifies each child's outcome,
repository and scope, exclusions, acceptance, route, shared
contract and dependency conditions. Children are cut as cases under shared
guidance "Staged outcomes", each ending in a result the user can try, not by
component or layer. Authority is inherited only within those
bounds; implementation, phase commits and each delivery action are separate
grants. The parent may accept derived child plans within the already approved
implementation scope,
but never pretends the user approved an unseen artifact or reopens settled
approval at every child. Children route unresolved material product,
public-contract, security, cost or destructive decisions to the parent, which
asks the user when existing authority does not settle them. Host permission
prompts remain user or host decisions. Unsupported models, tools or
authorization produce a precise blocker, never a substitution. Independent
unaffected work may continue while one child waits.

An exploratory assignment without implementation approval goes to a
root-capable child with investigation-only authority, naming the bounded
question, inspected product revision, investigation resources and a parent-readable
report destination. The child runs the read-only investigation of "Context
and planning", directly or with focused analyst evidence under "Standalone
tools"; only explicitly assigned analysis resources are
authorized. It returns the evidence-backed specification, cause or remaining
hypotheses, affected scope, risks, verification approach and a proportional
plan candidate when useful; unavailable reproduction stays
an explicit limitation. The report is authorized output outside product
source, not a phase plan or task state, and grants no implementation, branch, phase
state or delivery. A host-provisioned checkout is a separately authorized
resource with one owner and a cleanup handoff, not permission to edit.

The parent synthesizes that report for the user's decision without repeating
the investigation, then continues the same root when supported, carrying only
the actual scope, implementation, commit and delivery grants and
investigating only a material context delta. Use the existing combined
approval or parent acceptance of a derived plan, never a child approving its
own unseen plan; already authorized implementation gets no extra user stop
merely because the child investigated. An unavailable handle uses the
recovery rule below and the accessible report, never an automatic second
writer.

Keep one compact Markdown register, typically `BOARD.md`, linking the approved
brief and authority, repositories and checkout owners, shared contracts, child
routes, task-root resources, native handles, dependencies, results,
accepted SHAs, blockers and actual delivery. Each delivered task's line also
records its review rounds, how many times the user had to step in, and any
later revert or fix, so a rule change can be judged against outcomes. It replaces the initiative
index and does not duplicate child plans; optional `PROJECT.md` holds stable context, not progress; Now/Next/Done
are navigation, not states. Git and the host own execution state; a backlog
entry grants no authority.

Honor the user's chosen accessible location; otherwise use a caller-owned
external folder, an explicitly selected ignored
`<repo>/orchestra/projects/<project>` in a persistent checkout, or a verified
native project store. Resolve Git's exclude path with `git rev-parse
--git-path info/exclude` (`.git` may be a file). Never keep the register in
`.orchestra` or a disposable checkout. Verify access and retention, including
across hosts; ignored files are not backups, so retain or export needed
context through authorized storage at project closure or before
environment teardown. Obsidian may
edit these files but is no dependency. Durable repository knowledge follows
"Repository conventions".

The parent is the register's sole agent writer; children write their reports
elsewhere. Reread before narrow updates to keep human edits. An approved brief
is never rewritten: a later decision is appended as a dated amendment naming
what it supersedes, so a reader still sees what was approved. Write the pending
dispatch intent before launch, then the observed handle. A missing file or
pending row proves neither an empty project nor a failed launch: reconcile
native state first. Recover retrievable existing authority without re-asking;
unresolved material grants remain questions. Keep final evidence and
continuation handles while they have a consumer and remove only owned
transient prompts and logs no longer needed. No board schema, allocator, database or watcher.

Select resources separately for the parent, each task root and its role
agents. Carry the explicit root model and effort in the packet and register
through T3's actual controls; role assignments follow "Flow assignment".
Actual concurrency, nesting and
tool access must support the assignment; a model-family label is no evidence
of effort.

The parent's own research before dispatch (repositories, entry points, shared
contracts) never inherits the parent's model: it uses the flow's
`repository_context` row unless the user selects other resources, through a
source-read-only `delegate_task`. Start
one analyst per repository or independent area in the same turn, each with
only its framing questions; a contract question spanning areas goes in exactly
one packet. Each answers inline, Summary first, with Details limited to the
evidence behind each answer. Facts the children must share go into the brief,
register or a child packet, not a research file. A problem needing a cause,
specification or plan candidate goes to an investigation-only child root.

Launch each task root as a T3 thread under `orchestrator/host-transports.md`
in the resolved skills root, and internal roles through `delegate_task`, never
as a claim of persistent task-root capabilities a leaf lacks. Check
availability before launch, preserve exact thread identities and use argument
APIs or safe quoting. Never strip a root's protections, enable hidden bypass
permissions, or assume a plugin provides missing tools.

Exactly one checkout creator owns each checkout: T3's thread transport or
the child's setup, never both; a clean host-supplied isolated checkout may be
adopted under "Child root setup". Several mutable repositories get separate
checkouts and owners or explicitly serialized writes, each with its own
instructions. Never run two writers in one checkout; same-repository parallel
tasks need separate checkouts, and an explicitly shared checkout serializes
writes. Reconcile shared ports, databases and containers too: Git isolation
does not isolate them. Read dependencies from accepted revisions or a fixed
contract, never a sibling's evolving files. `completed` evidence marks a
reviewed child revision; `delivered` only an actual integration into the
required base or environment.

Resolve instructions separately from the product checkout through the
selected runtime and source-preparation recipe: each environment uses one
verified plugin or pinned read-only source, with absolute entry, role,
workflow and flow assignment paths in packets. When changing Orchestra itself,
prepare that copy before source edits. Verify it at launch instead of
reinstalling per role. Project preferences point to the pinned coordination
entry instead of copying its policy. After an update, report the instruction
revision the next child uses; local plugin updates do not change remote
Project pins.

Before mutable work in a disposable environment, settle how the parent
retrieves the accepted revision and required reports or screenshots after
release: the task-branch push grant with a verified remote SHA (never base
push, PR or merge authority), or an authorized retained artifact or held
result. Resolve a missing preservation route before dispatch. An
environment-local path is no evidence of cross-host access; send an
accessible bounded packet or report.

Waiting follows "Agent waiting": completion and attention events with known
handles and cursors, compact summaries at stable handoff, and no active diff
or file inspection or repeated transcript reads to infer progress; an interactive CLI does not by itself
cure polling. On a stable result, read full child evidence only when a missing fact or concrete
failure requires it. Process success establishes neither acceptance,
independent review nor delivery.

A child messages the parent only when it needs the parent or is done: a
decision outside its authority, a derived plan for acceptance, a shared
resource request or release, a blocker, or its stable final handoff. Progress,
started work, unsubmitted candidates and intermediate results stay in its own
thread and reports for the parent to read when needed; a grant is acknowledged
by acting on it, never by a reply. A parent woken by a message that needs no
decision records any needed register fact without narrating it to the user.

After interruption or an ambiguous launch, reconcile the existing host handle,
checkout and Git revision first; a pending entry does not mean nothing
launched. Never replay a mutating packet or create a replacement while an
earlier owner may be active; if the host cannot settle that, block that child
for reconciliation. Resume the same logical child with the current revision,
accepted correction scope and changed dependency evidence. Replace a confirmed
unavailable owner only after its writes stop and its checkout and evidence are
handed over. A local failure requires no whole-initiative restart.

Every implementation handoff gives repository, checkout, base and final full
SHA, acceptance, checks, independent review status, evidence and recipe
paths, blockers, assumptions, delivery state and resource cleanup. The parent
consumes it once, then runs the real cross-project journey against the exact
set of accepted revisions and relevant environment and configuration, naming which revisions
and determining non-Git dependency versions actually ran; individual green
suites cannot establish a shared contract. Before integrating a child
revision, the parent runs the repository's hard gates itself at that exact
SHA in a clean checkout, since a child may reuse evidence across its last
delta, and reads every changed test assertion against the product's real
behavior; a test changed to match a mock or current output is a finding. A
child the user authorized to `merge when clean` is its own integrator instead:
once its PR is clean and its branch contains the current base (otherwise it
first refreshes under "Base refresh before delivery"), it merges and reports
the merged SHA to the parent once; joint acceptance then runs on the delivered
base. A parent without the repository's execution environment commissions
these runs to a verifier in that environment at the exact revision and judges
its actual commands and exit codes.

A joint failure goes to its owning child as a focused repair, keeping the same
child and reviewer when supported. Before that child's delivery, a repair
within approved intent reopens only its affected implementation, review and
check cycle and updates its terminal SHA and plan, the same bounded exception
as an accepted PR fix. Unchanged sibling evidence stays valid; a changed
interface invalidates dependent acceptance even without sibling code changes.
After verified delivery, a repair is a new bounded child task or PR from the
delivered base under the remaining authority, checking whether its delivery is
covered; never reuse a merged PR or its pre-squash branch, and preserve the
old plan and delivery evidence. The parent reviews contract and integration
consequences rather than repeating unchanged local code reviews. Completion requires joint acceptance
and honest delivery state, not a list of successful child messages; merge,
push, release and deployment stay separately scoped under delivery policy.

An initiative parent may keep a periodic read-only retrospective: a cheap
periodic run only counts closed initiatives from the register and Git or host
state and, once three more have closed since the last retrospective thread,
launches a read-only thread (Claude Code `claude-opus-5-5` at `xhigh`) that
analyzes finished threads, reports, PRs and Git and returns only
evidence-backed proposals, consumed under "Engineering guidance and evidence".
An approved proposal enters through a normal root and PR; agents never rewrite
their own skills or policies. Beyond that periodic run it adds no artifact,
persistent counter or watcher.

### Child root setup

A child root, whether an initiative child or a task a Hermes dispatcher
launched, first resolves inherited approval and the supplied checkout here and
under the checkout rules, reusing settled scope and authority instead of
presenting them as new decisions. Inherited authority never approves the
child's own plan: it sends the plan to the parent thread and implements only
after the parent accepts it. An investigation-only
grant runs the read-only steps and returns at specification confirmation (or
the combined candidate), never reaching setup or execution without that
authority.

A child may adopt a clean isolated host-supplied checkout and owned non-base
branch after verifying repository identity, the approved base and HEAD, and no
other writer; a detached HEAD or base branch there gets one collision-free task
branch at that revision. For managed setup, an approved full base SHA in the
parent packet overrides upstream selection: verify it is available and
contained in the selected local base or its fetched upstream, then create the
checkout there, or block for parent reconciliation. Before setup or refresh
meant to publish, the base SHA must be in the fetched upstream unless the grant
covers publishing those local-only commits; otherwise the parent reconciles
publication scope. This never limits an authorized held result or local-only
integration. A child launched from a shared primary directory establishes its
isolated checkout before any write and uses it exclusively; an explicit
shared-checkout choice serializes writers. Supplied branches are not the
integration base; use managed semantics. Unexpected commits, even descendants, are preserved,
reported and reconciled; unknown work is never reset. The parent may direct safe selection of the approved
revision or accept a new captured base through a focused context delta. When
host metadata and the actual branch disagree, establish how resume and
publication use the branch first; invent no metadata API.

### Cross-environment acceptance

The child's independent review remains its responsibility. Parent-side
reproduction is conditional on a named risk, inaccessible evidence or a
different acceptance environment leaving a material verification gap. First
request retrievable child evidence or a focused correction where that
suffices; otherwise commission the missing proof at the exact child full SHA, before or after
delivery, in an owned independent checkout naming checks, environment,
permissions and cleanup. A verifier executes runtime or browser checks; a
reviewer assesses source and uses only the diagnostic execution "Review
policy" allows. `orchestrator/acceptance-packet.md` under the
resolved skills root illustrates this handoff without a result schema or a
mandatory second review. A shared VM does not remove reasoning independence;
a different environment establishes a separate property.

Consume actual commands, exit codes and limitations, not prose claims of
success, against repository requirements and authorized exceptions under
"Engineering guidance and evidence". A failure also present at the base is
evidence about its cause, not a waiver or a pass. Preserve partial work and
route findings to the same child and reviewer; the parent does not take over
its implementation or review loop.

### Hermes dispatcher

Inside T3 Code a Hermes thread may be the parent of one task or of an
initiative. It works out the request with the user, recommends, launches task
roots with the confirmed brief and the user's delivery endpoint, accepts a
derived plan that stays within that brief, relays any other plan and every
question to the user, and follows their reports. It never implements, not
even a small fix: every change goes through a task root and its review. It reads the pinned
instructions and the flow assignment by absolute path, needs no plugin, and
runs its own research through `delegate_task` on the flow's
`repository_context` row. It lacks the repository's execution environment, so
it commissions hard gates and joint acceptance to a verifier as described
above. For one task the register holds just that task's line. How the user reaches
Hermes and what Hermes remembers belong to the user's Hermes configuration;
repository knowledge stays under "Repository conventions".

## Flow assignment

There is one flow. `flow.toml` in the selected runtime (source
`codex/config/flow.toml`) assigns each capability a T3 provider instance, a
model and an optional effort, names the second reviewer of the review pair
under "Review policy", and lists the later recovery attempts. A user changes
the assignment in `${ORCHESTRA_HOME:-$HOME/.orchestra}/flow.toml`, which has the
same shape: each capability entry, `review_pair` or `escalation` it defines
replaces the shipped one whole, and anything it omits keeps the default. Never
edit the installed package to customize a task; `orchestra-models` shows the
assignment and writes the user's file.

Resolve the assignment once before the first dispatch and check every row
against T3's live `orchestrator_capabilities` catalog, as `host_t3.md` maps it.
An unavailable provider, model or effort blocks only the dispatches that need
it until the user selects a supported option; never substitute another
provider, model, account or billing path silently. When quota or credits are
the cause, continue work that does not need it and ask once: a recommended
substitute for the affected roles, keeping a reviewer outside the
implementer's model family, or waiting until the user reports the quota is
back, after which the original row runs again. Record the resolved assignment,
its override source and any chosen substitute in the plan Decisions. On resume
compare them with the current files; drift needs an explicit decision, never
an unnoticed reroute. No assignment waives production, migration, data,
security, payment, destructive-action or delivery authority.

Four roles carry every capability, and each role skill is self-contained.
`repository_context`, `web_research`, `technical_planning`,
`architecture_analysis` and `difficult_debugging` use the analyst;
`general_implementation` and `frontend_implementation` the implementer;
`independent_review` the reviewer; `runtime_verification` and
`browser_acceptance` the verifier. The only internal playbooks are
`repository_context`, `web_research`, `technical_planning`,
`difficult_debugging`, `frontend_implementation`, `browser_acceptance` and
`runtime_verification`. `architecture_analysis` uses the review frame of the
shared engineering guidance, and `general_implementation` and
`independent_review` use their role skill alone. Frontend implementation and
browser acceptance never run as one combined role.
`orchestra-project-start` is the additive implicit greenfield entry point;
`orchestra-repo-readiness` is the explicit-only lane that prepares an existing
repository and writes or refreshes its tracked `.agent/` store without
activating the workflow.

The launching conversation owns specification, orchestration, final judgment
and delivery; its model and effort are the user's choice. The root plans and
analyzes architecture itself when its observed model matches the
`technical_planning` row and it has sufficient context, including multi-phase
planning; otherwise it dispatches that row, and it dispatches an independent
planner only for a named investigation or missing context. Independent plan
and code reviews still follow "Review policy". Delegate coherent assignments,
not individual searches or commands; context workers return focused source
evidence that the root does not repeat. Never forward the full chat or turn an
implementer's session into its reviewer.

Recovery applies only to implementation and difficult debugging: attempt one
uses the capability row, and attempts two and three use the `escalation`
entries in order. A failed attempt means the agent returns with acceptance
unmet, establishes a substantive blocker, or exhausts an agreed bounded work
budget without a solution. An ordinary failing test during active development
is not an exhausted attempt. Authentication, quota, unavailable models,
permissions, transport failures and an ordinary wait timeout do not consume
attempts or trigger escalation. Scope or authority blockers require their
existing decision, not a more capable model.

The root decides each transition from evidence after the previous worker has
stopped and its changes and resources are inspected, and preserves useful
edits. Before the second attempt, pass what failed and the current revision to
a fresh child. Before the third, assemble both attempts' changes, commands and
results, failed approaches, discarded hypotheses, remaining acceptance and
exact scope in one compact packet. Difficult debugging remains read-only;
actual fixes use an implementation capability with explicit edit scope. The
rescue model does not replace the independent reviewer or verifier. If the
third attempt fails, report the concrete blocker and needed decision. Do not
reset the ladder by renaming the same unresolved assignment or switching its
capability. Attempt history stays in the existing reports and conversation,
with no retry database or agent registry.

## Autonomy within an approved objective

The root is the technical lead: it receives the objective, hard constraints,
and success criteria, and decides the steps itself.

Preserve the approved objective, behavioral acceptance, scope, authority, and
binding user, repository and verified-contract constraints. An explicitly
user-selected mechanism remains a constraint; if satisfying the result requires
changing a binding constraint, seek user direction instead of overriding it.
Approval authorizes the plan's work; it does not establish the truth of an
agent-proposed technical premise, even when the plan labels that premise a
constraint or acceptance criterion.
When evidence shows that a planned mechanism cannot satisfy the approved
result, the root corrects the affected plan through the existing replacement
and review rules. Reassess only changed decisions and affected evidence. Do not
weaken behavioral acceptance or hard gates to preserve the mechanism; seek user
direction only when the correction crosses a boundary below. Treat causal
explanations as hypotheses and prefer the smallest supported approach that
preserves the approved result.

For requests to answer, explain, review, diagnose, or plan: inspect the
relevant materials and report the result; implement nothing.

Within an approved objective or plan: make in-scope reversible decisions and
carry out the approved work, correcting technical steps as above without asking
again — technical choices, tool and configuration details, file and directory
locations, dependency and environment fixes, changed-approach retries, and
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

Write every question the user must decide in plain words a non-technical user
can act on: each option with what it gives and what it costs, your
recommendation and why, and what waiting costs when that is more than a delay
(a deadline, lost data). When one call covers several items, such as PRs
awaiting merge, list each with its number or link, what it changes for users,
the evidence and its risk, even a low one; never fold them into a count. Show a
visual choice as captured variants rather than describing it. Number the
questions and word each so a plain yes accepts your recommendation, letting
the user answer "yes to all but 2". Ask together only questions that do not
depend on one still open, and ask a decision no running investigation can
change while that work runs. When an answer belongs to someone the user must
consult (an accountant, a client, a provider), offer a short questionnaire the
user can forward, most important question first.

When user participation is genuinely required — a physical action or
observation (unplugging a monitor, another device), how the result feels or
looks in use, an account or approval only the user holds — batch every needed
check into one consolidated request with expected results, instead of
sequential single questions. A verifier or a command keeps everything it can
run or observe, and the product's own logs or output judge a physical step.

## Conversation continuity

Interpret incoming messages in the active conversation. A question,
acknowledgement or progress update does not replace the approved objective,
cancel pending work, change authority or complete the task. A reply such as
"yes" can resolve a pending question; infer its scope from that question, not
from the word alone. A request to continue resumes the existing assignment.
Apply a correction or additional constraint to the affected work while keeping
the rest of the objective. A delivery-only restriction does not pause unrelated
authorized implementation. Honor an explicit stop, pause or cancellation and
preserve unique work; clarify genuinely conflicting intent before dependent work.

During active work, answer incidental questions through the host's nonterminal
response channel when available, then continue the authorized task. Do not end
the turn merely to answer a status question while actionable work remains.
With no active work, answer a casual message from context without starting tools
or a workflow solely because it arrived. Neither case creates task state,
memory initialization, a new wait, cleanup or a checkpoint just for the message;
tools and waits needed by the existing assignment remain valid. Report only
meaningful changes to the existing plan or handoff, not a message ledger.

Worker commentary, a wait timeout and a completed native turn are different
signals. A progress message is not a result, blocker or failed launch. Use the
existing handle and completion evidence under "Agent waiting"; even process
success needs the assigned deliverable and acceptance
evidence. Do not relaunch, retire or inspect an evolving implementation because
its worker said it was still working. A user correction goes to the same owner
when supported, without replaying its original mutating assignment.

After interruption or compaction, retain the objective, constraints, decisions,
authority, completed acceptance, outstanding work and existing handles. Recover
only missing context from the established plan, reports or native session. Check
whether the previous owner is still running, completed, blocked or unavailable
before resuming or replacing it; a missing tool response alone cannot decide
that. Reconcile any interrupted mutation before repeating it, and preserve the
implementation observation boundary. Only affected evidence becomes stale.
Continue independent authorized work while a genuine dependency waits. Do not
create a recovery database or promise continuation the host cannot provide.

## Engineering guidance and evidence

The shared `architecture_guidance.md` reference, reached through the loaded role
skill and its runtime resources, owns reusable engineering criteria and
verification recipes. Apply only sections relevant to the task's acceptance or
material risks; a trivial edit acquires no design exercises, new tests,
benchmarks or dedicated verifier from it. Planning uses "Decision evidence" and
"Behavioral verification" to identify consequential choices, expected outcomes,
failure hypotheses and the evidence to settle them; implementation fills
affected gaps and applies "Change quality"; review assesses necessity,
maintainability and test sensitivity, reconciling original scope with actual
journeys and omitted paths; verification executes assigned checks against
their expectations and records observed effects and limits.
These criteria also apply to standalone roles; capability boundaries,
terminal-check ownership, authority rules and dedicated-gate reasons stay
decisive.

Resolve material acceptance or policy ambiguity before dependent code. Before
implementation, independently review consequential choices that select or
change authorization, cross-system compatibility, data integrity or recovery
behavior, including choices an analyst calls settled; no model or assignment
exempts them. Use the plan review or a bounded decision review, not a second gate for
choices already covered. A consequential choice emerging after combined
approval is still reviewed and reconciled under "Autonomy within an approved
objective" before dependent work. The root supplies the exact identities and
accessible results of the producers behind the decision, including results
omitted from `Review context`; the reviewer reads their material conclusions
and limits and checks for decision-changing omissions against the original
intent. `Review context` routes that evidence rather than replacing it with the
author's summary; incidental facts need no inventory. Assess alternatives,
authority, preservation and discriminating checks using "Decision evidence".
Touching related files or preserving an already reviewed policy needs
no new decision review. Factual questions may first be settled by the analyst
or an authorized experiment. Recommendations and agreement follow the
authority limits in "Decision evidence"; do not re-ask authorized decisions,
and if the owner picks a reviewed alternative, inspect only newly affected
assumptions. Standalone work uses the caller's review route and surfaces a
missing decision or review as a dependency; it never silently dispatches
agents or activates Orchestra. Decision review never replaces implementation review.

At intake, reconcile task acceptance, repository hard gates and optional
diagnostics with their execution owner and environment. "If available" waives
nothing. A genuine exception names the requirement and comes from authority
allowed to change it; inherited task approval does not supply it. Record an
already authorized exception and its limits in decisions instead of asking
again; until reconciled, keep the gate and report its blocker. An exception
covers only its named obligation, never separate review or configured delivery
checks, which need their own explicit authority and a supported policy or
configuration change. Never relabel a
missing mandatory check as optional or passing. Before accepting a report,
compare actual commands, results and source identity with the required set; well-formed output or a green subset is insufficient.

Before accepting work, diagnosing a failure or changing the workflow from a
retrospective, read the producer's relevant report and the evidence that could
change the judgment; a short final message does not prove missing
investigation. Keep observed facts, authorized decisions, recommendations and
uncertainty distinct when synthesizing. If a summary contradicts its source,
correct the summary and its dependent claims and prescribe no fix for the
unsupported diagnosis. Preserve prior reports and name superseded recommendations. This is
bounded source consumption, not replaying logs or repeating research.

Task-specific recipes and material assumptions live in the plan's acceptance,
risks and `Verification`, or the standalone brief; reports carry observed
evidence and limits in their existing fields. A decision map may live in a
report or an explicitly supplied portable document whose revision and access
consumers verify. There is no separate recipe registry or new artifact kind.
Reusable knowledge follows "Repository conventions" and "Durable knowledge
checkpoint"; a suggested recipe never becomes a hard gate by appearing in a
report.

## Context and planning

A root launched by a parent thread first applies "Child root setup".

After explicit activation in an execution-capable mode:

1. Reuse the conversation and classify the checkpoint (exploration, candidate
   specification, candidate plan, adopted implementation, resumable task).
   Obtain a minimum brief: objective, visible result, approximate area, known
   critical risks and bounded factual questions. Without an objective, ask
   before creating resources. Explicit brainstorming stays read-only until
   setup is authorized.
2. Resolve the flow assignment under "Flow assignment".
3. Weigh risk by what the current case touches and who can reach it, not by a
   later stage; that risk decides a dedicated verifier and decision reviews,
   never a separate track. Offer [User preview](#user-preview) in the first
   message that reports the brief when its detection rule matches. Nothing
   waives authority gates for production, migrations, data, security,
   payments, destructive actions or delivery.
4. Run a short read-only preflight: base branch and revision, repository
   policy, canonical runtime, dependency setup, services, permissions,
   credential categories (never secrets), verification commands, test-data
   provenance, generated paths and checkout mode. No branch, worktree, plan or
   fetch mutation yet. Once execution readiness is authorized and before
   substantial work, run the cheap required checks (lint, configuration
   validation) as a baseline and surface
   existing failures with their gate implications; do not run the whole suite
   speculatively, waive a baseline failure or fix unrelated issues.
5. Answer bounded factual questions directly when the preflight covers them;
   the criterion is the evidence still needed, never familiarity. When a
   material amount of source remains, dispatch an `orchestra_analyst` with
   `repository_context`, the minimum objective and those questions: before
   checkout it works read-only in the current checkout and returns a complete
   labeled inline report; afterwards it publishes a revision-identified
   artifact. Close each one-shot analyst; later dispatches request only
   targeted deltas for newly material questions.
   External questions arise only when the task adds a capability the
   repository lacks or replaces a mechanism (authentication, payments, email, storage, search, jobs, analytics and
   similar), adds or pins a dependency, depends on an unpinned external API,
   SDK or platform contract, touches auth, payments, stores or compliance, or
   hinges on a deprecation or CVE; cosmetic, refactor and in-code defect work
   raise none. Resolve them directly when two or three lookups suffice;
   dispatch one `web_research` analyst with dated, versioned questions when
   the remaining volume or the risk of mis-stating a version or contract is
   material, before specification confirmation. A claim about an unpinned
   external contract needs current primary evidence with version or date, or
   stays an Open question or Decision; nobody closes it from memory. For a
   missing capability, present the adopt-versus-build recommendation with
   alternatives against the reported constraints (stack, runtime, hosting,
   credentials, cost, lock-in, data residency) as a specification Decision in
   the same confirmation message; adopting is not a default, the user
   decides, and the plan inherits the Decision with its pinned version.
6. Confirm the final specification (Objective, User-visible behavior,
   Constraints, Acceptance, Exclusions, Decisions, Open questions), visibly on
   first confirmation. When the
   objective holds several user-visible capabilities, an end state or users
   who do not exist yet, apply shared guidance "Staged outcomes" first: the
   specification covers only the confirmed current case, and the vision and
   later cases go to Exclusions with a link to the case list. When security,
   privacy or money is involved, Constraints state the exposure of what the
   change touches: who can reach it and what is at stake. Resolve
   material product questions here; technical review never substitutes for
   the user's authority. Before confirming, ask what the outcome means from
   each reachable prior state in the context's `State writers` (already partly done, refunded,
   consumed, granted). Record the expected result in Acceptance when the
   user's words or a binding contract settle it; when plausible readings
   change a user-visible result, ask it as a material question with a
   recommended reading, never settled by literal wording or current behavior
   alone. Check the user's statements about current behavior against the
   source; when they disagree, show both in the user's terms ("you describe
   partial cancellation; the code cancels the whole order") and ask which one
   the result follows. When acceptance depends on behavior only a run can show
   (hardware, timing, availability, long-running use), confirm the routine-use scenarios
   that prove it; rarer cases go to Exclusions as deferred, neither built nor
   verified, unless the user asks for them. Include the missing-conventions
   checkpoint in the same request when the worktree has no normative
   conventions.
7. A single-phase task may combine specification and candidate
   plan in one message, visibly separated, only when the planning stage
   permits skipping plan and decision review; one approval covers both and a
   specification correction invalidates the plan. Otherwise confirm the
   specification, plan, complete required review, then request plan approval.
   Later in-scope corrections follow "Autonomy within an approved objective".
8. Immediately after confirmation, create the task checkout under "Task
   checkout and branch" (fresh canonical-base tasks fetch the configured
   upstream; a failed fetch blocks; never `git pull`, implicit merge or base
   rebase). Dirty, detached, conflicted, active-operation or
   identity-ambiguous state needs one consolidated decision before mutation.
   Run one idempotent `task_state.py init --worktree <task-worktree>` and
   pass the returned artifacts path to every producer; no global
   registration is required.
9. Confirmation starts formal planning, which the root runs as the root
   skill's `planning stage` reference defines: who authors the plan, review,
   finding judgment and approval. Plan documents, including phase boundaries,
   follow the `technical_planning` playbook.

All planning, implementation, review, verification and commit work uses the
exact selected task checkout. Managed mode leaves the base checkout read-only;
hybrid mode switches only the selected clean checkout to the task branch.
Scoped dirty adoption goes only into a managed task worktree unless the user
authorizes carrying named changes in place.

Implementation begins only after the user explicitly
approves the aligned plan, or the parent that launched the root accepts the
derived plan under "Child root setup". Approval covers implementation and commits at approved phase
boundaries, never merge, release, deployment, production mutation or other
delivery. Adopted committed work that passes unchanged needs no artificial
commit.

If the user rejects or abandons the task before approval, preserve unique
work; remove a managed worktree or restore a hybrid starting branch only when
the captured identity still matches and holds no unique work.

### Local task plan

Before approval the specification stays in conversation and the candidate
exists only as private `plan-overview`, `plan-phase` and optional
`plan-review` artifacts. After approval the root writes `active` to the plan
path returned by task-state initialization, normally
`<task-worktree>/.orchestra/plan.md`, inside the writable checkout with no
protected-path escalation. The plan is an intent, exact-bundle and
resume aid, not a workflow database: no field, artifact kind, ledger or status
beyond those named here.

It records task and Git identity, checkout mode and resource ownership, the
hybrid starting branch and revision, resolved flow assignment, user and root
decisions, authorized preexisting changes, and the effective approved
overview verbatim, including authorized replacements; material corrections go
in the root decisions so resume uses the current bundle. Its phase manifest
maps each phase to the exact artifact ID, path, revision, progress, accepted
commit, blocker and next action, without duplicating phase details. Adoption also records source revision,
imported paths, existing commit range and remaining phases.

Material human authority is quoted, not paraphrased: the user's outcome
statement and each answer that settles a material product question, with that
question, once, in Constraints or Decisions, in the original wording and
attributed to the actual speaker; the question is context, not user
authorization. A labeled gloss may
follow but never replaces or extends a quote; the Objective remains the
root's labeled synthesis. A dispatched planner receives these quotes, and
replacement overviews carry them unchanged; a later correction adds a new
quote naming the one it supersedes. Packets reach quotes through the overview
ID or `plan.md` and do not replay conversations.

Statuses are `active`, `blocked` (named blocker and next action; a
`user_preview` pause uses it) and `completed` (phases reviewed, verified and
committed; delivery authority stays separate). The root owns every update;
plan state never grants authority.

On resume, resolve the path again, reconcile checkout, identity, branch, base,
HEAD and commits with Git, then each phase by exact ID or path. Do not require
a clean worktree or a phase commit; preserve uncommitted unique work and
report Git and plan status. After reclaim in another thread or on another
provider, skip the previous thread's waits, dispatch fresh workers and keep the
plan's recorded flow assignment under its drift rule; permissions stay those
of the current chat. Git is authoritative for code and history; the plan only for
approved intent, bundle and progress. A missing or unreadable plan blocks
automatic continuation until reconstructed and realigned with the user.

Plan artifacts are immutable. A reversible in-scope clarification creates a
complete replacement phase and a manifest update; a material scope,
public-contract or user-visible change needs renewed approval. `completed`
freezes objective, acceptance and artifact selection; during authorized PR
review, an initiative's bounded joint-acceptance repair or "Base refresh
before delivery", an in-intent
correction advances a phase's terminal commit only through the phase path (or
the reviewed base-refresh merge), updating the manifest before pushing. A new
objective, behavior or material scope after `completed` or `hold` needs a new
task. Before delivery the
task head must equal the manifest's terminal commit. Between the last phase
commit and `completed`, run the "Durable knowledge checkpoint".

`Review context`, `Context maintenance paths` and `User preview` are sections
of the approved artifacts, not plan status. A validated context delta that
changes a future dependency, or a widened maintenance path, produces a
complete replacement for that phase.

### Task-private artifacts

Artifacts live only on the filesystem as UTF-8 Markdown in the task-private
directory returned by `task_state.py init`, normally
`<task-worktree>/.orchestra/artifacts`, named `<NN>-<kind>[-p<phase>].md`
with a zero-padded creation ordinal (for example `03-plan-phase-p2.md`). The file name
is the identifier packets and the manifest use. `task_state.py` creates a
self-ignored ownership marker, refuses tracked or unsafe collisions and proves
Git status unchanged, so publication needs no escalation. A legacy task keeps
its Git-private paths without migration or dual writes. If the directory cannot be written,
the agent returns the complete report inline.

An inline result that must survive task setup for a named consumer is copied
verbatim into the next matching artifact kind with its label and revision
(publication metadata identifies the producer without changing the report),
or kept inline when no kind fits; such copies follow the task-private
lifecycle, and a label alone is not a readable evidence
location. Root synthesis belongs in `Review context` or root decisions, never
in a producer's identity. An unrecoverable original is disclosed as missing
evidence, never reconstructed.

Role skills are self-contained; a packet never sends a role to WORKFLOW
sections. Every packet carries capability, explicit authority, worktree,
exact target artifact IDs and roles, stop conditions, current revision,
accepted finding IDs and only the new context delta; an implementation-review
packet also carries every context artifact the overview and phase require, or
each complete inline fallback with its label and revision. Initial repository
context also carries its minimum objective and focused questions. Later
agents read objective, scope, acceptance, verification and findings from the
named documents. A changed HEAD invalidates only affected evidence.

Load shared instructions once per context and read only the sections the
checkpoint needs; reread when the source changed or the context is gone. Consume delegated investigation rather than repeating it;
reopen source only for a named question or independent judgment, not to watch
progress. Reports keep enough evidence to establish their outcome and cite
prior evidence for unchanged facts; a delta report
names its prior report, revision, affected findings and new verification. Raw
logs and large tables stay in the evidence location. Every role report starts with
its status line and a `## Summary` of about 200 words, followed by
`## Details` with one `### <ID>` section per finding; the role returns the
status line, Summary and file name as its final message. The root consumes
that message and opens only the `### <ID>` sections a triage or decision
needs; a fix packet names the accepted IDs, whose sections the owner reads in
full.

Kinds are `repository-context`, `context-delta`, `plan-overview`,
`plan-phase`, `plan-review`, `implementation-report`, `verification-report`,
`implementation-review`, `debugging-report`, and `pr-review` only when PR
analysis has a downstream consumer. Corrected overview or phase documents
are complete immutable replacements, selected only by exact packet or manifest
IDs. Start, commit, push, check and
merge facts get no artifacts.

### Material context discovery and promotion

A delegated role that finds a material fact, inference or uncertainty absent
from its inputs records it in its report's optional `Context discoveries`
section only when it affects a named judgment in the current phase or a named
dependency of an identified later phase. Each entry has a report-local ID such as `CTX-001`
(globally `<artifact-identifier>#CTX-001`), evidence locator, inspected
revision, classification (`descriptive` current state, `normative` intended
behavior, or `uncertain` when the source's role cannot be established),
material impact, `Affected judgment`, and the named current-task consumer. Classification applies per claim. Agents omit incidental stale
information, never repeat unchanged context, turn guesses into facts, edit
earlier artifacts or claim authority. A discovery grants no authority and is
not an artifact kind or an entry in coordination or another state store; only
`repository_context`, performed by an `orchestra_analyst`, publishes a
`context-delta`.

At a stable handoff, never while an owner is mutating the worktree, the root
gives each material discovery one disposition, optionally after one bounded
`repository_context` confirmation of a consequential disputed claim when a
possible result could change
acceptance, a finding disposition, replanning or a persist:

- `route`: the report already gives sufficient evidence for a named
  current-task consumer; include the exact artifact and discovery ID (or the complete
  inline report and local ID) in the named consumer's packet;
- `replan`: replace the affected phase artifact and update the manifest;
  material scope, contract or user-visible changes need renewed approval;
- `persist`: canonical versioned human-readable product documentation goes
  through the current implementation owner, only for a confirmed
  `descriptive` claim at an exact path listed in `Context maintenance paths` (else `replan` within authority, or report the
  follow-up). Documentation states current behavior, commands and limits;
  verification evidence (dates, revisions, hashes, counts, runtime
  observations) stays in task artifacts and the handoff, so a code change never
  forces a documentation-only refresh. Normative `.agent/` conventions stay root-owned; descriptive
  recipes follow "Project verification". A `normative` or `uncertain`
  conflict is never rewritten to match code automatically; executable
  configuration, databases, generated and operational data remain normal
  implementation scope; or
- `discard`: duplicate, immaterial, disproven or unsupported, or an
  out-of-scope follow-up reported to the user.

Every reported discovery has a disposition before phase teardown; one without
an affected judgment and consumer is discarded without dispatch. Task-private
artifacts are not cross-task memory. A stale-context claim naming the exact
review judgment it undermines cannot be deferred into an `accepted` phase.

After an authorized documentation edit (owner `persist` or root `.agent/**`
write), the same owner reruns affected handoff checks and publishes a
replacement `implementation-report`, including any new literal hard-gate
command; a fresh delta review follows. Revalidate with
`repository_context` only when an unresolved factual question could change
acceptance or a finding; rerun a verifier only when its gate is affected. The
reviewer may still block when a named judgment depends on missing, stale or
conflicting context.

Publication failure returns the result inline without changing authority.
Successful managed delivery removes the worktree-local task state before the
task worktree; successful hybrid delivery removes it after restoring the
checkout.
Legacy tasks keep their Git-private cleanup path until they complete.

## Phase execution

Each phase has one outcome, allowed scope, acceptance criteria and
verification set. A phase-specific subplan exists only when the phase cannot
be safely delegated from the main plan.

The phase's `Verification` section separates `Implementation handoff checks`
from the `Independent verification gate`. The implementation owner runs every
required local deterministic check: affected tests, lint, type checks, builds,
validation commands and the canonical full suite when one exists, including
each applicable `.agent/` hard gate when configured, and fixes failures within scope before
handoff. An ordinary deterministic phase sets the independent
gate to `none`. A verifier is required only for browser interaction, owned
services or processes, mutable or stateful data, credentials, network or
another external environment, or explicit repository policy, where it
independently repeats the applicable gate. After an accepted
fix, rerun only affected checks unless the repository explicitly requires
another full gate. Configured delivery checks remain a separate final boundary.

Use shared "Behavioral verification" to select and assess tests. Each handoff
states the behavior or regression risk its changed tests demonstrate and any
concrete benefit of overlapping coverage. Changing test selection never
waives a repository gate.

Implementation and difficult debugging may escalate under the recovery ladder
in "Flow assignment"; acceptance, independent review, source-read-only
verification and delivery gates still apply.

1. The root selects one `orchestra_implementation_worker` with
   `general_implementation` or `frontend_implementation` as the phase's
   logical owner. One session covers the first handoff and preview
   absorption; every fix round is a fresh session of that owner whose packet
   carries the current revision and diff and the accepted findings with their
   evidence, started only after the previous session is confirmed closed, so
   there is never a second writer. The packet holds edit
   authority, worktree, `plan.md` path, exact overview and phase IDs,
   revision, accepted finding IDs, stop conditions and only new context. The
   worker reads scope, acceptance, verification and dependencies from those
   documents and only prior outputs the phase requires. A
   context-maintenance fix also carries the discovery ID, `persist`
   disposition, validating delta and exact maintenance path. While the worker
   is active the root waits: it handles user dialogue, resource coordination
   and root-owned setup that does not inspect or exercise the evolving
   implementation, and does not read the evolving diff, consume the
   worker's transcript as progress, run canaries against it or send design
   corrections.
2. At each stable handoff the worker publishes a complete
   `implementation-report` (or returns it inline). It cannot return
   `implemented` while a required check is failing, omitted without approved
   reason, stale, contradicted by its output or weakened to pass. For every
   check the report names the command and directory, evaluated revision and
   dirty paths, exit status and salient output, mapped acceptance or risk,
   tests changed and their coverage, permitted generated effects and cleanup, and
   residual risk.
   The root makes at most one bounded check of Git identity, status,
   allowed-path scope (exempting only its own authorized normative `.agent/`
   paths), `git diff --check` and the evidence inventory. For a
   `frontend_implementation` phase that changed a visible surface with preview
   `none`, that check also opens the cited screenshots, where the host renders
   images, and judges layout, states and coherence with the existing design; a
   material aesthetic defect becomes a finding, and missing screenshots block
   unless the report records why no runnable surface existed.
   When `plan.md` records a seed Decision, the root writes only the approved
   `.agent/**` seed paths at the first phase's stable handoff: owner delivers,
   root writes the seed, then independent gate, initial review and commit.
   Later `.agent/**` persists follow steps 5–7.
   A root investigation of a possible correctness defect is completed and
   confirmed against the current source and diff before it contacts the
   owner or pauses the phase cohort, then sent as one consolidated finding
   packet with evidence, impact and acceptance, never provisional or
   superseding directions. Returned discoveries get
   their disposition before routing a dependent consumer.
   Cleanup reporting is exception-based: no `cleanup`/`retained_resources`
   declaration means pass with nothing retained. Authorized non-browser
   retention stays in root memory until teardown; `partial` is non-blocking
   only for a source-read-only task tab or window; `blocked` stops downstream
   dispatch and gets one cleanup-only follow-up to the same owner, and a
   second failure blocks the phase.
   A `required` preview completes, with absorption, before the next step;
   never verify or review the pre-pause revision.
3. The root first validates the owner's evidence inventory, then starts the
   review in step 4. For a gate of
   `none` it creates no verifier; otherwise at most one verifier per
   applicable capability, passing the gate reason, overview, phase,
   implementation report, authority and revision. Each publishes a complete
   `verification-report`. The gate runs once, on the first revision whose
   review leaves no accepted open finding, because a run before review
   converges is repeated on the fixed revision; fix rounds before it rely on
   the owner's handoff checks and delta review. A failure goes to a fix round with its report and accepted finding IDs,
   without root-authored replay; after the fix's delta review the verifier
   reruns only the failed scenarios and those the fix affects. The
   verifier receives the revision as a commit SHA: `HEAD` when committed,
   otherwise a commit of the working tree that leaves branch and index
   untouched (`t=$(mktemp -u); GIT_INDEX_FILE=$t git read-tree HEAD &&
   GIT_INDEX_FILE=$t git add -A && git commit-tree $(GIT_INDEX_FILE=$t git
   write-tree) -p HEAD -m verify`). Verification copies are `git worktree add
   --detach` checkouts of that SHA; equal SHAs prove equal trees, so the
   packet names that SHA and the scenarios to run, with no file manifests or
   hash inventories.
   On `blocked`, the root decides whether the phase proceeds without that
   evidence and records the blocked reason in the phase evidence. While a stable revision is under verification the root does
   no speculative source review; it interrupts only for a changed revision or
   a finding confirmed against the exact current source and diff that
   invalidates that packet. Verifier
   discoveries stay in the verification report and get a disposition before
   use.
4. One reviewer receives the plan path with the relevant user and root
   decisions as authority, exact overview, phase, implementation and any
   verification IDs, every context artifact the overview and phase require,
   the cited screenshots for a visible change, and the exact `.agent/` seed
   paths when the commit will include root-authored `.agent/` files (that
   commit cannot close without their inspection). The delta review of a fix
   for a failed verification receives that `verification-report`.
   The reviewer inspects source and diff independently, judges approved
   intent before project guardrails and implementation evidence, and
   publishes a complete initial `implementation-review` with `Context basis`
   (only evidence actually consulted); fresh delta reviews under "Review
   policy" name the full-review base and prior dispositions and receive only
   new or replaced evidence rather than a replay of the full packet. It inspects source, diff, tests,
   evidence freshness and completeness, and does not rerun checks already
   evidenced; it may run the smallest local deterministic check that tests
   one concrete defect hypothesis and records that command and result in the
   `implementation-review`. Missing, stale,
   contradictory, incomplete or weakened required evidence is a finding or
   blocker. It opens full context only for a named `Review use` whose judgment depends
   on it, and returns
   `blocked` for missing or stale context only when that exact material
   judgment is named, after reporting independently resolvable findings.
5. The review and accepted finding IDs return to the same logical owner,
   except a root correction under finding triage; the root does not restate
   findings.
   Context discoveries follow "Material context discovery and promotion":
   confirm only when a result could change acceptance, a disposition,
   replanning or a needed persist; product documentation returns to the owner;
   normative `.agent/` policy stays root-authored; `normative` or `uncertain`
   conflicts are fixed as defects, replanned, reported or escalated, never
   rewritten to follow code.
6. After an authorized documentation or `.agent/` edit, the same owner reruns
   affected handoff checks and publishes a replacement `implementation-report`
   for that revision; a new or changed hard gate requires running its literal
   command. A fresh delta review follows. Apply the revalidation rule
   in "Material context discovery and promotion" without a second analysis
   cycle, and rerun a verifier only for an affected gate.
7. After final evidence is consumed and every discovery has a disposition,
   the reviewer must have an unblocked current context basis; a material
   unresolved, stale or conflicting basis blocks commit. The root then runs
   phase teardown.
8. When teardown permits, the root commits with direct Git or the exact-path
   helper and records the commit in the manifest. No commit artifact.

When the same causal failure repeats, corrections do not converge, scope
expands or evidence points to a deeper shared cause, stop blind retries and
choose: reassess the approach, dispatch
`difficult_debugging`, or ask the user at an authority boundary. Distinct
legitimate findings are not a trigger. An isolated Git failure stays with the
root: inspect status and the latest commit once, apply an obvious safe fix,
and never dispatch an agent merely to operate Git.

### User preview

User preview is an optional user inspection of a user-visible surface after a
phase's implementation handoff and before its independent verification and
review. It is not a flow row, role, plan status or artifact kind.

Offer it in the first message that reports the brief, without extra research,
when all three
hold: the result is a surface the user operates or looks at; the change is
material (a new or substantially changed screen or flow, not a string or
minor CSS tweak); and a local run recipe is known or trivially inferable.
Silence is `none`. A conversational `interactive` /
`interactivo` (or an equivalent in the chat language) that clearly means this
pause is `required`; if it might mean
the product is interactive, disambiguate once in that message. Never offer it
for API, schema, worker, CI, migration or library-only work, and do not
re-ask.

Record the task-level choice as a Decision before planning; plan approval
confirms the per-phase mapping. Each `plan-phase` carries `User preview:
required | none`, `required` only when the task Decision is `required`, the
phase has a user-visible surface and it names an executable local recipe.
Preview does not force a phase split. Changing preview on an unstarted phase
uses a replacement phase artifact; during any pause the user may skip the
remaining previews, and unstarted `required` phases become `none` the same
way.

After an `implemented` handoff with green required checks on a `required`
phase:

1. Keep only resources needed to show the result. The owning chat may start
   or retain a task-owned local preview process when the packet permits; the root
   records it and cleans it at completion or cancellation. Browser tabs follow
   the selected route and cleanup contract.
2. Set `plan.md` to `blocked` with blocker `user_preview` and next action user
   inspection.
3. Give the owning chat a preview pack: worktree, task branch, how to run or
   show the surface, allowed paths, a short visible-result summary and cited
   screenshots. The user may iterate the approved scope in this conversation; no new chat
   or manual process start is required.
   Git and the `implementation-report` remain truth; no preview artifact.
4. Wait with the provider's question tool for iterate, freeze as-is, or skip. Iteration
   stays uncommitted on the task branch unless the user authorized a commit;
   out-of-scope paths or new behavior block or replan.

Never auto-continue if the user does not return; mention that hybrid preview
can occupy the primary checkout for a long time when recommending it.

After freeze or skip, resume in the owning chat or reclaim (which abandons the
previous chat). Keep the logical owner and exact artifacts; spawn a
replacement with the same packet only after confirmed closure or
unavailability. In-scope uncommitted and untracked edits are the delta;
recommend against user commits, and record any new branch commits as
authorized preexisting changes for absorption. The absorbing owner reruns
handoff checks and publishes a replacement `implementation-report`, then the
pause repeats until the user explicitly confirms, freezes or skips; the root
never infers that exit. Dispatch the independent gate and review once,
against the frozen post-absorption revision with green checks.

The review packet states that the user accepted the visible result at that
revision: taste findings are out of scope; bugs, accessibility, regressions
and defect-prone complexity remain in scope, and a defect forcing a visual
change enables a short re-inspection. Preview never replaces
`browser_acceptance` or waives hard gates. After `completed`,
further taste work is a PR-fix inside approved intent or a new task.

### Phase teardown

The root keeps only an in-memory list of the agents and temporary resources it
created or permitted for the current phase. Every agent closes its own
servers, processes, terminal sessions and task tabs before a final, failed
or blocked handoff by default. Analysts and reviewers retain nothing. Implementation owners and
verifiers stay open through the phase to reuse context, not tools; they
recreate resources unless the packet authorizes retaining an exact
non-browser category. Browser tabs are never retained across a handoff.
Activity rows are observability snapshots, not resource handles.

Teardown is proportional. For an edit-only phase (no declared retention,
`partial` or `blocked`, no processes, services or browser work) the root
retires the cohort and commits. Otherwise, after
review and verification pass and before commit, it sends one parallel
cleanup-only follow-up to the owners of those declarations, stops shared
temporary processes it started, consumes the results, retires every phase
agent once its `delegate_task` result has returned with no retained
resource, and confirms that no agent or owned process with
worktree write access remains.

An active write-capable agent or owned process blocks the commit. A
source-read-only browser tab that failed to close is partial cleanup and does
not invalidate evidence or the commit. Orchestra never scans for or kills
unrelated processes, closes unrelated tabs or sessions, persists a resource
registry, or adds cleanup to the commit helper; the root stops only its own
resources or an exact safely addressable handle reported by the owner. Best-effort activity
clearing runs after teardown and never affects the commit.

### Test permissions and browser routing

Orchestra observes T3's runtime mode and each provider's permission choice; it
never changes them or blocks because they differ. A command that crosses a
protected boundary is issued once, and its prompt or denial is respected; never
retry a denial through a workaround or broaden permissions. Syntax, type,
compile, lint, import, assertion, validation-contract and CLI-usage failures
are real failures. A missing external service, credential or dependency may
return `blocked` but never broadens authority.

Packets for `frontend_implementation` browser work and `browser_acceptance`
carry `browser_route: auto | in_app | chrome | codex-cu`. Without a
user-selected route, the root uses the one-line user setting
`${ORCHESTRA_HOME:-$HOME/.orchestra}/browser-route`, else `auto`; no
installation writes or removes that setting.

- `auto`: T3's collaborative browser through its `preview_*` tools. When it is
  unavailable, including a `preview_open` sandbox or setup error, a Claude
  child started with `--chrome` uses Claude in Chrome and any other child uses
  `codex-cu`.
- `in_app`: T3's browser only.
- `chrome`: Claude in Chrome only, for a Claude child started with `--chrome`;
  otherwise `blocked`.
- `codex-cu`: the codex-cu MCP, Codex's computer-use engine driving Chrome. It
  is `blocked` when the server, the ChatGPT app or its Chrome extension is
  unavailable; because it cannot write files, copy each screenshot from the
  path its result reports and convert it to the required PNG evidence path.
  The optional server is
  [codex-cu](https://github.com/FranciscoJSBarragan/codex-cu-mcp).

The browser acceptance playbook defines the tab steps, and User preview never
replaces a blocked gate.

An explicit user route, relayed or given directly, must be attempted even as
a canary for a previously failing tool, and stays fixed without fallback. An
agent may return the route's technical blocker but never veto or substitute
it. Functional failures, application timeouts and selector problems never
cause a switch. On an allowed `auto` fallback, capture the first surface's
blocker, close any task-owned tab on it, open a new task tab on the fallback
surface and repeat the complete scenario, so evidence from different surfaces
is never combined; if both are unavailable, return `blocked`. Other computer
use, standalone browser automation and other browsers are not substitutes for
these routes.

Every visual interaction or acceptance run opens a fresh task-owned tab on
its surface, never a user tab or an earlier run's tab, and closes that exact
tab before every handoff; fixes and reruns open a new one. Browser handoffs
also stop their owned supporting processes and report `retained_resources:
none`. Frontend iteration and independent acceptance use separate tabs and
evidence. Orchestra preserves unrelated tabs, sessions, windows and browser
state and never closes Chrome or a shared window.

Every `browser_acceptance` run that reached a visible page writes PNG
screenshots into the task artifacts directory as
`<NN>-verification-report-shot-<k>.png` and cites them in the
`verification-report`; passed, failed and blocked runs cite at least the last
useful shot, and missing screenshots after a visible page make the evidence
incomplete. A `frontend_implementation` run that used the browser for visual iteration
writes
`<NN>-implementation-report-shot-<k>.png` the same way; a phase that never
opened the browser invents none. These files are evidence referenced by the
report, not an artifact kind. The root opens the cited paths when consuming
the report.

## Review policy

Every phase is accepted only after one current independent code review of its
exact revision, never on implementation checks alone; local integration and PR
delivery also need an independent review of the exact terminal revision before
their mutation or clean result: a single-phase task's phase review of that
revision is that review, and a multi-phase task gets one baseline review of the
complete range whose packet carries no earlier review. The first review covers
the whole bounded target and returns all known material findings; later reviews
inspect only the meaningful delta and interactions affected by accepted fixes,
because each fresh full review finds a different subset and never converges.

The review that first covers the complete terminal range runs as a pair, the
`independent_review` row and the flow's `review_pair`, in parallel on the same
packet and blind to each other. The root merges their findings by defect, and
one reviewer's dismissal never cancels the other's finding. Every other review
uses the `independent_review` row alone.

A reviewer is never resumed. Each delta round dispatches fresh reviewers, both
of the pair when the pair ran, whose packet carries the full-review base, prior
dispositions and only the meaningful delta.

How to review (counterexamples first, what counts as a finding, the scope of
exclusions, `Dismissed counterexamples` and the report) is defined only by the
reviewer role skill, which no packet can omit or narrow. A review packet names
the target, revision, producer evidence to read in full, quoted user outcome,
artifacts directory, accepted finding IDs and any exclusions. Author concerns in a packet are
non-exhaustive prompts, never the agenda or a narrower scope. The root uses
`Dismissed counterexamples` at approval under the planning stage.

The root may add a second plan or decision reviewer (`independent_review`)
only for a named measurable risk whose defect class it detects independently,
for example omissions in indirect consumers or pending external actions,
recorded in the plan risks or decisions. It gets the same intent, candidate
and producer evidence, never narrows the first review or duplicates a gate
under "Engineering guidance and evidence", may run in parallel with a distinct
publication target, and corrections get fresh delta reviews.

Implementation review follows approved user intent, material project
guardrails, current source and diff, and verification evidence, in that order;
no packet reorders it or exempts an accepted mechanism. Authority-based
dispositions follow "Decision evidence"; phase acceptance does not establish
that an unpresented consequence was authorized. A review discovery or blocker
names the affected judgment and current-task consumer.
Incidental stale information is omitted. A stale descriptive fact becomes a
documentation correction only after decision-changing independent validation;
normative intent is never rewritten to match current implementation.

The root triages every finding, from its reviewers and PR feedback alike,
before any fix, as the root skill's `finding triage` reference defines,
re-reading it at each triage; a finding is not fixed because it was reported.

The root alone sees every round, so it stops patching when the third review
round of a plan, a phase or a PR still has findings, the second independent
verification of a phase fails, a run in a scarce environment (hardware, a
limited or costly session) fails, or a finding lands in machinery an earlier
correction added. Replanning a phase does not reset these counts. It compares
the change's size with the problem and seeks a simpler design that removes the
failure class; when the outcome admits unbounded failures, such as timing,
availability or hardware behavior only a run can show, it narrows the failure
model or acceptance with the parent or user before another round or run.

### Mechanical release metadata

After reviewed implementation and its authorized delivery, the root may prepare
a separately authorized release's mechanical version and changelog updates
without dispatching another independent reviewer. Inspect the exact delta,
derive notes from the released Git range, and use the existing release tooling
to validate version, tag, changelog and packaging consistency. Preserve all
repository-required checks and any explicitly required release review; do not
infer a full-suite exemption from this review exception.

This lane covers only version identifiers and accurate release notes. Changes
to executable behavior, dependencies, build/release logic, migrations, security
or compatibility need the normal implementation review. Unresolved semantic
versioning or compatibility claims require evidence or a focused review, not a
mechanical-pass label. This is not a new phase, delivery authority, or permission
to replace the completed plan's terminal revision with an unreviewed commit.

## Task checkout and branch

A formal task normally uses a fresh `orchestra/<task-slug>[-N]` branch, created
immediately after specification confirmation; only read-only preflight and
pre-checkout context precede it. Neither mode ever implements on the starting
branch or on `main`.

The `${ORCHESTRA_HOME:-$HOME/.orchestra}/checkout-mode` user setting selects
`managed` (default) or opt-in `hybrid`; an explicit task direction overrides it
and is recorded in the plan. Loading a plugin creates no settings file. Managed
mode uses a dedicated worktree below `ORCHESTRA_WORKTREE_ROOT`, the
`${ORCHESTRA_HOME:-$HOME/.orchestra}/worktree-root` setting, or
`$HOME/.orchestra/worktrees`, in that order, created through T3 as
`host_t3.md` defines. Hybrid mode creates the task
branch from the exact captured HEAD of the current clean primary checkout or
linked worktree.

For a fresh task on the canonical base, resolve and fetch its configured
upstream and compare commits. Managed mode creates from the fetched upstream
without updating the local base. Hybrid mode proceeds when equal,
fast-forwards a strictly behind clean base with `git merge --ff-only
<upstream>`, and blocks for a user decision when ahead or diverged. A failed
upstream fetch blocks; with no remote or upstream, proceed from the local base
only when identified as not remotely verified. Never `git pull`, create an
implicit merge or rebase the base. An explicitly selected noncanonical base
stays at its captured commit (stacking stays possible), but a PR-required task
must first prove it remotely usable.

Initiative child checkouts follow "Child root setup".

Exactly one owner creates or adopts the checkout, recorded with the branch in
plan Decisions; never create a redundant worktree. Before the first dispatch
into it, write and remove one canary file there (creating the managed
repository directory first); failure blocks with exact path and environment
evidence. A failed `git worktree add` gets one inspection of branch, path and
error, then blocks. Active tasks outside the configured root are not migrated.

The root keeps checkout mode and path, starting branch and HEAD, task branch,
resource ownership, base and revision, and authorized preexisting changes in
transient context, with no classifier or registry. Fresh tasks start at the
intended committed base; adopted committed work starts at the source HEAD and
keeps the integration base. Scoped dirty adoption imports selected
non-ignored paths through `adopt_worktree.py` (content may stay unstaged);
ambiguous dirty ownership blocks.

Reuse is allowed only for the same live pre-approval task, or when plan,
objective, checkout mode and path, starting identity, task branch, base and
HEAD all identify the same resumed task; missing or conflicting identity
blocks. A legacy plan with a retired environment field blocks automatic resume
unless it already identifies the exact sibling worktree and the user
authorizes adoption.

After authorized integration or merge, managed cleanup removes the
worktree-local `.orchestra/` state, then the clean worktree and safe branches;
hybrid cleanup restores the unchanged starting branch, keeps the user's
checkout and removes only the guarded task branch and its state. Hold and an
open PR retain checkout and branch. For a host-owned managed checkout, pass
`--preserve-task-resources` to `pr.py merge` or `integrate_local.py`: it keeps
worktree and evidence for host release with no policy, review, freshness or
check waiver; PR delivery still attempts guarded remote-branch cleanup and
reports moved or inaccessible refs, and the helper reports verified delivery
with `partial` cleanup and `retained_resources`. The parent records
the local ref, delivered SHA and cleanup owner and, after release, removes only
an unchanged reviewed ref without rerunning delivery, keeping preserved
evidence accessible until it no longer needs it. Pre-approval
cancellation uses the state helper, removes only proven-clean resources and
never recursively deletes an unrecognized directory.
Dirty, moved, ambiguous or unverified resources are never removed; cleanup
after a completed mutation reports `partial` for them. Orchestra never runs
`git clean -x`; if a user's clean removes `.orchestra/`, the missing plan
blocks automatic resume.

## Agent waiting

Apply "Conversation continuity" to user messages and worker updates received
while waiting. An intermediate message does not terminate the assignment.

Dispatch roles with `delegate_task` in `async` mode and end the turn: T3's
completion notification wakes the root, which reads the result once with
`task_status`. Wait on a thread with one long `t3_thread_wait`. Completion or
error must return immediately, including before any status inspection. A timeout only means the wait ended, not that work failed.
Do not replace an event-aware wait with unconditional sleeps or a chain of
model turns whose only purpose is deciding to sleep again. If the host supports
only short waits, continue on the same handle without extra Git/log inspection
or unchanged narration; do not invent a background-notification API.

Independent roles may run in one parallel batch. A task root returns a stable accepted result or precise blocker, never completion while
required descendants remain active. Ending a turn alone proves neither lost nor
completed work. Resume only a confirmed completed/stopped owner, preserving its
handle; progress messages do not justify relaunch or another writer.

If manual status inspection is necessary, allow at least five minutes after
dispatch and between inspections; these intervals limit unsolicited polling,
never delay an available completion, error or answer to the user. Apply the
mutable-implementation boundary from `Phase execution` to active implementers in both phase and
standalone assignments.

After 30 accumulated minutes, the root may assess once for a concrete blocker;
a reported error, unavailable process, or known stuck command can justify an
earlier targeted diagnosis. Inspect only the needed process state or bounded
diagnostic tail, without dumping full process arguments or event history. The
owning worker should resolve a stalled command within its assignment. If a
child cannot receive a message while running, do not pretend otherwise:
first reconcile the current invocation and its resources, then resume its exact
session with the focused blocker when necessary. Never replay a mutating prompt.
Stop only the identified owned resource when justified; elapsed time or silence
alone never authorizes cancellation, escalation, or a replacement worker.

A normal timeout is not a user-visible transition. Report a material result,
blocker or decision, and answer explicit status requests, without repeating
unchanged progress.

## Commit path

Plan approval covers commits at successful phase boundaries. Commit execution
is a root responsibility, not an agent profile or capability. The default path
is one direct pass: inspect status and the relevant diff, stage only the accepted
paths, create a file-based commit with a concise title plus useful intent and
validation, then read the resulting SHA and status once. Do not require empty
ceremonial sections, byte-for-byte message equality, repeated authority checks,
or an agent dispatch.

The optional narrow helper exists only when exact-path staging is useful. It
refuses active merge, cherry-pick, revert, sequencer or rebase operations before
staging, preserves unrelated work, rejects staged paths outside the accepted scope,
commits the selected paths, and verifies that any created commit contains no
other paths. A legitimate commit-message hook may add trailers. If Git created
the intended commit, its SHA is success evidence even when an auxiliary command
reported a failure; do not retry, amend, or manufacture another commit.

Git provides atomic commit and reflog behavior. Local commits do not require an
isolated index, crash journal, authority bundle, or repeated subprocess
validation.

Phase-agent and temporary-resource teardown is complete before this path starts;
it is not part of direct Git or `commit_phase.py`.

## Base refresh before delivery

When a pending task's base moves, the parent sends its existing root the actual
authorized target's full SHA, expected task HEAD, affected dependencies and
unchanged authority. Local delivery uses the authorized local base, including
legitimate local commits ahead of origin; PR delivery uses the relevant remote
base. Ancestry or equal trees only classify candidates: reconcile acceptance and
actual delivery before replay or declaring success. Proven delivery with missing
reporting needs recovery, not another integration. Repairs after delivery use a
new bounded task. Serialize deliveries to each base; external writers still
require a final base recheck and refreshed affected evidence when it moves.

This continuation covers managed/host-supplied isolated tasks. Do not overwrite
hybrid's captured `start_revision` guard or silently change checkout mode. Resolve
that unsupported stale-base case explicitly. Refresh stays within existing scope
and delivery grants, including the base-publication check in "Task checkout and
branch"; it is not permission to push, force-push, rebase or merge the task into
its base. Product/security/public-contract expansion remains a question.

For full Orchestra, the task owner incorporates the exact target with
`git merge --no-commit --no-ff <target-sha>` after reconciling a clean task HEAD.
If `MERGE_HEAD` already exists, reconcile it with the requested target and preserve
unique resolutions before resuming. Never auto-stash, reset or abort such work.
Resolve textual conflicts and semantic interactions in the owning child, not the
parent. Separate imported upstream paths/range from child-authored resolution or
compatibility paths. A combined tree equal to the target can indicate lost task
behavior as well as prior delivery; reconcile original acceptance before a no-op
or empty merge, and never infer a squash delivery from equality alone.

Use existing replacement implementation-report and delta implementation-review
(or PR-review) artifacts. Identify the frozen result by old task HEAD, exact
`MERGE_HEAD` and `git write-tree` index SHA, with no unmerged paths or unrecorded
source edits. Run applicable required checks and independent delta review of the
task against the target plus changed interactions, even after a textually clean
merge. Reuse unaffected prior evidence when still valid. The root must not replace independent review with conflict resolution.

Commit the accepted merge directly with Git and normal hooks, without a pathspec;
`commit_phase.py` deliberately refuses this operation. Verify exact parents,
accepted tree and relevant checkout cleanliness after hooks. Compared with the old
task HEAD, no unexpected path may lie outside imported paths plus authorized
resolution/compatibility paths; these sets need not be equal. A changed tree or
hook-generated source edit invalidates acceptance: preserve the created commit and
work, return to its owner for reconciliation, and never automatically amend/reset
or retry the commit. Update the completed plan's terminal revision only after the
accepted commit under its bounded correction exception. Normal delivery then uses
that exact SHA, fresh configured checks and its existing policy; local integration
remains fast-forward. Recheck the base before delivery and return affected work to
the same child if it moved. Escalate actual unresolved scope or sustained contention,
not an arbitrary retry count.

## Repository conventions

A consumer repository may keep tracked `.agent/` knowledge. Distinguish three
kinds by meaning, not just directory: normative operating policy; descriptive
setup/verification instructions; and per-run evidence. The last belongs to task
reports, not durable `.agent/` knowledge. Reuse existing canonical contributor,
test or product docs rather than duplicate them. `orchestra.toml` remains the
source of delivery argv; host `AGENTS.md` and task-private `.orchestra/` have
their existing responsibilities.

Normative topic files use the established taxonomy where relevant: scope, hard
gates with exact argv/cwd, diagnostics, forbidden substitutions, opt-in gates,
prerequisites and conventions. No empty stubs or closed file enum. A convention
records a non-obvious intended constraint or failure it prevents, not general
engineering advice or a linter's defaults. A hard gate names a literal command.
New or changed policy requires user confirmation unless the current approved
scope already authorizes that exact policy change. Descriptive operational
recipes use "Project verification" and may be maintained by their authorized
implementation owner; they do not need to masquerade as hard gates.

Lookup reads relevant `.agent/` entries, applicable `AGENTS.md`, maintained docs,
Makefile/CI/manifests and `orchestra.toml`. Packets cite exact paths instead of
pasting bodies. Formal plans name task-relevant conventions in `Review context`
and copy literal mandatory commands into handoff checks. Applicable repository
instructions remain binding independently of packet citation. Conflicting
normative sources are an authority question; current implementation never
silently wins. Stale descriptive setup can be corrected from observed evidence
within scope, without changing what the product is expected to do.

After first `repository_context`, absence of normative project conventions is
one consolidated question with specification confirmation: offer only a useful,
evidence-backed seed or the explicit `orchestra-repo-readiness` route. A directory
containing only operational recipes does not establish normative policy.
If the user declines, infer and cite existing instructions/checks for this task;
do not repeatedly interrupt the same task or require an empty store. Greenfield
work may already have authorized operational recipes; the first full Orchestra
plan includes only any still-needed normative seed Decision and exact paths.

Normative seed writes remain root-owned at the approved phase's stable handoff,
before independent review and commit, never before plan approval. The root's
exact authorized policy paths are the allowed-path exception; implementers may
own explicitly scoped descriptive verification entries. Readiness first reads
and proposes policy, then uses its existing confirmation boundary. That same
confirmation may authorize bounded recipe execution and helpers; it is not
product-feature or production authority. All meaningful knowledge changes use
the affected checks and review under "Material context discovery and promotion".
Discovery alone grants no authority. Delivery checks remain in `orchestra.toml`.

## Durable knowledge checkpoint

For the final implementation phase, after its required verification and
independent review pass and before phase teardown retires owners or the phase is
committed, the root judges once whether the task produced knowledge of this
repository that a later task would otherwise have to rediscover at cost: a
convention the work had to infer, a verified operational lesson (a failing
setup, its cause, and the proven recovery), or a hard gate or prerequisite the
store did not name. For a genuinely blocked task, make the same judgment at the
blocking boundary. Sources are phase reports, discoveries already dispositioned
`discard` as out-of-scope, and the root's own observations; the root does not
dispatch an agent to search for candidates.

For a recurring failure already evidenced by the task, apply shared engineering
guidance "Prevent recurring failures" to choose a proportionate prevention
mechanism from the verified cause. The same criterion is available to ordinary,
maintenance work without this final-phase checkpoint. This judgment adds
no reflection stage or transcript-mining job; the only retrospective is the
initiative parent's under "Initiative coordination". The checkpoint's writes remain
limited to the repository knowledge below; code, routing, or Orchestra-policy
changes use normal implementation scope and review when already authorized,
otherwise become bounded follow-up proposals without delaying delivery. Agents
never gain authority to rewrite their own skills or policies from a failure.

Keep the implementation owner and reviewer available until any authorized
knowledge correction, affected checks, and delta review
finish. The destination is the existing canonical repository documentation
or an exact `.agent/` path under "Repository conventions"; do not create a
second copy of already maintained knowledge.
A candidate qualifies only when it is verified against the current revision,
non-obvious, not already represented in `.agent/`, `AGENTS.md`, source, or
canonical documentation, and not task progress, approvals, branch state,
secrets, or a user preference. Anything that fails that test is dropped in
silence; the checkpoint is never mentioned to the user when nothing qualifies.

A qualifying descriptive correction persists through its authorized owner and
exact documentation scope under the `persist` rules. A qualifying normative addition is new policy: the root names
the exact path and one-line content in the same consolidated final request
that carries the delivery decision, never as a separate turn, and writes it
only on confirmation. Either write follows the documented order (authorized owner write,
affected checks, fresh delta review, phase
commit); that commit becomes the terminal commit before `completed`. The
checkpoint never reopens scope, adds product behavior, or blocks delivery when
the user declines. Once the terminal phase commit is accepted, setting
`plan.md` to `completed` records the result; the checkpoint is not deferred until
after owners close.

## Delivery policy

A consumer repository stores an explicit delivery policy. When it is missing,
Orchestra asks the user once and recommends `hybrid`. It does not infer
permission from existing PRs, CI workflows, or branch history.

`orchestra.toml` contains only the delivery mode and ordered verification checks
as argument arrays. PR merge and local integration share that check runner;
commands never pass through a shell.

Supported policy modes:

- `pr-required`: final integration goes through a PR.
- `hybrid`: the user chooses local integration or PR per task.
- `local-direct`: local integration is permitted when explicitly requested.

## PR path

The unchanged public PR skills preserve the proven behavioral chain:

1. PR-open reads the complete branch commit range and diff, publishes the
   intended branch, and verifies the remote head and PR body after creation or
   update.
2. The root synthesizes and publishes a compact `PR-CONTEXT` capsule.
3. The root calls the narrow PR helper directly to observe every relevant
   GitHub/CI feedback surface: review bodies, issue comments, complete review
   threads, checks, review decision, merge state, and current head. It never
   relies on only the last thread comment.
4. The root triages actionable feedback under "Review policy" against
   PR-CONTEXT and current code, and dispatches a reviewer only for feedback
   whose validity needs investigation; status-only bodies need none, but a
   bot status reporting its review of the current head still in progress
   counts as a pending check until it completes. A PR
   cannot become clean without the terminal review "Review policy" requires.
   The root keeps revision-scoped dispositions in memory for the current
   observation and never persists a feedback ledger.
5. A fresh session of the implementation owner, or the root for a root
   correction under finding triage, applies accepted fixes, reruns the checks
   they affect, and publishes a replacement `implementation-report`; only an
   affected independent gate reruns, with the same verifier. The pushed
   head's PR checks and the merge helper's configured checks remain the full
   gate. A fresh delta review evaluates the meaningful delta and
   replacement evidence, producing the current accepted `pr-review`. The root
   commits with that current review and only the `verification-report` evidence
   required by the relevant gate, updates the affected phase's terminal
   manifest commit, and pushes.
6. The loop continues until one complete observation of the current head is
   clean; the merge helper observes again before and after its checks.
   Between observations the task root waits on T3's pull request watcher as
   `host_t3.md` defines, never by polling or by ending its turn with checks or
   review bots still pending.

GitHub remains the external truth. PR-CONTEXT lives only as one upserted capsule
in the PR body. The helper reports current checks and review-thread evidence; it
does not interpret feedback, fix code, route work, or persist state. The root
evaluates unresolved, non-outdated threads and supplemental review/issue comments and returns accepted findings
to the same implementation owner by stable finding or GitHub reference. Publish
`pr-review` only when an agent's semantic analysis must be consumed downstream;
do not duplicate check, push, thread, or merge state as artifacts.

`Open a PR` authorizes opening, review processing, fixes, commits, and pushes
needed to make that PR clean. It does not authorize merge unless the user said
`merge when clean` or separately requests merge later.

After an authorized merge, the PR helper verifies the `MERGED` state against the
exact reviewed head and performs conservative cleanup. The merge command itself
uses `--match-head-commit` to reject a concurrent head change. It uses lease-protected
deletion for an unchanged remote task branch and expected-value guards for local
resources. Managed mode removes its task worktree; hybrid mode restores the
starting branch and preserves the checkout. This exact
merged-head proof permits cleanup after merge, squash, or rebase without
pretending that all three preserve commit ancestry. An absent remote branch is
already clean; a moved branch is retained.

## Local integration path

Local integration is a direct alternative, not a degraded PR path. It requires:

- policy permission;
- explicit task-level user direction;
- clean task scope, a current independent code review of the terminal revision,
  and fresh complete configured checks;
- integration into the intended base without rewriting unrelated history;
- confirmation of the result;
- mode-aware checkout and merged-branch cleanup.

The mechanical path runs every configured check in the clean task checkout and
requires the independent review result for the same terminal revision. It permits
only conservative fast-forward integration, and verifies that the base contains
the captured task SHA. Before those checks, it requires the task HEAD to equal
the terminal commit supplied from the completed plan manifest. Managed mode
removes its still-clean worktree and branch;
hybrid mode restores and fast-forwards the unchanged starting branch, preserves
the checkout, and deletes only the fully merged task branch. Divergence returns
to the root for resolution.

It does not authorize release, deployment, or production mutation.

## Migrations at delivery

Migrations change databases outside Git, so delivery checks them. Before
delivery they run only on databases the task owns or can discard. Before merge
or local integration, confirm the task's migrations still apply in order on the
current base: no migration merged since the task started reuses their version
or opens a second head. After verified delivery of a range that adds
migrations, run the repository's migration status command for each environment
its conventions name, and apply pending migrations only where those conventions
let an agent apply them. Everywhere else, including interactive confirmations
and production, the completion handoff lists each environment's pending
migrations with the exact command as the next step needing authority. When
conventions name no status command or environment, it lists the delivered
migration files and asks where they apply.

## Maturity

Automated checks and representative canaries provide evidence. T3 Code is the
approved execution host; a Hermes thread there acts only as the parent under
"Hermes dispatcher". Any other host remains deferred.

## User-facing progress and handoff

Report only material phase transitions, findings or decisions, blockers, fresh
verification results and authority requests. Each update states current state,
user-visible result or evidence, and next action. Describe behavior and
decisions; mention process facts (model assignment, checkout, branch,
registration, service stacks, agent plumbing) only when they need a user
decision, block progress, or another rule requires their disclosure
(completion handoff, unverified base, skipped registration, resume status,
partial cleanup). At completion, distinguish implementation-complete
from delivered and state the result location, how to run or demonstrate it,
verification performed, safe test data, limitations, exact delivery state and
the next authority needed. A task that delivers a case marks its case-list
line ready to try with the delivery link and asks the user to try it; only the
user's confirmation marks it done. Name a task by its repository and human
title.

Explanations distinguish verified facts, supported inference and uncertainty,
and use an available visualization only when a complex sequence, hierarchy,
comparison or mapping becomes materially clearer; an unavailable capability
never blocks. Delegated agents report to the root and create no user-facing
visualizations.

A question required to continue uses the provider's question tool
(`AskUserQuestion` in Claude Code, `request_user_input` without
`autoResolutionMs` in Codex) when available, so the T3 thread shows that it
waits, and stays open until the user answers; a task root launched by a parent
sends the question to that parent instead. Stop watching a pull request before
asking. If the tool is unavailable or returns no usable selection, ask one concise
plain-text question in the final response and wait, without retrying the
selector. Automatic resolution is only for informational, non-blocking
questions whose timeout can safely accept the recommended default. This does
not change command, test or host-wait timeouts.
