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
    ".agent/backend-testing.md",
    ".githooks/pre-commit",
    "codex/scripts/validate_suite.py",
    "codex/scripts/sync.py",
    "codex/scripts/package_plugin.py",
    "codex/tests/test_package_plugin.py",
    "packaging/orchestra/.codex-plugin/plugin.json",
    "packaging/README.md",
    "codex/skills/orchestra/runtime.md",
    "codex/scripts/coordination.py",
    "codex/scripts/task_state.py",
    "codex/scripts/task_control.py",
    "codex/scripts/task_mcp.py",
    "codex/scripts/commit_phase.py",
    "codex/scripts/delegate.py",
    "codex/scripts/adopt_worktree.py",
    "codex/scripts/policy.py",
    "codex/scripts/pr.py",
    "codex/scripts/integrate_local.py",
    "codex/scripts/_common.py",
    "codex/config/roles.native.toml",
    "codex/config/execution-presets.toml",
    "codex/runtime/AGENTS.orchestra.md",
    "codex/agents/orchestra_analyst.toml",
    "codex/agents/orchestra_implementation_worker.toml",
    "codex/agents/orchestra_reviewer.toml",
    "codex/agents/orchestra_verifier.toml",
    "codex/skills/orchestra/SKILL.md",
    "codex/skills/orchestra/agents/openai.yaml",
    "codex/skills/orchestra-task/SKILL.md",
    "codex/skills/orchestra-task/agents/openai.yaml",
    "codex/control/orchestra_control/__init__.py",
    "codex/control/orchestra_control/db.py",
    "codex/control/orchestra_control/service.py",
    "codex/control/orchestra_control/cli.py",
    "codex/control/orchestra_control/mcp.py",
    "codex/skills/orchestra-project-start/SKILL.md",
    "codex/skills/orchestra-project-start/agents/openai.yaml",
    "codex/skills/orchestra-repo-onboard/SKILL.md",
    "codex/skills/orchestra-repo-onboard/agents/openai.yaml",
    "codex/skills/orchestra-delegate/SKILL.md",
    "codex/skills/orchestra-delegate/agents/openai.yaml",
    "codex/skills/orchestra-lite/SKILL.md",
    "codex/skills/orchestra-lite/agents/openai.yaml",
    "codex/skills/orchestra-lite/kickoff-template.md",
    "codex/skills/orchestra-lite/result-example.json",
    "codex/tests/test_orchestra_lite.py",
    "codex/tests/fixtures/orchestra-lite/README.md",
    "codex/tests/fixtures/orchestra-lite/make_fixture.py",
    "codex/tests/fixtures/orchestra-lite/gh_shim.py",
    "codex/skills/orchestra/references/repository_context.md",
    "codex/skills/orchestra/references/web_research.md",
    "codex/skills/orchestra/references/technical_planning.md",
    "codex/skills/orchestra/references/difficult_debugging.md",
    "codex/skills/orchestra/references/frontend_implementation.md",
    "codex/skills/orchestra/references/browser_acceptance.md",
    "codex/skills/orchestra/references/runtime_verification.md",
    "codex/skills/orchestra/references/architecture_guidance.md",
    "codex/skills/orchestra/references/shared_conduct.md",
    "codex/skills/orchestra/references/host_codex.md",
    "codex/skills/orchestra-role-analyst/SKILL.md",
    "codex/skills/orchestra-role-analyst/agents/openai.yaml",
    "codex/skills/orchestra-role-implementer/SKILL.md",
    "codex/skills/orchestra-role-implementer/agents/openai.yaml",
    "codex/skills/orchestra-role-reviewer/SKILL.md",
    "codex/skills/orchestra-role-reviewer/agents/openai.yaml",
    "codex/skills/orchestra-role-verifier/SKILL.md",
    "codex/skills/orchestra-role-verifier/agents/openai.yaml",
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
    "codex/tests/test_delegate.py",
    "codex/tests/test_coordination.py",
    "codex/tests/test_task_control.py",
    "codex/tests/test_adopt_worktree.py",
    "codex/tests/test_routing_activation.py",
    "codex/tests/test_planned_flow.py",
    "codex/tests/test_validate_suite.py",
    "codex/tests/test_delivery_policy.py",
    "codex/tests/test_pr_flow.py",
    "codex/tests/test_local_integration.py",
    "codex/tests/test_sync.py",
    "codex/tests/test_cursor_host.py",
    "codex/tests/test_grok_host.py",
    "hosts/cursor/config/roles.cursor.toml",
    "hosts/cursor/references/spawn.md",
    "hosts/cursor/plugin/.cursor-plugin/plugin.json",
    "hosts/cursor/plugin/commands/orchestra.md",
    "hosts/cursor/plugin/hooks/hooks.json",
    "hosts/cursor/plugin/scripts/session_identity.py",
    "hosts/grok/config/roles.grok.toml",
    "hosts/grok/references/spawn.md",
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
    "Orchestra is a cost-efficient, multi-agent software-delivery workflow for Codex,\n"
    "Cursor, and Grok Build."
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
    "Local plugin packaging is supported.",
    "does not prescribe an implementation design.",
)

