# Orchestra

Orchestra is a cost-efficient, multi-agent software-delivery workflow for Codex,
Cursor, and Grok Build. It is built for one developer who wants planned work to
arrive reviewed, verified, and committed.

Orchestra turns a well-defined change into an approved plan, then drives it through implementation, independent review, runtime verification, and phase commits on an isolated `orchestra/*` branch. You stay the product owner and final authority; the orchestrator acts as your technical lead.

It is not a framework, a daemon, or a second Git. It is a set of skills, four agent profiles, and a few small Python helpers that your existing coding agent already knows how to run.

```text
$orchestra add CSV export to the orders page
```

```text
Brief ............ export orders as CSV from the orders list
Tier ............. standard (recommended: bounded UI + file download, low blast radius)
Acceptance ....... button visible on /orders; downloads orders.csv with the visible columns
Checkout ......... orchestra/orders-csv-export (worktree, from main)

Phase 1  export helper + unit tests .......... implemented ▸ reviewed ▸ committed
Phase 2  button + download flow .............. implemented ▸ browser-verified ▸ reviewed ▸ committed

Implementation complete; delivery pending.
Hold, open a PR, or integrate locally?
```

---

## Why Orchestra

Coding agents are already good at writing code. What they lack is a dependable process around the code: a confirmed spec, a plan that survives contact with the repository, someone independent who reads the diff, evidence that the thing actually runs, and commits you can trace. Most attempts to add that process turn into a workflow engine that costs more tokens than it saves.

Orchestra makes different bets:

- **Explicit, not ambient.** Nothing happens until you say `$orchestra`. Ordinary requests, plan mode, and quick fixes stay exactly as they were.
- **Four roles, not forty personas.** Analyst, implementer, reviewer, verifier. The root adds a capability (frontend, debugging, browser acceptance, planning) per dispatch instead of inventing a new agent for each domain.
- **Independence where it pays.** The implementer runs and fixes every deterministic check before handoff. A reviewer who did not write the code reads intent, diff, tests, and fresh evidence. A separate verifier appears only at real boundaries: browsers, running services, mutable data, credentials, or critical tiers.
- **Git is the state machine.** One task, one branch, one commit per accepted phase. No event ledger, no lock files, no plan CLI you have to keep in sync.
- **Quality per token.** Tokens go to understanding the repository, root-causing, tests, and high-signal review — not to re-validating unchanged authority or restarting whole runs after a local failure.
- **Bounded autonomy.** Inside an approved objective the orchestrator makes reversible technical decisions on its own. It stops for you at data loss, production, public contracts, security, external cost, scope expansion, and anything hard to undo.

## How a task flows

1. **Brief and tier.** Orchestra reuses the conversation you already had, summarizes the brief, recommends a tier with its cost-benefit, and asks you to choose.
2. **Specification.** A short read-only preflight and focused repository context close real gaps. You confirm observable acceptance in one message for simple tasks.
3. **Checkout.** One collision-free `orchestra/<slug>` branch is created — in a dedicated worktree (`managed`) or in your clean current checkout (`hybrid`). Never directly on `main`.
4. **Plan.** A planner writes one overview and one self-contained document per phase. You approve; the plan lands in the task's private `.orchestra/plan.md`.
5. **Phases.** For each phase: implement and self-check → optional visual preview for UI work → independent review → verification where the boundary demands it → phase commit with exact path scope and evidence.
6. **Delivery.** `implementation complete; delivery pending`. You decide: hold, open a PR, or integrate locally — according to the repository's declared policy.

Tier controls intensity (models, review depth, double evidence), never authority. `critical` phases keep independent double verification; `minimal` exists for cheap, bounded work on hosts that assign it.

## Hosts

| Host | Tiers | Notes |
| --- | --- | --- |
| **Codex** | `standard`, `critical`, plus opt-in `luna` (external mode) | Guardian permissions synced as default; native V2 or external V1 matrices |
| **Cursor** | `minimal`, `standard`, `critical` | Reads its own role matrix; browser work routed through Browser Use |
| **Grok Build** | `standard`, `critical` | `grok-4.6`; no cheaper tier |

All three share the same skills, helpers, plan format, and Git workflow. Each host contributes only spawn, models, permissions, and browser routing.

## Use the pieces on their own

You do not need the full workflow to benefit from the roles. Each skill works standalone from any chat:

```text
Use $orchestra-role-reviewer to review this diff for correctness.
Use $orchestra-role-implementer to fix this bug in these files.
Use $orchestra-role-verifier to verify this acceptance scenario in the browser.
Use $orchestra-phase-commit to commit these changes with the available evidence.
```

Or keep your current chat as orchestrator and hand a bounded assignment to another CLI:

```text
Use $orchestra-delegate to implement this with Codex CLI, model gpt-6-astra, effort low.
Use $orchestra-delegate to independently review this diff with Grok Build.
```

Delegation reuses that CLI's own account and session, reports source changes, and hands the result back for review — no billing surprises, no hidden workflow switch.

## Companion skills

