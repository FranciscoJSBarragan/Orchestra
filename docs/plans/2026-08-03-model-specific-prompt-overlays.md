# Model-specific prompt overlays (deferred analysis)

Status: deferred. Recorded during the 2026-08-03 flow-simplification plan so a
later task can evaluate it with evidence. Nothing here is implemented; the
base role skills introduced by that plan are intentionally model-agnostic.

## Motivation

Orchestra assigns different models per capability and tier (native: Sol/Terra;
external: Grok, GLM, Composer, Gemini variants through aliases). Model
families respond differently to prompt style — e.g. the GPT-5.6 guide shows
GPT-5.6 performs better with leaner prompts, strong intent inference, and a
single compact autonomy policy, while other families may still benefit from
more explicit step structure or stricter output scaffolding. A per-model
overlay could close measured gaps without forking role behavior.

## Design sketch (to validate later)

- The role skill stays the single canonical source of behavior. An overlay is
  an optional, short prompt fragment selected by the *assigned model family*,
  never a divergent copy of the role.
- Natural attachment point: the assignment matrix already resolves
  `profile + model + reasoning_effort` per capability; an optional
  `prompt_overlay` key could name a fragment under
  `codex/skills/orchestra/references/overlays/<family>.md`, passed in the
  packet like capability references are today.
- Overlay content budget: ≤ 15 lines. Only style/scaffolding adaptations
  (output framing, step explicitness, tool-call phrasing). Behavior,
  authority, stop conditions, and output contracts stay in the role skill and
  shared conduct.

## Rules for adoption (from the GPT-5.6 guide, generalized)

- Add an overlay only to correct a *measured* gap on representative tasks,
  never speculatively ("keep examples and style guidance when they encode a
  product requirement or correct a measured gap").
- Re-run the same comparison after model upgrades; overlays rot quickly.
- If an overlay grows or starts restating role rules, delete it or fix the
  role skill instead.

## GPT-5.6 features to evaluate for Orchestra later

- `max` reasoning effort (supported by GPT-5.6): compare against `high`/
  `xhigh` for the critical tier's hardest capabilities before adopting; the
  current matrices intentionally avoid Sol xhigh.
- Pro mode (`reasoning.mode: "pro"`) and Programmatic Tool Calling are
  Responses-API features; whether/how Codex CLI exposes them to spawned
  agents must be verified against the installed Codex version before any
  matrix change.
- Explicit prompt caching: potentially relevant to the root's stable skill
  preamble if Codex exposes cache controls; verify first.

## Trigger to revisit

Revisit when (a) a capability shows a repeatable quality gap attributable to
prompt style on its assigned model, or (b) the model matrix changes family
composition, or (c) Codex exposes new GPT-5.6 runtime controls to spawned
agents.
