# Orchestra

Orchestra is a Codex-native, cost-efficient, multi-agent software-delivery workflow.

It helps an individual developer move a software change from a clear objective
to a reviewed, verified, and committed result. The root orchestrator acts as
the technical lead: it frames the problem, selects a proportional workflow,
routes focused work to specialized agents, resolves ordinary blockers, and
makes the final technical judgment. The user remains the product owner and
final authority.

## Product sources

Product intent follows this precedence:

1. `VISION.md` defines mission, audience, principles, success, and non-goals.
2. `docs/WORKFLOW.md` defines behavior from request through delivery.
3. `docs/ARCHITECTURE.md` defines component and role boundaries.
4. `AGENTS.md` provides concise executable rules for agents.
5. Skills, profiles, scripts, tests, and hooks implement those sources.

Lower levels must not silently redefine higher levels. A deliberate product
change updates the relevant canonical document and its executable enforcement
together.

## Delivery model

Orchestra scales discovery, planning, implementation, review, and verification
to task risk. It supports both direct local integration and GitHub PR delivery
when repository policy and user authority allow them.

The source repository is authoritative. Runtime resources are installed through
repository-driven direct sync, with one owner for managed files and no changes
to unrelated Codex configuration.

## Conformance

Run the deterministic suite validator from the repository root:

```sh
python3 codex/scripts/validate_suite.py --quick
python3 codex/scripts/validate_suite.py --full
```

The versioned pre-commit hook invokes only quick validation. Full validation is
the manual and CI entry point.