| Skill | When |
| --- | --- |
| `orchestra` | Explicit full workflow: spec → plan → phases → delivery |
| `orchestra-project-start` | You have an idea and no repository. Picks a proportional stack, builds a runnable vertical slice, then *offers* Orchestra |
| `orchestra-repo-onboard` | Existing repo, first time. Verifies build/test commands and conventions from evidence and writes a tracked `.agent/` store so later tasks stop rediscovering them |
| `orchestra-task` | Capture and prepare a task card (`A1`, `A2`, …) from any chat without starting anything; adopt it later from a native host chat |
| `orchestra-delegate` | Run one assignment through Codex CLI, Cursor CLI, or Grok Build CLI with scoped permissions |
| `orchestra-role-*` | Analyst, implementer, reviewer, verifier as standalone tools |
| `orchestra-phase-commit` · `orchestra-delivery-policy` · `orchestra-pr-open` · `orchestra-pr-review` · `orchestra-pr-merge` · `orchestra-local-integrate` | Delivery, each with its own explicit authority contract |

## Install

**Prerequisites:** Python 3, Git, and at least one host (Codex ≥ 0.146, Cursor, or Grok Build). GitHub CLI only if you want PR delivery.

Clone this repository and run the sync from the checkout. It installs skills, profiles, role matrices, and helpers into the host's own directories, records everything it owns in a manifest, and never touches unrelated configuration.

```sh
git clone https://github.com/FranciscoJSBarragan/Orchestra.git
cd Orchestra

# Preview what would change
python3 codex/scripts/sync.py status --host all --modelconfig dual
python3 codex/scripts/sync.py apply --host all --modelconfig dual --dry-run

# Install for every host (or pick: --host codex | cursor | grok)
python3 codex/scripts/sync.py apply --host all --modelconfig dual

# Later
python3 codex/scripts/sync.py status
python3 codex/scripts/sync.py uninstall
```

Useful flags:

- `--modelconfig dual|native|external` — Codex model matrix. `dual` lets the root model pick per task. Persisted after the first apply.
- `--checkout-mode managed|hybrid` — dedicated worktree (default) or a fresh branch in your clean current checkout.
- `--worktree-root /path` — where managed worktrees live (default `~/.orchestra/worktrees`).

Sync results are `ok`, `partial` (nothing unsafe happened, read `detail`), or `blocked` (a named safety, drift, or ownership issue; nothing was written). Uninstall removes only content whose digest still matches the manifest.

### Per-repository configuration

Each consumer repository declares its delivery policy and checks in `orchestra.toml`:

```toml
[delivery]
mode = "hybrid"   # "hold" | "pr" | "hybrid" | "local"

[[checks]]
name = "suite"
command = ["python3", "-m", "pytest", "-q"]
```

Missing policy is never inferred — Orchestra asks once and recommends `hybrid`. Repository conventions that workers should cite (hard gates, prerequisites, code conventions) live in tracked `.agent/` files; `$orchestra-repo-onboard` writes them for you.

## What Orchestra will not do

- Replace Git, GitHub, CI, or your tests.
- Require PRs, or merge, release, or deploy without separate explicit authorization.
- Run in the background. There is no daemon, HTTP server, or remote service.
- Persist every thought. Task state lives in one self-ignored `.orchestra/` directory inside the worktree and is removed only by guarded cleanup.
- Become an enterprise approval platform.

## Repository layout

```text
VISION.md              mission, principles, success criteria, non-goals
docs/WORKFLOW.md       the canonical behavior contract, request → delivery
docs/ARCHITECTURE.md   components, contracts, host adapters, installation boundary
docs/ROADMAP.md        non-canonical; deferred distribution and benchmarks
AGENTS.md              concise executable rules for agents working on Orchestra itself
codex/skills/          the 15 skills and their internal playbooks
codex/agents/          the four namespaced agent profiles
codex/config/          Codex role matrix and permission defaults
codex/scripts/         sync.py, validate_suite.py, coordination and task-control helpers
codex/tests/           conformance suite
hosts/cursor, hosts/grok  host role matrices
hub/                   optional local read-only hub, TUI, and macOS menu-bar client
```

Product intent has a strict precedence: `VISION.md` → `docs/WORKFLOW.md` → `docs/ARCHITECTURE.md` → `AGENTS.md` → skills, profiles, scripts, tests. Lower layers never silently redefine higher ones.

## Contributing

Run the conformance suite before opening a PR:

```sh
python3 codex/scripts/validate_suite.py --quick   # what the pre-commit hook runs
python3 codex/scripts/validate_suite.py --full    # manual and CI entry point
```

Every test must prove observable acceptance or pin a named regression risk. Read `AGENTS.md` for the anti-overengineering rules — before adding a mechanism, name its consumer, the failure it prevents, why an existing primitive is not enough, and its cleanup path.

## Status

Orchestra is in active use on real projects by its author and is shared here for developers who want the same process. The skill and helper contracts are stable enough to install; the plugin/marketplace distribution boundary is intentionally deferred until install, update, and both delivery paths are proven in more repositories (see `docs/ROADMAP.md`). Feedback from real tasks is the most useful contribution right now.

## License

[MIT](LICENSE)
