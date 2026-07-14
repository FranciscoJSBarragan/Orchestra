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
    "codex/scripts/commit_phase.py",
    "codex/scripts/policy.py",
    "codex/scripts/pr.py",
    "codex/scripts/integrate_local.py",
    "codex/config/roles.toml",
    "codex/runtime/AGENTS.orchestra.md",
    "codex/agents/implementation_worker.toml",
    "codex/agents/reviewer.toml",
    "codex/agents/phase_committer.toml",
    "codex/agents/repo_context_explorer.toml",
    "codex/agents/planner.toml",
    "codex/agents/plan_scope_auditor.toml",
    "codex/agents/debugging_investigator.toml",
    "codex/agents/web_researcher.toml",
    "codex/agents/browser_acceptance_tester.toml",
    "codex/agents/pr_polling_specialist.toml",
    "codex/agents/pr_triage_specialist.toml",
    "codex/skills/orchestra/SKILL.md",
    "codex/skills/orchestra/agents/openai.yaml",
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
    "repo_context_explorer",
    "planner",
    "plan_scope_auditor",
    "implementation_worker",
    "reviewer",
    "debugging_investigator",
    "web_researcher",
    "browser_acceptance_tester",
    "phase_committer",
    "pr_polling_specialist",
    "pr_triage_specialist",
)

EXPECTED_TIER_ROLES = {
    "light": {
        "implementation_worker",
        "reviewer",
        "phase_committer",
        "pr_polling_specialist",
        "pr_triage_specialist",
    },
    "standard": {
        "planner",
        "plan_scope_auditor",
        "implementation_worker",
        "reviewer",
        "debugging_investigator",
        "repo_context_explorer",
        "web_researcher",
        "browser_acceptance_tester",
        "phase_committer",
        "pr_polling_specialist",
        "pr_triage_specialist",
    },
    "critical": {
        "planner",
        "plan_scope_auditor",
        "implementation_worker",
        "reviewer",
        "reviewer_second_pass",
        "debugging_investigator",
        "repo_context_explorer",
        "web_researcher",
        "browser_acceptance_tester",
        "phase_committer",
        "pr_polling_specialist",
        "pr_triage_specialist",
    },
}

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
    if not isinstance(tiers, dict) or set(tiers) != set(EXPECTED_TIER_ROLES):
        failures.append(
            "role-contract: roles.toml must define light, standard, and critical"
        )
    else:
        for tier, expected_roles in EXPECTED_TIER_ROLES.items():
            actual_roles = tiers.get(tier)
            if not isinstance(actual_roles, dict) or set(actual_roles) != expected_roles:
                failures.append(f"role-contract: unexpected {tier} role set")
                continue
            for role, assignment in actual_roles.items():
                if not isinstance(assignment, dict) or set(assignment) != {
                    "model",
                    "reasoning_effort",
                }:
                    failures.append(
                        f"role-contract: {tier}.{role} needs model and reasoning_effort"
                    )
                    continue
                if assignment["model"] not in VALID_MODELS:
                    failures.append(f"role-contract: {tier}.{role} has invalid model")
                if assignment["reasoning_effort"] not in {
                    "low",
                    "medium",
                    "high",
                    "xhigh",
                    "max",
                }:
                    failures.append(
                        f"role-contract: {tier}.{role} has invalid reasoning_effort"
                    )

    agents = root / "codex/agents"
    actual_profiles = sorted(path.stem for path in agents.glob("*.toml"))
    if actual_profiles != sorted(PROFILE_NAMES):
        failures.append("profile-contract: current routing must define exactly eleven profiles")
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

    if isinstance(tiers, dict):
        for tier, roles in tiers.items():
            if not isinstance(roles, dict):
                continue
            for role in roles:
                consumer = (
                    "orchestra-pr-review"
                    if role in {"pr_polling_specialist", "pr_triage_specialist"}
                    else "orchestra"
                )
                consumer_path = root / f"codex/skills/{consumer}/SKILL.md"
                if not consumer_path.is_file():
                    continue
                routing = consumer_path.read_text(encoding="utf-8")
                if f"`{role}`" not in routing:
                    failures.append(
                        f"role-contract: {tier}.{role} is not consumed by {consumer} routing"
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

    runtime = root / "codex/runtime/AGENTS.orchestra.md"
    if runtime.is_file():
        text = runtime.read_text(encoding="utf-8")
        if text.count("<!-- orchestra:start -->") != 1 or text.count(
            "<!-- orchestra:end -->"
        ) != 1:
            failures.append("runtime-contract: managed markers must occur exactly once")
        for target in (
            "codex/skills/orchestra/SKILL.md",
            "codex/skills/orchestra-delivery-policy/SKILL.md",
            "codex/config/roles.toml",
            "codex/agents/",
        ):
            if target not in text:
                failures.append(f"runtime-contract: managed block must route to {target}")
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
