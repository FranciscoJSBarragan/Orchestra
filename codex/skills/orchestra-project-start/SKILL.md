---
name: orchestra-project-start
description: Turn a greenfield software idea into a proportional, runnable project foundation and an evidence-backed handoff. Use implicitly when the user wants to create a new project, starts from an idea without an existing repository, works in an empty directory, asks for help choosing a stack, or requests initial project scaffolding. Do not replace normal repository work when meaningful application code already exists, and do not activate Orchestra delivery without an explicit user choice.
---

# Start a greenfield project

Help a non-expert user move from an idea to a small runnable vertical foundation
without imposing a generic stack, hidden mutation, or the full Orchestra
delivery workflow.

## Establish the greenfield boundary

Inspect the supplied directory and nearby project context read-only. Treat the
request as greenfield when there is no meaningful application repository or the
user explicitly wants a separate new project. If meaningful code already
exists, stop using this workflow and continue as ordinary repository work or
offer Orchestra only when the user explicitly asks for planned delivery.

Reuse requirements and decisions already present in the conversation. Ask only
questions whose answers materially change product behavior, stack, location,
cost, privacy, or acceptance.

## Shape the foundation

1. State the objective, primary audience, visible result, constraints, and
   exclusions in the user's language.
2. Propose one to three observable journeys: the main success path and any
   material empty, error, or failure behavior.
3. Recommend the smallest MVP and a proportional stack from actual constraints:
   target platform, deployment needs, offline or realtime behavior, data shape,
   authentication, integrations, team familiarity, and available runtimes.
   Explain the recommendation briefly and let the user choose.
4. Inspect runtime and tool availability read-only. Identify the intended
   location, canonical setup, run and test commands, required services or
   credential categories without reading secrets, test-data approach, and
   generated paths.
5. Present one concise mutation summary covering the target directory, stack,
   repository initialization, first vertical slice, verification, exclusions,
   and material risks. Require an explicit later confirmation before creating
   files, installing dependencies, initializing Git, or changing external
   state. A later explicit instruction for that unchanged summary satisfies the
   checkpoint without duplicate confirmation.

## Build after confirmation

Create only the approved project location and use the selected ecosystem's
canonical initializer or existing local tooling. Do not add a custom scaffolder,
bundled template, framework abstraction, deployment, hosted resource, or
production integration without explicit scope.

Produce the smallest vertical foundation that demonstrates one confirmed user
journey, including proportionate error or empty behavior. Establish canonical
development and verification commands and add only the configuration and tests
needed to prove the foundation. Preserve unrelated files and existing Git state.
Initialize Git only when the user approved it.

Run the smallest sufficient fresh checks and read their results. Classify
deterministic failures directly. Orchestra synchronizes Guardian
(`:workspace`, `on-request`, and Auto-review) as the default, while the active
permission choice for the task, host, or launcher remains authoritative.
Orchestra never changes that choice or blocks solely because it differs. When
Guardian is active, use one exact automatically reviewed escalation for a
protected boundary; never broaden the confirmed project scope merely because
an external service, credential, or dependency is missing.

## Hand off and offer Orchestra

Return:

- the project location and visible behavior;
- the chosen stack and why it fits;
- exact setup, run, and verification commands;
- fresh verification evidence;
- safe demo or test-data instructions;
- known limitations and the next useful product slice;
- Git and delivery state.

Then offer planned continuation through Orchestra in plain language. Do not
activate `$orchestra` automatically. If the user explicitly accepts, that
instruction activates Orchestra, which reuses this brief, decisions, readiness,
acceptance, and fresh evidence instead of restarting discovery.
