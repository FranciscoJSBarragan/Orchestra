# Capy host

Capy is the host when the session has Capy's tools (`message_agent`,
`tools.subagent.create`, `tools.pr.create`). Capy's own instructions already
define threads, subagents, pull requests, wakes and reviews; this reference
maps WORKFLOW "Host" onto them and states only where Orchestra departs from
Capy's defaults. Specification, planning, review policy, commits and delivery
follow WORKFLOW.

## Primitives

| Primitive | Capy |
| --- | --- |
| `launch_task_root` | `tools.thread.create` from a Captain; a thread that invokes Orchestra itself is a root |
| `report_to_parent` | `message_agent` without a target, as a needs_you or final report |
| `dispatch_role` | `tools.subagent.create` and `tools.subagent.start` on the shared machine; the final report wakes the root |
| `continue_session` | `message_agent` to the subagent's path; its next final report wakes the root |
| `model_catalog` | The subagent model list in the session's context |
| `task_checkout` | The thread's own checkout, in hybrid mode |
| `watch_pr` | The watch `tools.pr.create` registers, then `end_turn` |
| `browser_surface` | `tools.capy.browser` on the shared machine |
| `user_preview` | `tools.expose.port`, revoked with `tools.unpublish.port` |
| `ask_user` | `message_user` as needs_you, or `clarify_questions` |
| `permissions` | No permission mode; Capy's platform rules apply |
| `dispatcher_parent` | A Captain |

## Runtime

The Capy bundle (`package_plugin.py --target capy`) installs into the root of
one Drive location with the update command in its `README.md`: each skill
lands at `skills/<name>/SKILL.md`, where Capy discovers it, and
`.codex-plugin/plugin.json`, `WORKFLOW.md`, `flow.toml` and `scripts/` sit
beside `skills/`, so [runtime resources](../runtime.md) resolve a plugin root
under `~/.capy/drive/<location>/`. Use the Captain's Drive when a Captain
launches task roots, otherwise the person's own Drive. Every crew thread mounts
its Captain's Drive, and subagents on the root's machine read it by the same
absolute paths. Capy reads only a skill's name and description, so
explicit-only skills rely on their descriptions.

A cloud machine's home is neither shared between threads nor kept when Capy
rebuilds the machine. Keep settings and the user's `flow.toml` in the same
Drive's `orchestra-home/` and set `ORCHESTRA_HOME` to that path in every
shell call that runs a helper or reads settings, unless the project sets
`ORCHESTRA_HOME`.

## Flow rows

The flow keeps its provider ids. Map each row to one Capy model id and check it
against the subagent model list in your context, which is the live catalog;
organization policy may still refuse a model at start and names the permitted
alternatives.

| Flow `provider` | Capy model id | Billing route |
| --- | --- | --- |
| `claudeAgent` | `claude-code/<model>` | Claude plan |
| `codex` | `openai/<model>` | Codex plan |
| `cursor`, `grok` | `xai/<model>` | the route the catalog names |

`effort` passes unchanged as `reasoning_mode`. [Model notes](model_notes.md)
apply by family: every `openai/gpt-*` model, Terra included, takes the GPT
lines. A missing id or effort blocks under WORKFLOW "Flow assignment". A
different billing route for the same model (for example `anthropic/` on Capy
credits instead of `claude-code/`) is a substitution that needs the user's
choice. `tools.subagent.get` reports the model that ran; that is observed
evidence, the effort is requested only.

## Checkout

The project checkout at the thread's workspace root belongs to that thread.
Use hybrid semantics there: create `orchestra/<task-slug>` from the fetched
upstream in that checkout and record the mode in plan Decisions. Hybrid rules
still apply: fetch, compare the captured HEAD with upstream, fast-forward a
strictly behind clean base, and block when ahead or diverged. No managed
worktree, handoff or `--preserve-task-resources` is needed.

Where `/usr/bin/git` is Capy's wrapper that writes
`$HOME/.capy/git-shim.log` (the real binary is then `/usr/bin/git.real`), a
repository test that asserts nothing is written under a temporary `HOME` can
fail for that reason alone, also on the base. Run the repository's hard gate
once in preflight; if it fails only that way, run every gate with a directory
holding a `git -> /usr/bin/git.real` symlink first on `PATH`, record that
environment fix in plan Decisions and pass it in every packet that runs the
gate. GitHub CI stays the shim-free evidence.

Unpushed commits and `.orchestra/` are lost when Capy rebuilds the machine.
Ask for the task-branch push grant with specification confirmation; once
granted, push the task branch after every phase commit. Without it, the
handoff states that the result exists only on that machine.

## Role transport

- Dispatch each role as one subagent with `machine: "shared"` and the model
  "Flow rows" maps; it works in the root's checkout. Never `fresh`: a fresh
  machine checks out the upstream branch and cannot see the phase's
  uncommitted work.
- Every fix round and every review round is a new subagent with its packet.
  Continue a subagent with `message_agent` to its path only where WORKFLOW
  continues a session, such as a technical planner's plan-review loop.
- The packet adds: do not commit, open pull requests, spawn subagents, create
  threads or message other agents; end with one final report carrying the
  role's status line, Summary and artifact file name. Packets and reports are
  in the user's language from the first dispatch, including an analyst
  dispatched before checkout.
- One `tools.subagent.start` call applies one model to every index it starts.
  For the review pair, create both drafts in one `tools.subagent.create` call,
  start each index with its own model, and read each `rejected` list. Wait on
  both with `wait` (`subagents`, `return_when: "all"`) so the root wakes
  once with both reports.
