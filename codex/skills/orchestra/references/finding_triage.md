# Finding triage

Re-read this file every time you judge findings: plan review, each
implementation or delta review, and PR feedback. Reviewers stay unfiltered;
you are the filter. A finding is never fixed because it was reported. Judge
each one yourself against the confirmed specification, the approved plan and
the current code, and stop at the first rule that applies:

1. **Conflicts with intent.** It contradicts the confirmed specification, an
   exclusion, an invariant that has an origin, or an earlier accepted fix, or
   the reviewer role skill lists it under `Not findings`: reject it, citing
   which.
2. **No origin.** Trace what it breaks to the user's words, a confirmed
   acceptance point, a binding contract, existing behavior the repository
   relies on (`file:line`), or security, privacy or data integrity. When it
   breaks only a plan invariant, decision or mechanism with none of these
   origins, including one you or the planner added, do not send it to
   implementation: remove or narrow that plan item instead. Ask the user only
   when the removal changes a user-visible result.
3. **Disproven.** The current code already handles it: resolve it without
   code and cite the evidence.
4. **Not reachable.** It needs a deployment, exposure, environment or
   dependency misbehavior the system does not have, or a sequence the
   product's own operations cannot produce: reject it. When reachability is
   plausible but unshown, run one cheap deterministic check that builds the
   claimed state or input, and reject it only if that check disproves it. A
   check that never creates the claimed condition, such as observing a host
   that lacks it, proves nothing.
5. **User choice.** A product, contract or authority decision, or a
   correction that would change user-visible appearance or behavior beyond
   the request: ask once, grouped, with your recommendation.
6. **Accept** the rest: incorrect behavior or unmet acceptance, a regression
   of existing behavior, a security, privacy or data risk, unsafe error
   handling or concurrency, missing verification of important behavior, a
   mechanism materially larger than a named smaller design that meets the
   same outcome, or a demonstrated maintenance cost. Judge impact, not the
   reviewer's severity label; a false authorization claim in documentation is
   not cosmetic.

Before sending accepted findings:

- **Proportional correction.** When the smallest correction needs a new
  mechanism larger than the defect (process control, protocol, state, lock,
  retry or supervision layer), question the requirement before building it:
  narrow the plan item or ask the user. A finding inside machinery an earlier
  correction added means that correction was wrong: remove it instead of
  patching it.
- **Rounds.** Only an accepted finding that breaks the outcome, regresses
  existing behavior or risks security, privacy or data opens a fix round with
  a fresh delta review. Minor accepted findings (wording, docs, messages,
  readability, redundant tests) join that round when one exists; otherwise
  the owner fixes them and you inspect the exact delta yourself, without a
  review round, when it changes no executable behavior. Never reopen
  unaffected evidence or loop on pure preference.
- **Fix packet.** Group accepted findings per owner. State each accepted
  defect, its evidence and the outcome or invariant it breaks. The owner
  designs the correction; prescribe a mechanism only when the user chose it
  or an alternative must stay excluded.

At plan approval, apply rules 2 and 4 and the proportional-correction check to
the plan's own invariants, decisions and mechanisms, not only to reviewer
findings.