HOOK_CONTENT = """#!/bin/sh
set -eu
REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$REPO_ROOT/codex/scripts/validate_suite.py" --quick
"""

ROLE_SKILL_BY_PROFILE = {
    "orchestra_analyst": "orchestra-role-analyst",
    "orchestra_implementation_worker": "orchestra-role-implementer",
    "orchestra_reviewer": "orchestra-role-reviewer",
    "orchestra_verifier": "orchestra-role-verifier",
}
PROFILE_NAMES = (
    "orchestra_analyst",
    "orchestra_implementation_worker",
    "orchestra_reviewer",
    "orchestra_verifier",
)

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
    "analyst",
    "browser_acceptance_tester",
    "debugging_investigator",
    "frontend_implementation_worker",
    "implementation_worker",
    "phase_committer",
    "plan_scope_auditor",
    "planner",
    "pr_polling_specialist",
    "pr_triage_specialist",
    "repo_context_explorer",
    "reviewer",
    "verifier",
    "web_researcher",
)

SKILL_NAMES = (
    "orchestra",
    "orchestra-task",
    "orchestra-project-start",
    "orchestra-repo-onboard",
    "orchestra-delegate",
    "orchestra-lite",
    "orchestra-phase-commit",
    "orchestra-delivery-policy",
    "orchestra-pr-open",
    "orchestra-pr-review",
    "orchestra-pr-merge",
    "orchestra-local-integrate",
    "orchestra-role-analyst",
    "orchestra-role-implementer",
    "orchestra-role-reviewer",
    "orchestra-role-verifier",
)
LITE_KICKOFF_MARKER = "ORCHESTRA_LITE_SPEC"
LITE_MANDATORY_FIELDS = (
    "Repo",
    "Base",
    "Slug",
    "Rama",
    "PR",
    "Autorización",
    "Objetivo",
    "Aceptación",
)
LITE_RESULT_KEYS = (
    "Estado",
    "PR",
    "Rama",
    "Publicada",
    "Commits",
    "Checks",
    "CI",
    "Decisiones tomadas",
    "Riesgos / no hecho",
    "Pendiente para merge",
    "Bloqueo",
)
LITE_CHECK_KEYS = ("Comando", "Resultado", "Código de salida")
VALID_MODELS = {
    "gpt-6-astra",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-5.6-luna",
}


def check_required_paths(root: Path) -> list[str]:
    """Ensure every current conformance consumer is present and tracked."""
    failures = [
        f"required-path: missing {relative}"
        for relative in REQUIRED_PATHS
        if not (root / relative).is_file()
    ]
    git_dir = root / ".git"
    if not git_dir.exists():
        return failures
    try:
        listed = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=True,
            capture_output=True,
        ).stdout
    except OSError as exc:
        failures.append(
            "required-path: unable to verify tracked paths via git ls-files "
            f"({type(exc).__name__})"
        )
        return failures
    except subprocess.CalledProcessError as exc:
        failures.append(
            "required-path: unable to verify tracked paths via git ls-files "
            f"(exit {exc.returncode})"
        )
        return failures
    tracked = set(listed.decode().split("\0")) - {""}
    failures.extend(
        f"required-path: untracked {relative}"
        for relative in REQUIRED_PATHS
        if (root / relative).is_file() and relative not in tracked
    )
    return failures


CAPABILITY_PROFILES = {
    "repository_context": "orchestra_analyst",
    "web_research": "orchestra_analyst",
    "technical_planning": "orchestra_analyst",
    "architecture_analysis": "orchestra_analyst",
    "difficult_debugging": "orchestra_analyst",
    "general_implementation": "orchestra_implementation_worker",
    "frontend_implementation": "orchestra_implementation_worker",
    "independent_review": "orchestra_reviewer",
    "browser_acceptance": "orchestra_verifier",
    "runtime_verification": "orchestra_verifier",
}
EXPECTED_TIERS = {
    "native": {"standard", "critical"},
}
REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max"}