- End the turn after dispatch: a subagent's final report wakes the root. A
  `queued` subagent starts on its own; never relaunch it. Stop one that must
  not continue with `tools.subagent.stop`.
- Capy has no read-only mode for subagents, so the Git check after every return
  is the guarantee. A role that needs a decision returns as `needs_you`; treat
  it as that role's `blocked` report.

## Task roots

- A task root is one Capy thread. Launched by a Captain with
  `tools.thread.create`, it is a crew thread whose `model` is the flow's
  `task_root` row mapped as "Flow rows" defines, and the Captain is its parent
  and its dispatcher parent under WORKFLOW "Dispatcher parent". Invoked
  directly, it is a plain thread and the person is its user.
- Report to the parent with a `message_agent` report without `to`:
  `needs_you` for a derived plan, a decision or a question for the person,
  `final` for the stable handoff. A `working` report never reaches the
  parent, so progress stays in the thread. The Captain hears from a crew thread
  each time it finishes a turn, so a wake that changes nothing the parent needs
  (a subagent result, CI) ends with `end_turn`.
- An initiative parent is a Captain. It keeps the register as its Drive
  `NOTES.md`, writes crew rules in `CREW.md`, and reads child handoffs in
  `reports/<code>.md` and through `tools.thread.get`. A crew stays inside the
  Captain's project.
- Capy issues may carry intake and link the thread and its PR; they never hold
  plan, phase or delivery state.

## Pull requests

- Push the task branch and confirm its published head is the terminal
  manifest commit. Open the PR with `tools.pr.create` passing
  `head: orchestra/<task-slug>`, base, title and body: it touches no checkout
  and makes this thread the PR's owner, so CI results, reviews, comments,
  conflicts and the merge wake it. Then run `pr.py open` on the same head to
  write the PR-CONTEXT capsule into that PR: it finds the open PR, keeps the
  body `tools.pr.create` wrote and replaces only the capsule. Pass
  `--repository` with the owner/name casing `tools.pr.create` returned. Never
  `gh pr create`.
- Only the root pushes to the task branch; the thread that last pushed owns
  the PR's events.
- A wake is news. Observe again with `pr.py observe` under WORKFLOW "PR path";
  `tools.pr.getChecks` and `tools.pr.getComments` are quick reads, not the
  clean judgment. With checks or a bot review pending, end the turn with
  `end_turn`.
- Capy's automatic review adds a PR feedback surface; it never replaces the
  WORKFLOW "Review policy" reviews or the review pair. When its verdict wakes
  the root, read `tools.pr.getFindings`, triage each finding under
  [finding triage](finding_triage.md) like other PR feedback, record the
  disposition with `tools.pr.updateFindings`, and fix accepted ones through a
  normal fix round. Capy also posts a review body, which `pr.py observe`
  lists as `supplemental_feedback`; after triage pass its `fingerprint` with
  `--acknowledged-feedback` to `observe` and `merge`. Inline comments it
  leaves are review threads `observe` reads, so the PR is not clean until
  each one has a disposition.
- Capy's instructions allow a merge only when the person asks for it in this
  thread: a `merge when clean` grant the person gave here counts, one relayed
  by a Captain does not.
  Otherwise report the clean PR and end the turn; the person merges from
  Capy's pull request page or asks here. A merge wakes the thread only when
  someone wrote in it within the last three days by default; otherwise run the
  post-delivery steps at its next wake. A merge done outside `pr.py merge`,
  such as GitHub's squash button, gets the hybrid cleanup by hand: confirm the
  merged head equals the terminal commit and the trees match, run
  `task_state.py cleanup`, switch the checkout to the fast-forwarded base,
  then delete the local and remote task branch only while each still points at
  that commit.

## Browser and preview

The root copies the lines below for the packet's `browser_route`, and the tab
lines, into each browser packet; roles never read this reference.

- `auto` and `in_app` use `tools.capy.browser` on the shared machine; no
  other surface exists, so any other `browser_route` returns `blocked`.
- Open a new tab for each run with a `tab` `new` action and note its id.
  Actions run on the selected tab, so select the task tab by id in its own call
  before acting, since shared subagents use the same browser. Save evidence
  with the `screenshot` action and copy its returned `path` to the PNG
  evidence path. Close that tab before every handoff and list tabs to confirm.
- User preview: start the app as a detached command, publish its port with
  `tools.expose.port` under a title naming the task, and include that preview
  in the preview pack. Revoke it with `tools.unpublish.port` and stop the
  process at freeze, skip or cancellation.

## Questions and gates

- In a plain thread, a question the person must answer is the turn's last act:
  `message_user` with `needs_you`, or `clarify_questions` for options.
- In a crew thread, gates go to the Captain as `needs_you` reports: the
  investigation-only report, the specification and the plan each in its own
  report, since a parent-launched root never combines them. The Captain
  answers what the brief and earlier decisions settle and relays the rest; the
  person may answer in the crew thread directly. A Captain's reply approves a
  delivery action, preview exit or new repository convention only when it
  quotes the person; a merge needs the person's own request.
- Comments and status changes on an issue the root owns also wake it. One that
  asks nothing, and any wake the parent does not need, ends with `end_turn`.
  When the Captain asks for no interim reports, platform reminders to report
  after repeated waits are answered with `end_turn` as well.
