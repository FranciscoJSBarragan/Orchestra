<!-- orchestra:start -->
## Orchestra routing

Orchestra is an explicit planned-work route, not the default implementation route. Activate `$orchestra` only through an explicit `$orchestra` invocation or an unequivocal imperative to use or start Orchestra. Ordinary plan requests, descriptive mentions, and direct change, fix, or implementation work remain outside Orchestra. In a planning-only host mode, reuse the conversation and pause before branch, worktree, plan, implementation, or commit mutation; continue without a second invocation once the host is execution-capable. Orchestra observes the current host mode and never changes it.

Ordinary technical work may use `$orchestra-engineering` and maintained project
verification recipes without activating the planned route. WORKFLOW "Modular
engineering" owns their composition. Explicit repository audit or deslop requests
may use `$orchestra-repo-maintenance` under WORKFLOW "Repository maintenance".
For meaningful behavior or test changes, use `$orchestra-engineering`'s shared
"Behavioral verification" and "Change quality" criteria. Suite cleanup uses
"Test maintenance" through the maintenance entry, within the current authority.

User follow-ups and worker updates preserve the active objective under WORKFLOW
"Conversation continuity". Apply its response and recovery rules without
activating the planned route for ordinary work.

Workflow policy has one canonical home: `${ORCHESTRA_HOME:-$HOME/.orchestra}/WORKFLOW.md`, routed by `$orchestra`. This managed block is the Codex host overlay and adds only host runtime facts:

- Use `${ORCHESTRA_HOME:-$HOME/.orchestra}` as the shared runtime home; helpers live at `${ORCHESTRA_HOME:-$HOME/.orchestra}/scripts/` with fallback `${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/`.
- Read `${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml` and resolve `tiers.<tier>.<capability>` directly. Codex uses native host execution; WORKFLOW owns model availability and legacy task transitions.
- Explicit execution presets resolve through `scripts/delegate.py --resolve-only` and the shared `execution-presets.toml` before native capability lookup; WORKFLOW owns their selection and recovery rules.
- Load profiles from `${CODEX_HOME:-$HOME/.codex}/agents/` and pass each explicit `model` and `reasoning_effort`. Never fork full root history into an agent. Wait with `wait_agent` using `timeout_ms: 600000` and without `autoResolutionMs`.
- Checkout configuration lives at `${ORCHESTRA_HOME:-$HOME/.orchestra}/checkout-mode` and `${ORCHESTRA_HOME:-$HOME/.orchestra}/worktree-root`, with Codex fallbacks under `${CODEX_HOME:-$HOME/.codex}/orchestra/`. The selected managed or hybrid checkout is the only task checkout; scoped dirty-path imports use `adopt_worktree.py`.
- Orchestra synchronizes Guardian (`:workspace`, `on-request`, Auto-review) as the default; the active permission choice for the task, host, or launcher remains authoritative.
- After approval the root maintains `plan.md` (`active`, `blocked`, `completed`) per WORKFLOW. Use `$orchestra-phase-commit` only after review and verification pass, then route delivery through `$orchestra-delivery-policy`. Incomplete intended post-mutation cleanup is `partial`.
<!-- orchestra:end -->