def check_distribution_boundary(root: Path) -> list[str]:
    """Keep generated plugin manifests out of the canonical source roots."""
    failures: list[str] = []
    migration = root / "docs/MIGRATION.md"
    if migration.exists():
        failures.append("distribution-boundary: remove docs/MIGRATION.md")

    for relative in (Path(".codex-plugin"), Path("codex/.codex-plugin")):
        if (root / relative).exists():
            failures.append(
                f"distribution-boundary: generated manifest belongs in a package, not {relative.as_posix()}"
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
    roles_paths = {
        "native": root / "codex/config/roles.native.toml",
    }
    if not all(path.is_file() for path in roles_paths.values()):
        return []

    failures: list[str] = []
    # Use the runtime resolver's config validation rather than a second schema.
    preset_check = subprocess.run(
        [sys.executable, str(root / "codex/scripts/delegate.py"),
         "--presets-file", str(root / "codex/config/execution-presets.toml"),
         "--preset", "standard-delegate", "--host", "codex",
         "--capability", "repository_context", "--resolve-only"],
        capture_output=True, text=True, check=False,
    )
    if preset_check.returncode:
        failures.append(f"role-contract: execution preset is invalid: {preset_check.stdout.strip()}")
    tiers_by_config: dict[str, dict[str, object]] = {}
    for modelconfig, roles_path in roles_paths.items():
        relative = roles_path.relative_to(root).as_posix()
        try:
            roles = tomllib.loads(roles_path.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeError) as error:
            failures.append(f"role-contract: {relative} is invalid: {error}")
            continue
        if set(roles) != {"tiers"}:
            failures.append(f"role-contract: {relative} must contain tiers only")
        tiers = roles.get("tiers")
        expected_tier_names = EXPECTED_TIERS[modelconfig]
        if not isinstance(tiers, dict) or set(tiers) != expected_tier_names:
            expected_tiers = ", ".join(sorted(expected_tier_names))
            failures.append(
                f"role-contract: {relative} must define {expected_tiers}"
            )
            continue
        tiers_by_config[modelconfig] = tiers
        for tier in expected_tier_names:
            actual_assignments = tiers.get(tier)
            if not isinstance(actual_assignments, dict) or set(
                actual_assignments
            ) != set(CAPABILITY_PROFILES):
                failures.append(
                    f"role-contract: unexpected {modelconfig}.{tier} capability set"
                )
                continue
            for capability, assignment in actual_assignments.items():
                if not isinstance(assignment, dict) or set(assignment) != {
                    "profile",
                    "model",
                    "reasoning_effort",
                }:
                    failures.append(
                        f"role-contract: {modelconfig}.{tier}.{capability} needs "
                        "profile, model, and reasoning_effort"
                    )
                    continue
                if assignment["profile"] != CAPABILITY_PROFILES[capability]:
                    failures.append(
                        f"role-contract: {modelconfig}.{tier}.{capability} does "
                        "not match the approved assignment matrix"
                    )
                if assignment["profile"] not in PROFILE_NAMES:
                    failures.append(
                        f"role-contract: {modelconfig}.{tier}.{capability} has "
                        "invalid profile"
                    )
                if assignment["model"] not in VALID_MODELS:
                    failures.append(
                        f"role-contract: {modelconfig}.{tier}.{capability} has "
                        "invalid model"
                    )
                if assignment["reasoning_effort"] not in {
                    "low",
                    "medium",
                    "high",
                    "xhigh",
                    "max",
                }:
                    failures.append(
                        f"role-contract: {modelconfig}.{tier}.{capability} has "
                        "invalid reasoning_effort"
                    )
                if (
                    assignment["model"] == "gpt-5.6-sol"
                    and assignment["reasoning_effort"] == "xhigh"
                ):
                    failures.append(
                        f"role-contract: {modelconfig}.{tier}.{capability} must "
                        "not use Sol xhigh"
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
        role_skill = ROLE_SKILL_BY_PROFILE[name]
        if f".agents/skills/{role_skill}/SKILL.md" not in instructions:
            failures.append(
                f"profile-contract: {name} must read its role skill {role_skill}"
            )
        role_path = root / f"codex/skills/{role_skill}/SKILL.md"
        if role_path.is_file():
            role_text = role_path.read_text(encoding="utf-8")
            for heading in ("## Input", "## Output", "## Stop conditions"):
                if heading not in role_text:
                    failures.append(
                        f"profile-contract: {role_skill} is missing {heading}"
                    )
            if "shared_conduct.md" not in role_text:
                failures.append(
                    f"profile-contract: {role_skill} must reference shared conduct"
                )

    if len(declared_names) != len(set(declared_names)):
        failures.append("profile-contract: profile names must be unique")

    behavior_sources = [
        *(agents / f"{name}.toml" for name in PROFILE_NAMES),
        *(root / f"codex/skills/{name}/SKILL.md" for name in SKILL_NAMES),
        root / "codex/runtime/AGENTS.orchestra.md",
    ]
    for path in behavior_sources:
        if path.is_file() and re.search(r"\bgpt-\d", path.read_text(encoding="utf-8")):
            failures.append(
                "role-contract: model assignments must exist only in roles.*.toml; "
                f"found one in {path.relative_to(root)}"
            )

    routing_path = root / "codex/skills/orchestra/SKILL.md"
    if routing_path.is_file() and tiers_by_config:
        routing = routing_path.read_text(encoding="utf-8")
        capabilities = {
            capability
            for tiers in tiers_by_config.values()
            for assignments in tiers.values()
            if isinstance(assignments, dict)
            for capability in assignments
        }
        for capability in capabilities:
            if f"`{capability}`" not in routing:
                failures.append(
                    f"role-contract: {capability} is not consumed by orchestra routing"
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


def _local_markdown_links(text: str) -> list[str]:
    return [
        target
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text)
        if not target.startswith(("#", "http://", "https://"))
    ]


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

        for target in _local_markdown_links(text):
            resolved = (skill.parent / target.split("#", 1)[0]).resolve()
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
            if name == "orchestra-project-start" and (
                "allow_implicit_invocation: true" not in ui
            ):
                failures.append(
                    "skill-contract: orchestra-project-start must allow implicit invocation"
                )

    references = root / "codex/skills/orchestra/references"
    expected_references = {
        *(f"{name}.md" for name in PLAYBOOK_NAMES),
        f"{ARCHITECTURE_REFERENCE}.md",
        "shared_conduct.md",
        "host_codex.md",
    }
    if not references.is_dir():
        failures.append("skill-contract: orchestra internal references are missing")
    else:
        actual_references = {entry.name for entry in references.iterdir()}
        if actual_references != expected_references or any(
            not entry.is_file() or entry.is_symlink() for entry in references.iterdir()
        ):
            failures.append(
                "skill-contract: orchestra must contain exactly seven playbooks, "
                "one architecture reference, one shared conduct reference, "
                "and the Codex spawn adapter"
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
            for forbidden in (
                "references/general_implementation.md",
                "references/independent_review.md",
                "references/architecture_analysis.md",
            ):
                if forbidden in routing:
                    failures.append(
                        f"skill-contract: {forbidden} must not be a playbook"
                    )
    guidance = (references / f"{ARCHITECTURE_REFERENCE}.md").resolve()
    guidance_consumers = [
        *(f"codex/skills/{name}/SKILL.md" for name in (
            "orchestra",
            "orchestra-role-analyst",
            "orchestra-role-implementer",
            "orchestra-role-reviewer",
            "orchestra-role-verifier",
            "orchestra-repo-onboard",
            "orchestra-project-start",
        )),
        *(f"codex/skills/orchestra/references/{name}.md" for name in (
            "repository_context",
            "technical_planning",
            "runtime_verification",
            "browser_acceptance",
        )),
    ]
    for relative in guidance_consumers:
        consumer = root / relative
        if not consumer.is_file():
            continue  # Required-path validation owns missing source files.
        targets = {
            (consumer.parent / target.split("#", 1)[0]).resolve()
            for target in _local_markdown_links(consumer.read_text(encoding="utf-8"))
        }
        if guidance not in targets:
            failures.append(
                f"skill-contract: {relative} must link to shared engineering guidance "
                f"({ARCHITECTURE_REFERENCE}.md)"
            )

    direct_consumers = {
        "orchestra": (
            "task_state.py",
            "coordination.py",
        ),
        "orchestra-phase-commit": ("commit_phase.py",),
        "orchestra-pr-review": (
            "pr.py",
            "observe",
            "independent_review",
        ),
        "orchestra-pr-open": (
            "pr.py",
            "--expected-task-revision",
        ),
        "orchestra-pr-merge": (
            "--base-worktree",
            "--task-branch",
            "--base-branch",
            "--expected-task-revision",
            "--remote",
            "lease",
        ),
        "orchestra-local-integrate": (
            "--task-worktree",
            "--base-worktree",
            "--expected-task-revision",
            "--checkout-mode",
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
        if "$orchestra" not in text:
            failures.append("runtime-contract: managed block must route to $orchestra")
    orchestra_home = "${ORCHESTRA_HOME:-$HOME/.orchestra}"
    exempt = {"orchestra-project-start", *ROLE_SKILL_BY_PROFILE.values()}
    for name in (skill for skill in SKILL_NAMES if skill not in exempt):
        skill = root / f"codex/skills/{name}/SKILL.md"
        if skill.is_file() and orchestra_home not in skill.read_text(encoding="utf-8"):
            failures.append(f"runtime-contract: {name} must state the Orchestra home")
    return failures


def check_orchestra_lite(root: Path) -> list[str]:
    """Pin the machine-consumed Lite kickoff and result shapes without freezing prose."""
    failures: list[str] = []
    skill_dir = root / "codex/skills/orchestra-lite"
    skill = skill_dir / "SKILL.md"
    template = skill_dir / "kickoff-template.md"
    example = skill_dir / "result-example.json"
    workflow = root / "docs/WORKFLOW.md"
    if not all(path.is_file() for path in (skill, template, example, workflow)):
        return failures  # Required-path validation owns missing files.

    skill_text = skill.read_text(encoding="utf-8")
    links = {target.split("#", 1)[0] for target in _local_markdown_links(skill_text)}
    for resource in (template.name, example.name):
        if resource not in links:
            failures.append(f"lite-contract: orchestra-lite must link {resource}")
    section = "Orchestra Lite companion"
    if f"## {section}" not in workflow.read_text(encoding="utf-8"):
        failures.append(f"lite-contract: docs/WORKFLOW.md must define the {section} section")
    if section not in skill_text:
        failures.append(f"lite-contract: orchestra-lite must route to WORKFLOW {section}")

    template_text = template.read_text(encoding="utf-8")
    template_lines = {line.split(":", 1)[0].strip() for line in template_text.splitlines()}
    if LITE_KICKOFF_MARKER not in template_lines:
        failures.append(f"lite-contract: kickoff template must start with {LITE_KICKOFF_MARKER}")
    for field in LITE_MANDATORY_FIELDS:
        if field not in template_lines:
            failures.append(f"lite-contract: kickoff template is missing mandatory field {field}")

    try:
        payload = json.loads(example.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as error:
        return [*failures, f"lite-contract: result-example.json is invalid JSON: {error}"]
    if not isinstance(payload, dict) or set(payload) != set(LITE_RESULT_KEYS):
        failures.append(
            "lite-contract: result-example.json must contain exactly the fixed result keys"
        )
        return failures
    branch = payload["Rama"]
    if not isinstance(branch, dict) or set(branch) != {"Nombre", "SHA"}:
        failures.append("lite-contract: result Rama must be an object with Nombre and SHA")
    checks = payload["Checks"]
    if not isinstance(checks, list) or any(
        not isinstance(item, dict) or set(item) != set(LITE_CHECK_KEYS) for item in checks
    ):
        failures.append(
            "lite-contract: every result Checks item must record Comando, Resultado, and Código de salida"
        )
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
                "MODELCONFIGS",
                "HOSTS",
                "PERMISSION_PROFILE",
                "GUARDIAN_MIN_VERSION",
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
        failures.append("sync-contract: sync inventory must match the canonical skill set")
    if set(constants.get("AGENTS", ())) != set(PROFILE_NAMES):
        failures.append("sync-contract: sync inventory must name exactly four agents")
    if set(constants.get("LEGACY_AGENTS", ())) != set(LEGACY_PROFILE_NAMES):
        failures.append(
            "sync-contract: stale-profile cleanup must be limited to the "
            f"{len(LEGACY_PROFILE_NAMES)} retired agent names"
        )
    if tuple(constants.get("HELPERS", ())) != (
        "coordination.py",
        "task_state.py",
        "task_control.py",
        "task_mcp.py",
        "commit_phase.py",
        "delegate.py",
        "adopt_worktree.py",
        "policy.py",
        "pr.py",
        "integrate_local.py",
        "_common.py",
    ):
        failures.append("sync-contract: sync inventory must match the canonical helper set")
    if tuple(constants.get("MODELCONFIGS", ())) != ("native",):
        failures.append(
            "sync-contract: modelconfig choices must be native only"
        )
    if tuple(constants.get("HOSTS", ())) != ("codex", "cursor", "grok", "all"):
        failures.append(
            "sync-contract: host choices must be exactly codex, cursor, grok, and all"
        )
    if constants.get("PERMISSION_PROFILE") != ":workspace":
        failures.append(
            "sync-contract: installs must select the built-in workspace profile"
        )
    if tuple(constants.get("GUARDIAN_MIN_VERSION", ())) != (0, 146, 0):
        failures.append(
            "sync-contract: Guardian installs must require Codex 0.146.0 or later"
        )
    if "b'approval_policy = \"on-request\"'" not in text:
        failures.append(
            "sync-contract: managed permissions must keep approvals interactive"
        )
    if "b'approvals_reviewer = \"auto_review\"'" not in text:
        failures.append(
            "sync-contract: managed approvals must route through Auto-review"
        )
    if '"--modelconfig"' not in text:
        failures.append("sync-contract: CLI must expose --modelconfig")
    if '"--worktree-root"' not in text:
        failures.append("sync-contract: CLI must expose --worktree-root")
    if '"--checkout-mode"' not in text:
        failures.append("sync-contract: CLI must expose --checkout-mode")
    if '"--host"' not in text:
        failures.append("sync-contract: CLI must expose --host")
    for destination in (
        ".agents/skills/",
        "agents/",
        "orchestra/roles.toml",
        "orchestra/worktree-root",
        "orchestra/checkout-mode",
        "orchestra/scripts/",
        "install-manifest.json",
        "scripts/",
        "hosts/cursor/roles.toml",
        "hosts/grok/roles.toml",
        ".cursor/plugins/local/orchestra",
        "AGENTS.md",
        "config.toml",
    ):
        if destination not in text:
            failures.append(f"sync-contract: missing destination contract {destination}")
    skill_dirs = sorted(
        path.name for path in (root / "codex/skills").iterdir() if path.is_dir()
    )
    if skill_dirs != sorted(SKILL_NAMES):
        failures.append("sync-contract: source must contain exactly the supported skill directories")
    profiles = sorted(path.stem for path in (root / "codex/agents").glob("*.toml"))
    if profiles != sorted(PROFILE_NAMES):
        failures.append("sync-contract: source must contain exactly four agent profiles")
    role_sources = sorted(
        path.name for path in (root / "codex/config").glob("roles.*.toml")
    )
    if role_sources != ["roles.native.toml"]:
        failures.append(
            "sync-contract: source must contain only the native Codex role matrix"
        )
    runtime = root / "codex/runtime/AGENTS.orchestra.md"
    if runtime.is_file():
        runtime_text = runtime.read_text(encoding="utf-8")
        if not runtime_text.startswith("<!-- orchestra:start -->\n") or not runtime_text.endswith(
            "<!-- orchestra:end -->\n"
        ):
            failures.append("sync-contract: runtime source must be exactly one marked block")

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


CURSOR_CAPABILITIES = (
    "repository_context",
    "web_research",
    "runtime_verification",
    "browser_acceptance",
    "technical_planning",
    "architecture_analysis",
    "difficult_debugging",
    "general_implementation",
    "frontend_implementation",
    "independent_review",
)
CURSOR_COMPOSER_FAST_CAPABILITIES = {
    "repository_context",
    "web_research",
    "runtime_verification",
}
ASSIGNMENT_FIELDS = {"profile", "subagent_type", "model", "effort"}


def _cursor_assignment_failures(
    tier: str,
    assignments: object,
    expected_model_effort: Callable[[str], tuple[str, str, str]],
) -> list[str]:
    failures: list[str] = []
    if not isinstance(assignments, dict) or set(assignments) != set(CURSOR_CAPABILITIES):
        return [
            f"cursor-contract: {tier} must define all ten capabilities and no extras"
        ]
    for capability, assignment in assignments.items():
        if not isinstance(assignment, dict) or set(assignment) != ASSIGNMENT_FIELDS:
            failures.append(
                f"cursor-contract: {tier}.{capability} needs profile, "
                "subagent_type, model, and effort"
            )
            continue
        model, effort, worker = expected_model_effort(capability)
        if assignment["model"] != model or assignment["effort"] != effort:
            failures.append(
                f"cursor-contract: {tier}.{capability} must be {model} {effort}"
            )
        if assignment["subagent_type"] != worker:
            failures.append(
                f"cursor-contract: {tier}.{capability} must dispatch {worker}"
            )
        if assignment["profile"] not in PROFILE_NAMES:
            failures.append(
                f"cursor-contract: {tier}.{capability} has an invalid profile"
            )
    return failures


def check_cursor_host(root: Path) -> list[str]:
    """Validate the Cursor adapter inventory and spawn contract."""
    failures: list[str] = []
    roles_path = root / "hosts/cursor/config/roles.cursor.toml"
    spawn_path = root / "hosts/cursor/references/spawn.md"
    hooks_path = root / "hosts/cursor/plugin/hooks/hooks.json"
    identity_path = root / "hosts/cursor/plugin/scripts/session_identity.py"
    if not all(path.is_file() for path in (roles_path, spawn_path, hooks_path, identity_path)):
        return failures
    try:
        roles = tomllib.loads(roles_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeError) as error:
        return [f"cursor-contract: roles.cursor.toml is invalid: {error}"]
    tiers = roles.get("tiers")
    if not isinstance(tiers, dict) or set(tiers) != {"minimal", "standard", "critical"}:
        failures.append(
            "cursor-contract: roles.cursor.toml must assign minimal, standard, and critical"
        )
        return failures

    def minimal_contract(capability: str) -> tuple[str, str, str]:
        if capability in CURSOR_COMPOSER_FAST_CAPABILITIES:
            return "composer-2.5-fast", "fast", "composer-fast-worker"
        if capability == "browser_acceptance":
            return "gpt-5.6-luna", "high", "luna-worker"
        return "cursor-grok-4.6", "high", "grok-worker"

    def standard_contract(capability: str) -> tuple[str, str, str]:
        if capability in CURSOR_COMPOSER_FAST_CAPABILITIES:
            return "composer-2.5-fast", "fast", "composer-fast-worker"
        if capability == "browser_acceptance":
            return "gpt-5.6-luna", "xhigh", "luna-worker"
        if capability in {"technical_planning", "architecture_analysis"}:
            return "claude-fable-5-1", "low", "generalPurpose"
        if capability in {"difficult_debugging", "independent_review"}:
            return "gpt-5.6-sol", "medium", "sol-worker"
        if capability in {"general_implementation", "frontend_implementation"}:
            return "cursor-grok-4.6", "high", "grok-worker"
        return "", "", ""

    def critical_contract(capability: str) -> tuple[str, str, str]:
        if capability in CURSOR_COMPOSER_FAST_CAPABILITIES:
            return "composer-2.5-fast", "fast", "composer-fast-worker"
        if capability == "browser_acceptance":
            return "gpt-5.6-luna", "xhigh", "luna-worker"
        if capability in {"technical_planning", "architecture_analysis"}:
            return "claude-fable-5-1", "medium", "generalPurpose"
        if capability in {"difficult_debugging", "independent_review"}:
            return "gpt-5.6-sol", "high", "sol-worker"
        if capability in {"general_implementation", "frontend_implementation"}:
            return "cursor-grok-4.6", "xhigh", "grok-worker"
        return "", "", ""

    failures.extend(_cursor_assignment_failures("minimal", tiers.get("minimal"), minimal_contract))
    failures.extend(
        _cursor_assignment_failures("standard", tiers.get("standard"), standard_contract)
    )
    failures.extend(
        _cursor_assignment_failures("critical", tiers.get("critical"), critical_contract)
    )
    spawn = " ".join(spawn_path.read_text(encoding="utf-8").split())
    for required in (
        "Task",
        "run_in_background",
        "composer-fast-worker",
        "composer-2.5-fast",
        "luna-worker",
        "grok-worker",
        "sol-worker",
        "cursor-grok-4.6-high",
        "cursor-grok-4.6-xhigh",
        "gpt-5.6-luna-xhigh",
        "claude-fable-5-1-thinking-low",
        "claude-fable-5-1-thinking-medium",
        "gpt-5.6-sol-medium",
        "gpt-5.6-sol-high",
        "generalPurpose",
        "plugin-browser-use-browser-use",
        "Browser Use",
    ):
        if required not in spawn:
            failures.append(f"cursor-contract: spawn.md must name {required}")
    if "map to Playwright" in spawn or "maps to Playwright" in spawn:
        failures.append(
            "cursor-contract: spawn.md must not map Cursor routes to Playwright"
        )
    try:
        hooks = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as error:
        failures.append(f"cursor-contract: hooks.json is invalid: {error}")
    else:
        expected_hooks = {
            "version": 1,
            "hooks": {
                "sessionStart": [
                    {"command": "python3 ./scripts/session_identity.py"}
                ]
            },
        }
        if hooks != expected_hooks:
            failures.append(
                "cursor-contract: sessionStart must invoke the identity bridge exactly once"
            )
    identity = identity_path.read_text(encoding="utf-8")
    for required in (
        "conversation_id",
        "session_id",
        "ORCHESTRA_HOST_THREAD_ID",
        "return 2",
    ):
        if required not in identity:
            failures.append(
                f"cursor-contract: session identity bridge must name {required}"
            )
    return failures


GROK_CAPABILITIES = CURSOR_CAPABILITIES


def check_grok_host(root: Path) -> list[str]:
    """Validate the Grok adapter inventory, deferred critical, and spawn contract."""
    failures: list[str] = []
    roles_path = root / "hosts/grok/config/roles.grok.toml"
    spawn_path = root / "hosts/grok/references/spawn.md"
    if not roles_path.is_file() or not spawn_path.is_file():
        return failures
    try:
        roles = tomllib.loads(roles_path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeError) as error:
        return [f"grok-contract: roles.grok.toml is invalid: {error}"]
    tiers = roles.get("tiers")
    if not isinstance(tiers, dict) or set(tiers) != {"standard", "critical"}:
        failures.append(
            "grok-contract: roles.grok.toml must assign standard and critical only"
        )
        return failures
    if "minimal" in tiers:
        failures.append("grok-contract: minimal must remain unassigned")

    def expected_assignment(tier: str, capability: str) -> tuple[str, str, str]:
        model = "grok-4.6"
        return model, "inherit", "general-purpose"

    for tier_name in ("standard", "critical"):
        assignments = tiers.get(tier_name)
        if not isinstance(assignments, dict) or set(assignments) != set(GROK_CAPABILITIES):
            failures.append(
                f"grok-contract: {tier_name} must define all ten capabilities and no extras"
            )
            continue
        for capability, assignment in assignments.items():
            if not isinstance(assignment, dict) or set(assignment) != ASSIGNMENT_FIELDS:
                failures.append(
                    f"grok-contract: {tier_name}.{capability} needs profile, "
                    "subagent_type, model, and effort"
                )
                continue
            model, effort, worker = expected_assignment(tier_name, capability)
            if assignment["model"] != model or assignment["effort"] != effort:
                failures.append(
                    f"grok-contract: {tier_name}.{capability} must be {model} {effort}"
                )
            if assignment["subagent_type"] != worker:
                failures.append(
                    f"grok-contract: {tier_name}.{capability} must dispatch {worker}"
                )
            if assignment["profile"] not in PROFILE_NAMES:
                failures.append(
                    f"grok-contract: {tier_name}.{capability} has an invalid profile"
                )
    spawn = " ".join(spawn_path.read_text(encoding="utf-8").split())
    for required in (
        "spawn_subagent",
        "isolation: none",
        "resume_from",
        "get_command_or_subagent_output",
        "timeout_ms: 600000",
        "GROK_SESSION_ID",
        "Playwright",
        "general-purpose",
    ):
        if required not in spawn:
            failures.append(f"grok-contract: spawn.md must name {required}")
    return failures


def check_repository_conventions(root: Path) -> list[str]:
    """Keep this repository's `.agent/` hard-gate command declaration exact."""
    failures: list[str] = []
    relative = ".agent/backend-testing.md"
    path = root / relative
    if not path.is_file():
        return [f"repository-conventions: missing {relative}"]
    normalized = " ".join(path.read_text(encoding="utf-8").lower().split())
    for contract in (
        "python3 codex/scripts/validate_suite.py --full",
        "python3 codex/scripts/validate_suite.py --quick",
    ):
        if contract not in normalized:
            failures.append(
                f"repository-conventions: {relative} must name {contract}"
            )
    return failures


Check = Callable[[Path], list[str]]
QUICK_CHECKS: tuple[Check, ...] = (
    check_required_paths,
    check_distribution_boundary,
    check_delivery_config,
    check_documentation,
    check_hook,
    check_roles_and_profiles,
    check_skills_and_runtime,
    check_orchestra_lite,
    check_repository_conventions,
    check_direct_sync,
    check_cursor_host,
    check_grok_host,
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
