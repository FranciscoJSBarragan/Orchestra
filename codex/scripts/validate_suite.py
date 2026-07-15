#!/usr/bin/env python3
"""Validate the executable conformance contract for the Orchestra source tree."""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from typing import Callable


REQUIRED_PATHS = (
    "README.md",
    "VISION.md",
    "AGENTS.md",
    "docs/WORKFLOW.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    "orchestra.toml",
    ".githooks/pre-commit",
    "codex/scripts/validate_suite.py",
    "codex/scripts/sync.py",
    "codex/scripts/commit_phase.py",
    "codex/scripts/policy.py",
    "codex/scripts/pr.py",
    "codex/scripts/integrate_local.py",
    "codex/config/roles.toml",
    "codex/runtime/AGENTS.orchestra.md",
    "codex/agents/analyst.toml",
    "codex/agents/implementation_worker.toml",
    "codex/agents/reviewer.toml",
    "codex/agents/verifier.toml",
    "codex/skills/orchestra/SKILL.md",
    "codex/skills/orchestra/agents/openai.yaml",
    "codex/skills/orchestra/references/repository_context.md",
    "codex/skills/orchestra/references/web_research.md",
    "codex/skills/orchestra/references/technical_planning.md",
    "codex/skills/orchestra/references/difficult_debugging.md",
    "codex/skills/orchestra/references/frontend_implementation.md",
    "codex/skills/orchestra/references/browser_acceptance.md",
    "codex/skills/orchestra/references/runtime_verification.md",
    "codex/skills/orchestra/references/architecture_guidance.md",
    "codex/skills/orchestra-phase-commit/SKILL.md",
    "codex/skills/orchestra-phase-commit/agents/openai.yaml",
    "codex/skills/orchestra-delivery-policy/SKILL.md",
    "codex/skills/orchestra-delivery-policy/agents/openai.yaml",
    "codex/skills/orchestra-pr-open/SKILL.md",
    "codex/skills/orchestra-pr-open/agents/openai.yaml",
    "codex/skills/orchestra-pr-review/SKILL.md",
    "codex/skills/orchestra-pr-review/agents/openai.yaml",
    "codex/skills/orchestra-pr-merge/SKILL.md",
    "codex/skills/orchestra-pr-merge/agents/openai.yaml",
    "codex/skills/orchestra-local-integrate/SKILL.md",
    "codex/skills/orchestra-local-integrate/agents/openai.yaml",
    "codex/tests/test_commit_phase.py",
    "codex/tests/test_light_flow.py",
    "codex/tests/test_planned_flow.py",
    "codex/tests/test_validate_suite.py",
    "codex/tests/test_delivery_policy.py",
    "codex/tests/test_pr_flow.py",
    "codex/tests/test_local_integration.py",
    "codex/tests/test_sync.py",
)

PERMANENT_DOCS = (
    "README.md",
    "VISION.md",
    "AGENTS.md",
    "docs/WORKFLOW.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
)

IDENTITY = (
    "Orchestra is a Codex-native, cost-efficient, multi-agent "
    "software-delivery workflow."
)

