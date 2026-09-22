---
name: orchestra-project-verification
description: Prepare, run, refresh, or audit a project's reusable verification recipes and feature map. Use when the user wants agents to operate and verify the real application reliably, or when an authorized task needs to maintain an affected recipe. Does not require the full Orchestra workflow.
---

# Project verification

Read [runtime resources](../orchestra/runtime.md). WORKFLOW "Project verification"
and "Repository conventions" own the lifecycle, write authority, and distinction
between policy, operational instructions, and run evidence. Use
[shared engineering guidance](../orchestra/references/architecture_guidance.md)
("Verification recipes") for the substantive proof standard.

Resolve the requested operation from the brief: prepare, run, refresh affected
entries, or audit the named map. Existing maintained project instructions win
over a new copy. Use `.agent/verification/README.md` when no equivalent exists.
Discover the real setup, tests, fixtures, and interaction tools from the repo;
do not guess commands, selectors, environments, or expected behavior.

For preparation, establish a small useful map and make one representative
journey executable. The [feature example](feature-example.md) illustrates the
level of detail; adapt its shape to the project. Keep scripts beside the
existing test tools when those own them. Retain a new helper only when it has
a continuing consumer and a documented invocation. Reuse rather than wrap a
command that already gives the agent the necessary control and evidence.

For a run, read the index and selected entries, check the actual instance,
exercise the assigned entry points, inspect the expected effects, and capture
revision-bound evidence. Independent role invocations use
[runtime verification](../orchestra/references/runtime_verification.md) or
[browser acceptance](../orchestra/references/browser_acceptance.md) with their
source-read-only and host-routing contracts. Direct runs use the caller's
available tools and authority; they do not certify independent acceptance.

For refresh or audit, distinguish recipe drift, an interaction-tool gap, and a
product defect. Re-exercise a corrected recipe or tool. Do not redefine the
expected outcome to hide a regression. Full audit covers the named map;
ordinary feature maintenance covers affected entries and dependencies.

Report what was mapped, what actually ran, which revision and environment were
used, evidence locations, and remaining gaps. An unexecuted recipe is a draft.
A demonstrated route is not proof of every mapped route. Preserve evidence
when cleaning up owned processes and disposable data. Return compact results;
do not install into a host's global skill directory or modify the plugin cache.
