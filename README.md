# Orchestra

Orchestra provides reusable engineering skills and an explicit multi-agent
software-delivery workflow that runs inside [T3 Code](https://github.com/pingdotgg/t3code).
Use individual skills in any harness, or invoke `$orchestra` in a T3 thread for
an approved plan, implementation, independent review, verification and phase
commits. You remain the product owner and final authority.

The core is skills, one flow assignment and focused Python helpers. It needs no
task manager, MCP server, database or background service of its own: T3 Code
supplies threads, worktrees, delegation to the providers it runs, the browser
and pull request watching.

```text
$orchestra add CSV export to the orders page
```

```text
Brief ............ export orders as CSV from the orders list
Acceptance ....... button visible on /orders; downloads orders.csv with the visible columns
Checkout ......... orchestra/orders-csv-export (T3 worktree, from main)

Phase 1  export helper + unit tests .......... implemented ▸ reviewed ▸ committed
Phase 2  button + download flow .............. implemented ▸ browser-verified ▸ reviewed ▸ committed

Implementation complete; delivery pending.
Hold, open a PR, or integrate locally?
```

---

## Why Orchestra

Coding agents are already good at writing code. What they lack is a dependable process around the code: a confirmed spec, a plan that survives contact with the repository, someone independent who reads the diff, evidence that the thing actually runs, and commits you can trace. Most attempts to add that process turn into a workflow engine that costs more tokens than it saves.

Orchestra makes different bets:

- **Explicit full workflow.** `$orchestra` starts the planned route. Modular skills support ordinary work without activating it.
- **Four roles, not forty personas.** Analyst, implementer, reviewer, verifier. The root adds a capability (frontend, debugging, browser acceptance, planning) per dispatch instead of inventing a new agent for each domain.
- **The right model for each role.** One flow assigns each capability a provider and model inside T3: Claude Code implements, GPT Sol reviews and verifies, a second reviewer from another family joins the first full review. You change any row without forking the flow.
- **Independence where it pays.** The implementer runs and fixes every deterministic check before handoff. A reviewer who did not write the code reads intent, diff, tests, and fresh evidence. A separate verifier appears only at real boundaries: browsers, running services, mutable data, credentials.
- **Git is the state machine.** One task, one branch, one commit per accepted phase. No event ledger, no lock files, no plan CLI you have to keep in sync.
- **Bounded autonomy.** Inside an approved objective the orchestrator makes reversible technical decisions on its own. It stops for you at data loss, production, public contracts, security, external cost, scope expansion, and anything hard to undo.

## How a task flows

1. **Brief.** Orchestra reuses the conversation you already had, summarizes the brief and resolves the flow assignment against T3's live model catalog.
2. **Specification.** A short read-only preflight and focused repository context close real gaps. You confirm observable acceptance in one message for simple tasks.
3. **Checkout.** One collision-free `orchestra/<slug>` branch is created — in a T3 worktree (`managed`) or in your clean current checkout (`hybrid`). Never directly on `main`.
4. **Plan.** The root or a planner writes one overview and one self-contained document per phase. Any required plan or decision review finishes before the plan is presented for approval; simple tasks can combine specification and plan approval. The approved plan lands in the task's private `.orchestra/plan.md`.
5. **Phases.** For each phase: implement and self-check → optional visual preview for UI work → independent review → verification where the boundary demands it → phase commit with exact path scope and evidence.
6. **Delivery.** `implementation complete; delivery pending`. You decide: hold, open a PR, or integrate locally — according to the repository's declared policy. You can also grant the endpoint up front ("open a PR and merge when clean").

## Models

[`codex/config/flow.toml`](codex/config/flow.toml) is the default assignment:
a T3 provider instance, model and optional effort for each capability, the
second reviewer, and the recovery attempts. To change it, write only the
entries you want in `~/.orchestra/flow.toml`, or ask `$orchestra-models` to
show and change them against T3's live catalog; each entry replaces the
shipped one whole. Supporting another T3 provider is one more row and a short check that
its children can read their role skill and keep read-only work read-only.

## Use the pieces on their own

You do not need the full workflow to benefit from the roles. Each skill works standalone from any chat, inside or outside T3:

```text
Use $orchestra-role-reviewer to review this diff for correctness.
Use $orchestra-role-implementer to fix this bug in these files.
Use $orchestra-role-verifier to verify this acceptance scenario in the browser.
Use $orchestra-phase-commit to commit these changes with the available evidence.
```

Use `$orchestra-engineering` for focused understanding, design, implementation
or debugging in your current workflow. `$orchestra-project-verification` builds
or maintains a small map of how to operate and verify the actual application.
Both reuse the same engineering guidance without creating phases or task state.

Use `$orchestra-repo-readiness` to diagnose an existing repository against a
checkable readiness target or repair what you name: setup, deterministic gates,
isolated tests, an isolated runnable app, structure and `.agent/` conventions. It preserves actual
consumers and useful knowledge; folder reorganization is excluded. Source-writing
entries apply the shared zero explanatory comments policy, with legal and
functional exceptions.

Use `$orchestrator` when the outcome requires independent projects or task
roots. The parent sets shared contracts and checks the combined result; each
child runs full Orchestra in its own T3 thread. A Hermes thread in T3 can act as
that parent, or dispatch a single task: it works out the request with you and
delegates, but never implements. See [the coordination packet](codex/skills/orchestrator/packet-example.md)
and [behavioral acceptance](docs/evaluation/MODULAR_ACCEPTANCE.md).

## Companion skills

| Skill | When |
| --- | --- |
| `orchestra` | Explicit full workflow in T3: spec → plan → phases → delivery |
| `orchestra-project-start` | You have an idea and no repository. Picks a proportional stack, builds a runnable vertical slice, then *offers* Orchestra |
| `orchestra-repo-readiness` | Existing repo. Checks it against a runnable target state (one-command setup, clean and deterministic gates, isolated tests, isolated app, structure) and repairs what you grant, writing a short tracked `.agent/` store |
| `orchestra-models` | See or change the provider and model of each role, checked against T3's live catalog |
| `orchestra-role-*` | Analyst, implementer, reviewer, verifier as standalone tools |
| `orchestra-phase-commit` · `orchestra-delivery-policy` · `orchestra-pr-open` · `orchestra-pr-review` · `orchestra-pr-merge` · `orchestra-local-integrate` | Delivery, each with its own explicit authority contract |

## Install

**Prerequisites:** Python 3, Git, T3 Code with the providers you want to use
(Claude Code, Codex, Cursor, Grok), and the GitHub CLI if you want PR delivery.

Build a self-contained bundle for each provider you use as a task root, and
install it with that provider's plugin manager:

```sh
python3 codex/scripts/package_plugin.py --target claude --output dist/claude/orchestra
python3 codex/scripts/package_plugin.py --target portable --output dist/portable/orchestra   # Codex
python3 codex/scripts/package_plugin.py --target cursor --output dist/cursor/orchestra
python3 codex/scripts/package_plugin.py --target grok --output dist/grok/orchestra
```

Every bundle carries the same workflow, skills, helpers and flow assignment and
inherits the provider's permissions. See [plugin packaging](packaging/README.md)
for local loading and updates. A remote T3 environment can instead pin a
source checkout with `codex/scripts/prepare_source.py`. Building does not
install or publish anything.

Optional settings live in `~/.orchestra/`: `checkout-mode` (`managed` or
`hybrid`), `worktree-root`, `browser-route` (`auto`, `in_app`, `chrome` or
`codex-cu`) and `flow.toml`.

### Per-repository configuration

Each consumer repository declares its delivery policy and checks in `orchestra.toml`:

```toml
[delivery]
mode = "hybrid"   # "hold" | "pr" | "hybrid" | "local"

[[checks]]
name = "suite"
command = ["python3", "-m", "pytest", "-q"]
```

Missing policy is never inferred — Orchestra asks once and recommends `hybrid`. Repository conventions that workers should cite (hard gates, prerequisites, code conventions) live in tracked `.agent/` files; `$orchestra-repo-readiness` writes them for you.

## What Orchestra will not do

- Replace Git, GitHub, CI, or your tests.
- Require PRs, or merge, release, or deploy without separate explicit authorization.
- Run its own daemon, HTTP server, or remote service.
- Persist every thought. Task state lives in one self-ignored `.orchestra/` directory inside the worktree and is removed only by guarded cleanup.
- Become an enterprise approval platform.

## Repository layout

```text
VISION.md              mission, principles, success criteria, non-goals
docs/WORKFLOW.md       the canonical behavior contract, request → delivery
docs/ARCHITECTURE.md   components, contracts, the T3 host, installation boundary
docs/ROADMAP.md        non-canonical; decisions, deferred work and rejected ideas
AGENTS.md              concise executable rules for agents working on Orchestra itself
codex/skills/          the shared skills and their internal playbooks
codex/config/flow.toml the default flow assignment
codex/scripts/         packaging, validation, local plan and Git helpers
codex/tests/           conformance suite
packaging/             plugin metadata and the Claude Code read hook
```

Product intent has a strict precedence: `VISION.md` → `docs/WORKFLOW.md` → `docs/ARCHITECTURE.md` → `AGENTS.md` → skills, scripts, tests. Lower layers never silently redefine higher ones.

## Contributing

Run the conformance suite before opening a PR:

```sh
python3 codex/scripts/validate_suite.py --quick   # what the pre-commit hook runs
python3 codex/scripts/validate_suite.py --full    # manual and CI entry point
```

Every test must prove observable acceptance or pin a named regression risk. Read `AGENTS.md` for the anti-overengineering rules — before adding a mechanism, name its consumer, the failure it prevents, why an existing primitive is not enough, and its cleanup path.

## Status

Orchestra is in active use on real projects by its author and is shared here for
developers who want the same process. The last release that supported Codex,
Cursor, Grok Build, Devin and Claude Code as separate hosts is the
`multi-host-final` tag. Public marketplace publication and broader real-project
delivery coverage remain in [the roadmap](docs/ROADMAP.md). Feedback from real
tasks is the most useful contribution right now.

## License

[MIT](LICENSE)
