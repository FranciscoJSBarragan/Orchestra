---
name: orchestra
description: Route small, fully understood software changes through Orchestra's dependable light workflow. Use when the root must classify a requested implementation, fail closed on ambiguity or risk, dispatch one implementation worker and an independent reviewer, require targeted verification, and hand an accepted phase to the thin commit path. Standard and critical execution are not implemented by this skill.
---

# Route a light change

Keep the root orchestrator responsible for problem framing, tier selection, user alignment, routing, compact synthesis, blocker resolution, and final technical judgment.

## Classify before dispatch

Declare `Tier: light|standard|critical — reason` before execution. Select `light` only when all of these facts are proven:

- one small, fully understood objective;
- localized impact following an established pattern;
- no public API, schema, CLI, persisted format, dependency, or architecture change;
- no auth, security, privacy, payment, migration, production, deployment, destructive, or irreversible risk;
- no unresolved product decision;
- one direct targeted verification exists.

Fail closed to `standard` on any ambiguity, unknown scope, new coupling, or risk. Stop this skill before dispatch for `standard` or `critical`, report that those execution lanes are unavailable in the current slice, and return control to the root. Do not improvise their explorer, planning, audit, or implementation flow.

## Resolve role assignments

Read [roles.toml](../../config/roles.toml) as the only machine-readable model and reasoning matrix. For every light spawn, including `phase_committer`, resolve `tiers.light.<role>` and pass its `model` and `reasoning_effort` as explicit overrides. Use [implementation_worker.toml](../../agents/implementation_worker.toml), [reviewer.toml](../../agents/reviewer.toml), and [phase_committer.toml](../../agents/phase_committer.toml) for role instructions. Do not copy assignments into profiles or this skill.

## Build the packet

Keep one compact packet in memory with exactly these fields:

- objective;
- known decisions and context;
- allowed paths;
- acceptance;
- verification;
- exclusions;
- stop conditions;
- references and revision.

Do not write workflow state, transition logs, authority bundles, or task-packet files.

## Execute and review

1. Send the packet to one `implementation_worker`.
2. Require the worker to change only allowed paths and return observed targeted-verification evidence.
3. Send the packet, revision, relevant diff, and evidence to one independent `reviewer`. Do not ask the reviewer to edit.
4. Evaluate material findings at the root. Return accepted findings to the same implementation owner.
5. Re-run affected verification and review only the meaningful delta until accepted or blocked.
6. Hand the exact authorized paths, structured message, and verification summary to [orchestra-phase-commit](../orchestra-phase-commit/SKILL.md) through the `phase_committer` profile.
7. Read the compact commit result and make the final technical judgment at the root.

Stop for the user at destructive or irreversible operations, production mutation, data-loss risk, security or privacy policy changes, public-contract changes, new product choices, material external cost, or substantial scope expansion.