HISTORICAL_NARRATIVES = (
    (
        "historical product replacement narrative",
        re.compile(
            r"\b(?:this|orchestra)\s+replaces?\s+(?:the\s+)?"
            r"(?:legacy|former|predecessor)\s+"
            r"(?:product|implementation|workflow|runtime)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "historical product label",
        re.compile(
            r"\b(?:legacy|former|predecessor)\s+(?:[\w-]+\s+){0,3}"
            r"(?:product|implementation|repository|runtime|workflow)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "historical repository path",
        re.compile(r"\bOrchestra-legacy\b", re.IGNORECASE),
    ),
    (
        "versioned product identity",
        re.compile(r"\bOrchestra\s+(?:v2|version\s+2)\b", re.IGNORECASE),
    ),
    (
        "rebuild narrative",
        re.compile(
            r"\b(?:clean-room rebuild|target for the rebuild|plan the rebuild|"
            r"during the rebuild|rebuild of Orchestra|fresh Git history)\b",
            re.IGNORECASE,
        ),
    ),
)

ROADMAP_REQUIREMENTS = (
    "This roadmap is non-canonical. It does not override `VISION.md`, "
    "`docs/WORKFLOW.md`, `docs/ARCHITECTURE.md`, or `AGENTS.md`.",
    "Plugin distribution remains deferred until all of these conditions hold:",
    "does not prescribe an implementation design.",
)

DEFERRED_DISTRIBUTION_CRITERIA = (
    "install, update, status, and uninstall are dependable;",
    "user configuration is preserved reliably;",
    "light and standard workflows succeed in real projects;",
    "local and PR delivery are proven;",
    "the user judges the product mature;",
    "packaging reduces friction without creating a second runtime.",
)

HOOK_CONTENT = """#!/bin/sh
set -eu
REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$REPO_ROOT/codex/scripts/validate_suite.py" --quick
"""

PROFILE_NAMES = (
    "analyst",
    "implementation_worker",
    "reviewer",
    "verifier",
)

EXPECTED_ASSIGNMENTS = {
    "light": {
        "general_implementation": ("implementation_worker", "gpt-5.6-luna", "max"),
        "independent_review": ("reviewer", "gpt-5.6-luna", "max"),
        "runtime_verification": ("verifier", "gpt-5.6-luna", "max"),
    },
    "standard": {
        "repository_context": ("analyst", "gpt-5.6-luna", "xhigh"),
        "web_research": ("analyst", "gpt-5.6-luna", "xhigh"),
        "technical_planning": ("analyst", "gpt-5.6-sol", "high"),
        "architecture_analysis": ("analyst", "gpt-5.6-sol", "high"),
        "difficult_debugging": ("analyst", "gpt-5.6-sol", "high"),
        "general_implementation": ("implementation_worker", "gpt-5.6-luna", "max"),
        "frontend_implementation": ("implementation_worker", "gpt-5.6-sol", "medium"),
        "independent_review": ("reviewer", "gpt-5.6-sol", "medium"),
        "browser_acceptance": ("verifier", "gpt-5.6-luna", "xhigh"),
        "runtime_verification": ("verifier", "gpt-5.6-luna", "max"),
    },
    "critical": {
        "repository_context": ("analyst", "gpt-5.6-sol", "medium"),
        "web_research": ("analyst", "gpt-5.6-sol", "medium"),
        "technical_planning": ("analyst", "gpt-5.6-sol", "high"),
        "architecture_analysis": ("analyst", "gpt-5.6-sol", "high"),
        "difficult_debugging": ("analyst", "gpt-5.6-sol", "high"),
        "general_implementation": ("implementation_worker", "gpt-5.6-sol", "high"),
        "frontend_implementation": ("implementation_worker", "gpt-5.6-sol", "high"),
        "independent_review": ("reviewer", "gpt-5.6-sol", "high"),
        "browser_acceptance": ("verifier", "gpt-5.6-sol", "medium"),
        "runtime_verification": ("verifier", "gpt-5.6-sol", "medium"),
    },
}

PLAYBOOK_NAMES = (
    "repository_context",
    "web_research",
    "technical_planning",
    "difficult_debugging",
    "frontend_implementation",
    "browser_acceptance",
    "runtime_verification",
)
ARCHITECTURE_REFERENCE = "architecture_guidance"
LEGACY_PROFILE_NAMES = (
    "browser_acceptance_tester",
    "debugging_investigator",
    "frontend_implementation_worker",
    "phase_committer",
    "plan_scope_auditor",
    "planner",
    "pr_polling_specialist",
    "pr_triage_specialist",
    "repo_context_explorer",
    "web_researcher",
)

SKILL_NAMES = (
    "orchestra",
    "orchestra-phase-commit",
    "orchestra-delivery-policy",
    "orchestra-pr-open",
    "orchestra-pr-review",
    "orchestra-pr-merge",
    "orchestra-local-integrate",
)
VALID_MODELS = {"gpt-5.6-luna", "gpt-5.6-sol"}

GRAPHIFY_ROUTING_REQUIREMENTS = (
    "## Use advisory Graphify context",
    "`graphify hook status` exactly once",
    "`uv tool install --upgrade graphifyy`",
    "`graphify . --update` at most once",
)

GRAPHIFY_CONTEXT_REQUIREMENTS = (
    "only when the root packet explicitly says the current detection pass found "
    "the graph usable",
    "verify every relevant claim against current source at the packet revision",
    "file existence alone never authorizes graph use",
)

GRAPHIFY_RUNTIME_REQUIREMENTS = (
    "The root solely owns Graphify as advisory, non-blocking context",
    "A missing command or incorrect exact tracked/ignored boundary adds the one "
    "approval-gated bootstrap",
    "Only when the command exists, interpret exactly one `graphify hook status` result",
    "Tell `repository_context` whether the pass found a usable graph",
    "Graphify never establishes correctness or policy",
)


def check_required_paths(root: Path) -> list[str]:
    """Ensure every current conformance consumer is present."""
    return [
        f"required-path: missing {relative}"
        for relative in REQUIRED_PATHS
        if not (root / relative).is_file()
    ]


def check_distribution_boundary(root: Path) -> list[str]:
    """Reject migration evidence and V1 distribution implementation paths."""
    failures: list[str] = []
    migration = root / "docs/MIGRATION.md"
    if migration.exists():
        failures.append("distribution-boundary: remove docs/MIGRATION.md")

    for relative in (Path(".codex-plugin"), Path("codex/.codex-plugin")):
        if (root / relative).exists():
            failures.append(
                f"distribution-boundary: prohibited V1 path {relative.as_posix()}"
            )
    return failures


def check_delivery_config(root: Path) -> list[str]:
    """Delegate source policy validation to its only loader."""
    helper = root / "codex/scripts/policy.py"
    if not helper.is_file():
        return []
    result = subprocess.run(
        [sys.executable, str(helper), "--repo", str(root), "show"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        return [f"delivery-contract: policy helper returned invalid JSON: {error}"]
    if not isinstance(payload, dict):
        return ["delivery-contract: policy helper returned invalid result"]
    if result.returncode or payload.get("status") != "ok":
        return [f"delivery-contract: {payload.get('reason', 'policy validation failed')}"]
    if payload.get("mode") != "hybrid":
        return ["delivery-contract: source repository mode must be hybrid"]
    return []


def check_roles_and_profiles(root: Path) -> list[str]:
    """Keep assignments canonical and profiles limited to behavior contracts."""
    roles_path = root / "codex/config/roles.toml"
    if not roles_path.is_file():
        return []
    try:
        roles = tomllib.loads(roles_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeError) as error:
        return [f"role-contract: codex/config/roles.toml is invalid: {error}"]

    failures: list[str] = []
    if set(roles) != {"tiers"}:
        failures.append("role-contract: roles.toml must contain tiers only")
    tiers = roles.get("tiers")
    if not isinstance(tiers, dict) or set(tiers) != set(EXPECTED_ASSIGNMENTS):
        failures.append(
            "role-contract: roles.toml must define light, standard, and critical"
        )
    else:
        for tier, expected_assignments in EXPECTED_ASSIGNMENTS.items():
            actual_assignments = tiers.get(tier)
            if not isinstance(actual_assignments, dict) or set(
                actual_assignments
            ) != set(expected_assignments):
                failures.append(f"role-contract: unexpected {tier} capability set")
                continue
            for capability, expected in expected_assignments.items():
                assignment = actual_assignments[capability]
                if not isinstance(assignment, dict) or set(assignment) != {
                    "profile",
                    "model",
                    "reasoning_effort",
                }:
                    failures.append(
                        f"role-contract: {tier}.{capability} needs profile, model, "
                        "and reasoning_effort"
                    )
                    continue
                actual = (
                    assignment["profile"],
                    assignment["model"],
                    assignment["reasoning_effort"],
                )
                if actual != expected:
                    failures.append(
                        f"role-contract: {tier}.{capability} does not match the "
                        "approved assignment matrix"
                    )
                if assignment["profile"] not in PROFILE_NAMES:
                    failures.append(
                        f"role-contract: {tier}.{capability} has invalid profile"
                    )
                if assignment["model"] not in VALID_MODELS:
                    failures.append(
                        f"role-contract: {tier}.{capability} has invalid model"
                    )
                if assignment["reasoning_effort"] not in {
                    "low",
                    "medium",
                    "high",
                    "xhigh",
                    "max",
                }:
                    failures.append(
                        f"role-contract: {tier}.{capability} has invalid reasoning_effort"
                    )
                if (
                    assignment["model"] == "gpt-5.6-sol"
                    and assignment["reasoning_effort"] == "xhigh"
                ):
                    failures.append(
                        f"role-contract: {tier}.{capability} must not use Sol xhigh"
                    )
                if capability in {"root", "orchestrator"} or assignment[
                    "profile"
                ] in {"root", "orchestrator"}:
                    failures.append("role-contract: root must have no assignment")

    agents = root / "codex/agents"
    actual_profiles = sorted(path.stem for path in agents.glob("*.toml"))
    if actual_profiles != sorted(PROFILE_NAMES):
        failures.append("profile-contract: current routing must define exactly four profiles")
        return failures
    declared_names: list[str] = []
    for name in PROFILE_NAMES:
        path = agents / f"{name}.toml"
        try:
            profile = tomllib.loads(path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError, UnicodeError) as error:
            failures.append(f"profile-contract: {path.relative_to(root)} is invalid: {error}")
            continue
        if set(profile) != {"name", "description", "developer_instructions"}:
            failures.append(
                f"profile-contract: {name} must contain only name, description, "
                "and developer_instructions"
            )
            continue
        if profile["name"] != name:
            failures.append(f"profile-contract: {name} has a mismatched name")
        if isinstance(profile["name"], str):
            declared_names.append(profile["name"])
        if not isinstance(profile["description"], str) or not profile["description"].strip():
            failures.append(f"profile-contract: {name} needs a description")
        instructions = profile["developer_instructions"]
        if not isinstance(instructions, str):
            failures.append(f"profile-contract: {name} needs developer instructions")
            continue
        for heading in ("## Input", "## Output", "## Stop conditions"):
            if heading not in instructions:
                failures.append(f"profile-contract: {name} is missing {heading}")

    if len(declared_names) != len(set(declared_names)):
        failures.append("profile-contract: profile names must be unique")

    behavior_sources = [
        *(agents / f"{name}.toml" for name in PROFILE_NAMES),
        *(root / f"codex/skills/{name}/SKILL.md" for name in SKILL_NAMES),
        root / "codex/runtime/AGENTS.orchestra.md",
    ]
    for path in behavior_sources:
        if path.is_file() and "gpt-5." in path.read_text(encoding="utf-8"):
            failures.append(
                "role-contract: model assignments must exist only in roles.toml; "
                f"found one in {path.relative_to(root)}"
            )

    routing_path = root / "codex/skills/orchestra/SKILL.md"
    if routing_path.is_file() and isinstance(tiers, dict):
        routing = routing_path.read_text(encoding="utf-8")
        for tier, capabilities in tiers.items():
            if not isinstance(capabilities, dict):
                continue
            for capability in capabilities:
                if f"`{capability}`" not in routing:
                    failures.append(
                        f"role-contract: {tier}.{capability} is not consumed by "
                        "orchestra routing"
                    )
    return failures


def _skill_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None
    raw = text[4:].split("\n---\n", 1)[0]
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key or not value.strip():
            return None
        metadata[key.strip()] = value.strip()
    return metadata


def check_skills_and_runtime(root: Path) -> list[str]:
    """Validate skill metadata, direct links, and the managed routing block."""
    failures: list[str] = []
    for name in SKILL_NAMES:
        skill = root / f"codex/skills/{name}/SKILL.md"
        if not skill.is_file():
            continue
        text = skill.read_text(encoding="utf-8")
        metadata = _skill_frontmatter(text)
        if metadata is None or set(metadata) != {"name", "description"}:
            failures.append(f"skill-contract: {name} needs name and description metadata")
        elif metadata["name"] != name or "TODO" in metadata["description"]:
            failures.append(f"skill-contract: {name} metadata is incomplete")

        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
            if target.startswith(("#", "http://", "https://")):
                continue
            resolved = (skill.parent / target).resolve()
            if not resolved.is_file():
                failures.append(f"skill-contract: {name} has broken link {target}")

        metadata_file = skill.parent / "agents/openai.yaml"
        if metadata_file.is_file():
            ui = metadata_file.read_text(encoding="utf-8")
            for field in ("display_name:", "short_description:", "default_prompt:"):
                if field not in ui:
                    failures.append(f"skill-contract: {name} openai.yaml is missing {field}")
            if f"${name}" not in ui:
                failures.append(
                    f"skill-contract: {name} default_prompt must mention ${name}"
                )

    references = root / "codex/skills/orchestra/references"
    expected_references = {
        *(f"{name}.md" for name in PLAYBOOK_NAMES),
        f"{ARCHITECTURE_REFERENCE}.md",
    }
    if not references.is_dir():
        failures.append("skill-contract: orchestra internal references are missing")
    else:
        actual_references = {entry.name for entry in references.iterdir()}
        if actual_references != expected_references or any(
            not entry.is_file() or entry.is_symlink() for entry in references.iterdir()
        ):
            failures.append(
                "skill-contract: orchestra must contain exactly seven playbooks "
                "and one architecture reference"
            )
        routing_path = root / "codex/skills/orchestra/SKILL.md"
        if routing_path.is_file():
            routing = routing_path.read_text(encoding="utf-8")
            for name in PLAYBOOK_NAMES:
                target = f"references/{name}.md"
                if target not in routing:
                    failures.append(
                        f"skill-contract: orchestra does not consume playbook {target}"
                    )
            architecture_target = f"references/{ARCHITECTURE_REFERENCE}.md"
            if routing.count(architecture_target) < 3:
                failures.append(
                    "skill-contract: shared architecture guidance must serve "
                    "technical planning, architecture analysis, and independent review"
                )
            for forbidden in (
                "references/general_implementation.md",
                "references/independent_review.md",
                "references/architecture_analysis.md",
            ):
                if forbidden in routing:
                    failures.append(
                        f"skill-contract: {forbidden} must not be a playbook"
                    )
            for required in GRAPHIFY_ROUTING_REQUIREMENTS:
                if required not in routing:
                    failures.append(
                        "graphify-contract: orchestra routing is missing "
                        f"{required}"
                    )

        repository_context = references / "repository_context.md"
        if repository_context.is_file():
            context_text = repository_context.read_text(encoding="utf-8")
            for required in GRAPHIFY_CONTEXT_REQUIREMENTS:
                if required not in context_text:
                    failures.append(
                        "graphify-contract: repository_context is missing "
                        f"{required}"
                    )

    direct_consumers = {
        "orchestra-phase-commit": ("commit_phase.py", "root directly run"),
        "orchestra-pr-review": (
            "pr.py",
            "observe",
            "independent_review",
            "same implementation owner",
        ),
    }
    for name, required_text in direct_consumers.items():
        skill = root / f"codex/skills/{name}/SKILL.md"
        if not skill.is_file():
            continue
        text = skill.read_text(encoding="utf-8")
        for expected in required_text:
            if expected not in text:
                failures.append(
                    f"skill-contract: {name} must directly consume {expected}"
                )

    runtime = root / "codex/runtime/AGENTS.orchestra.md"
    if runtime.is_file():
        text = runtime.read_text(encoding="utf-8")
        if text.count("<!-- orchestra:start -->") != 1 or text.count(
            "<!-- orchestra:end -->"
        ) != 1:
            failures.append("runtime-contract: managed markers must occur exactly once")
        for target in (
            "$orchestra",
            "$orchestra-delivery-policy",
            "${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml",
            "${CODEX_HOME:-$HOME/.codex}/agents/",
        ):
            if target not in text:
                failures.append(f"runtime-contract: managed block must route to {target}")
        for required in GRAPHIFY_RUNTIME_REQUIREMENTS:
            if required not in text:
                failures.append(
                    f"graphify-contract: managed runtime is missing {required}"
                )
    fallback = "${CODEX_HOME:-$HOME/.codex}"
    for name in SKILL_NAMES:
        skill = root / f"codex/skills/{name}/SKILL.md"
        if skill.is_file() and fallback not in skill.read_text(encoding="utf-8"):
            failures.append(f"runtime-contract: {name} must state the Codex home fallback")
    return failures


def check_direct_sync(root: Path) -> list[str]:
    """Validate the bounded source inventory and direct-sync public contract."""
    failures: list[str] = []
    sync_path = root / "codex/scripts/sync.py"
    if not sync_path.is_file():
        return failures
    text = sync_path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(sync_path))
    except SyntaxError:
        return failures
    constants: dict[str, object] = {}
    commands: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(
            node.targets[0], ast.Name
        ):
            if node.targets[0].id in {
                "SKILLS",
                "AGENTS",
                "LEGACY_AGENTS",
                "HELPERS",
            }:
                try:
                    constants[node.targets[0].id] = ast.literal_eval(node.value)
                except (TypeError, ValueError):
                    pass
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_parser"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        ):
            commands.add(node.args[0].value)
    if commands != {"status", "apply", "uninstall"}:
        failures.append("sync-contract: CLI must expose exactly status, apply, and uninstall")
    if set(constants.get("SKILLS", ())) != set(SKILL_NAMES):
        failures.append("sync-contract: sync inventory must name exactly seven skills")
    if set(constants.get("AGENTS", ())) != set(PROFILE_NAMES):
        failures.append("sync-contract: sync inventory must name exactly four agents")
    if set(constants.get("LEGACY_AGENTS", ())) != set(LEGACY_PROFILE_NAMES):
        failures.append(
            "sync-contract: stale-profile cleanup must be limited to the ten "
            "retired agent names"
        )
    if tuple(constants.get("HELPERS", ())) != (
        "commit_phase.py",
        "policy.py",
        "pr.py",
        "integrate_local.py",
    ):
        failures.append("sync-contract: sync inventory must name exactly four helpers")
    for destination in (
        ".agents/skills/",
        "agents/",
        "orchestra/roles.toml",
        "orchestra/scripts/",
        "orchestra/install-manifest.json",
        "AGENTS.md",
    ):
        if destination not in text:
            failures.append(f"sync-contract: missing destination contract {destination}")
    skill_dirs = sorted(
        path.name for path in (root / "codex/skills").iterdir() if path.is_dir()
    )
    if skill_dirs != sorted(SKILL_NAMES):
        failures.append("sync-contract: source must contain exactly seven skill directories")
    profiles = sorted(path.stem for path in (root / "codex/agents").glob("*.toml"))
    if profiles != sorted(PROFILE_NAMES):
        failures.append("sync-contract: source must contain exactly four agent profiles")
    runtime = root / "codex/runtime/AGENTS.orchestra.md"
    if runtime.is_file():
        runtime_text = runtime.read_text(encoding="utf-8")
        if not runtime_text.startswith("<!-- orchestra:start -->\n") or not runtime_text.endswith(
            "<!-- orchestra:end -->\n"
        ):
            failures.append("sync-contract: runtime source must be exactly one marked block")

    gitignore = root / ".gitignore"
    if gitignore.is_file():
        patterns = set(gitignore.read_text(encoding="utf-8").splitlines())
        required = {
            "graphify-out/*",
            "!graphify-out/graph.json",
            "!graphify-out/graph.html",
            "!graphify-out/GRAPH_REPORT.md",
            "graphify-out/manifest.json",
            "graphify-out/cost.json",
        }
        missing = sorted(required - patterns)
        if missing:
            failures.append(
                "sync-contract: .gitignore is missing Graphify boundaries: "
                + ", ".join(missing)
            )
        if "graphify-out/" in patterns:
            failures.append("sync-contract: graphify-out/ blanket ignore defeats the allowlist")
    return failures


def check_documentation(root: Path) -> list[str]:
    """Validate product identity, roadmap boundary, and timeless documentation."""
    failures: list[str] = []
    readme = root / "README.md"
    if readme.is_file() and IDENTITY not in readme.read_text(encoding="utf-8"):
        failures.append("documentation: README.md is missing the canonical identity")

    roadmap = root / "docs/ROADMAP.md"
    if roadmap.is_file():
        roadmap_text = roadmap.read_text(encoding="utf-8")
        normalized = " ".join(roadmap_text.split())
        for requirement in ROADMAP_REQUIREMENTS:
            if requirement not in normalized:
                failures.append(
                    "documentation: docs/ROADMAP.md is missing required boundary: "
                    f"{requirement}"
                )

        criteria: list[str] = []
        in_distribution_section = False
        for line in roadmap_text.splitlines():
            if line == "## Deferred distribution boundary":
                in_distribution_section = True
                continue
            if in_distribution_section and line.startswith("## "):
                break
            if in_distribution_section and line.startswith("- "):
                criteria.append(line[2:])
        if tuple(criteria) != DEFERRED_DISTRIBUTION_CRITERIA:
            failures.append(
                "documentation: docs/ROADMAP.md must contain exactly the six "
                "approved deferred distribution criteria in order"
            )

    for relative in PERMANENT_DOCS:
        path = root / relative
        if not path.is_file():
            continue
        normalized = " ".join(path.read_text(encoding="utf-8").split())
        for label, pattern in HISTORICAL_NARRATIVES:
            if pattern.search(normalized):
                failures.append(f"documentation: {relative} contains {label}")
                break
    return failures


def check_hook(root: Path) -> list[str]:
    """Keep the hook an executable wrapper around quick conformance."""
    hook = root / ".githooks/pre-commit"
    if not hook.is_file():
        return []
    failures: list[str] = []
    if hook.read_text(encoding="utf-8") != HOOK_CONTENT:
        failures.append(
            "hook-contract: .githooks/pre-commit must only invoke "
            "validate_suite.py --quick"
        )
    if not os.access(hook, os.X_OK):
        failures.append("hook-contract: make .githooks/pre-commit executable")
    return failures


def check_python_syntax(root: Path) -> list[str]:
    """Parse the Python implementation and its tests without executing them."""
    failures: list[str] = []
    for base in (root / "codex/scripts", root / "codex/tests"):
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeError) as error:
                relative = path.relative_to(root).as_posix()
                failures.append(f"python-syntax: {relative}: {error}")
    return failures


def check_python_tests(root: Path) -> list[str]:
    """Run the repository's standard-library unit tests in full mode."""
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "codex/tests",
            "-p",
            "test_*.py",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if result.returncode == 0:
        return []
    output = "\n".join(
        part.strip() for part in (result.stdout, result.stderr) if part.strip()
    )
    return [f"python-tests: unittest discovery failed\n{output}"]


Check = Callable[[Path], list[str]]
QUICK_CHECKS: tuple[Check, ...] = (
    check_required_paths,
    check_distribution_boundary,
    check_delivery_config,
    check_documentation,
    check_hook,
    check_roles_and_profiles,
    check_skills_and_runtime,
    check_direct_sync,
)
FULL_CHECKS: tuple[Check, ...] = QUICK_CHECKS + (
    check_python_syntax,
    check_python_tests,
)


def validate(root: Path, mode: str) -> list[str]:
    """Run the checks registered for mode and return actionable failures."""
    checks = QUICK_CHECKS if mode == "quick" else FULL_CHECKS
    failures: list[str] = []
    for check in checks:
        failures.extend(check(root))
        if failures:
            break
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--quick", action="store_true", help="run hook-safe checks")
    mode.add_argument("--full", action="store_true", help="run all local checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = "quick" if args.quick else "full"
    root = Path(__file__).resolve().parents[2]
    failures = validate(root, mode)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"Conformance failed with {len(failures)} actionable issue(s).")
        return 1
    check_count = len(QUICK_CHECKS if mode == "quick" else FULL_CHECKS)
    print(f"OK: {mode} conformance passed ({check_count} checks).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
