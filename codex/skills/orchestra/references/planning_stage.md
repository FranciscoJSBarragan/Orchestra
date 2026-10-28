# Planning stage

Read this once the specification is confirmed. Re-read
[finding triage](finding_triage.md) at every plan judgment.

1. **Author.** Write the plan yourself under
   [technical planning](technical_planning.md) when one owner of one
   implementation capability covers the work, its risk order is uniform, no
   result must be committed before another begins and its material design
   decisions are resolved. Otherwise, or for high-impact risk or an unresolved
   boundary decision (version compatibility, migration order, recovery
   semantics, ownership handoff), dispatch `technical_planning`. Item, file or
   screen counts and crossing a runtime boundary are not criteria, a short diff
   settles no boundary, and this choice waives no gate. When your observed
   model matches the flow's `technical_planning` row, the root-reuse rule in
   WORKFLOW "Flow assignment" replaces this choice.
2. **Own the bundle.** Read the overview, phase index, risks and only the
   detail your judgment needs. Collapse phases that name no boundary yourself,
   without a review cycle. Apply triage rules 2 and 4 and the
   proportional-correction check to the plan's own invariants, decisions and
   mechanisms before review and again before approval.
3. **Review.** Skip independent plan review only when current evidence settles
   the material design choices, every `State writers` entry (including `none`)
   cites source evidence, and WORKFLOW "Engineering guidance and evidence"
   requires no decision review. Dispatch it for an unresolved architectural
   alternative, consequential contract, migration or recovery assumption,
   unfamiliar dependency or costly-to-reverse decision; counts never create the
   gate. Prefer a bounded authorized experiment for an empirical question.
4. **Judge.** Triage each `plan-review` finding by its stable ID. Accepting a
   defect does not approve its proposed correction; a correction that narrows,
   excludes or excepts the confirmed outcome is replaced by an in-scope one.
   Only a genuine new product choice, or infeasibility crossing an authority
   boundary, goes to the user with options and consequences. Send accepted
   IDs and the correction direction to a fresh planning session with the
   current bundle, which republishes only affected members and names the full current bundle. After a second material
   review, and at once for marginal, contradictory or out-of-scope findings,
   read the exact bundle and reviews yourself and correct direction by finding
   ID.
5. **Approval.** Request approval of the exact accepted bundle at the user's
   altitude, separating required outcomes and binding constraints from the
   technical approach, including any new verification tooling and its size
   and any step the user must perform.
   Show every material change to the requested outcome (narrowing, exclusion,
   exception, changed user-visible amount or behavior, new user-facing
   consequence, including effects on indirect consumers) with its
   consequence, recorded in Decisions or Risks. Ask each `Dismissed
   counterexamples` entry that changes a user-visible result with its
   recommended reading unless an earlier answer settles it; technical-only
   entries stay your decisions. Do not reconfirm unchanged requirements,
   ordinary technical conditions or reversible technical decisions. A
   multi-phase bundle names, one line per extra phase, the boundary it buys.
