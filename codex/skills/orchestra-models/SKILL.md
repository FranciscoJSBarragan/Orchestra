---
name: orchestra-models
description: Use when the user asks to see or change which providers and models Orchestra assigns to its roles.
---

# Orchestra models

Read [runtime resources](../orchestra/runtime.md) once to resolve the package.
The shipped assignment is `${ORCHESTRA_RUNTIME_ROOT}/flow.toml`. The user's
changes live only in `${ORCHESTRA_HOME:-$HOME/.orchestra}/flow.toml`, and
WORKFLOW "Flow assignment" owns how the two combine. This skill never starts a
task, dispatches agents or changes permissions.

## Show

1. Read both files and show one table: each capability, then `review_pair` and
   each `escalation` attempt, with provider, model, effort, and whether the
   entry is the default or the user's.
2. With the `t3-code` tools available, read `orchestrator_capabilities` and mark
   every entry whose provider instance, model or effort the live catalog lacks.
   Without them, say that the check needs T3 Code.

## Change

1. Take the change in the user's words ("review with Opus", "research on
   Cursor") and map it to exact entries and catalog ids. Ask only when a phrase
   fits several capabilities or catalog entries.
2. Refuse a provider, model or effort the live catalog lacks and name what it
   offers instead. Without the catalog, save it only if the user accepts that
   an unknown model blocks the task that first needs it.
3. Keep `independent_review` and `review_pair` outside the implementer's model
   family; if the user still wants the same family, say once that reviewers
   from the implementer's family share its blind spots, then follow the user.
4. Show the resulting entries, then write only the user's file: the shipped
   shape with just the entries that differ. Never edit the package.
5. To restore defaults, delete the user's entries, or the whole file, after the
   user confirms.

A change applies to tasks that resolve the assignment afterwards. A running task
keeps its recorded assignment until the user decides under WORKFLOW "Flow
assignment".

## Output

Return the table, any refused change with the catalog's alternatives, and the
path written, if any.
