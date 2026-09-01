<!-- orchestra:start -->
## Orchestra routing

Orchestra is an explicit planned-work route, not the default implementation route. Activate `$orchestra` only through an explicit `$orchestra` invocation or an unequivocal imperative to use or start Orchestra. Ordinary plan requests, descriptive mentions, and direct change, fix, or implementation work remain outside Orchestra. In a planning-only host mode, reuse the conversation and pause before branch, worktree, plan, implementation, or commit mutation; continue without a second invocation once the host is execution-capable. Orchestra observes the current host mode and never changes it.

Workflow policy has one canonical home: `${ORCHESTRA_HOME:-$HOME/.orchestra}/WORKFLOW.md`, routed by `$orchestra`. This managed block is the Codex host overlay and adds only host runtime facts:

- Use `${ORCHESTRA_HOME:-$HOME/.orchestra}` as the shared runtime home; helpers live at `${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/` with fallback `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/`.
- Read `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml`. A dual matrix requires one `session_model.py` run before tier selection and resolves `modes.<modelconfig>.tiers.<tier>.<capability>`; a legacy matrix resolves `tiers.<tier>.<capability>`. The selected model configuration is immutable for the task.
- Load profiles from `${CODEX_HOME:-$HOME/.codex}/agents/` and pass each explicit `model` and `reasoning_effort`. Never fork full root history into an agent. Wait with `wait_agent` using `timeout_ms: 600000` and without `autoResolutionMs`.
- Checkout configuration lives at `${ORCHESTRA_HOME:-$HOME/.orchestra}/checkout-mode` and `${ORCHESTRA_HOME:-$HOME/.orchestra}/worktree-root`, with Codex fallbacks under `${CODEX_HOME:-$HOME/.codex}/orchestra/`. The selected managed or hybrid checkout is the only task checkout; scoped dirty-path imports use `adopt_worktree.py`.
- Orchestra synchronizes Guardian (`:workspace`, `on-request`, Auto-review) as the default; the active permission choice for the task, host, or launcher remains authoritative.
- After approval the root maintains `plan.md` (`active`, `blocked`, `completed`) per WORKFLOW. Use `$orchestra-phase-commit` only after review and verification pass, then route delivery through `$orchestra-delivery-policy`. Incomplete intended post-mutation cleanup is `partial`.
<!-- orchestra:end -->
