#!/usr/bin/env python3
"""Validate the executable conformance contract for the Orchestra source tree."""

from __future__ import annotations

import argparse
import ast
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Callable


REQUIRED_PATHS = (
    "README.md",
    "VISION.md",
    "AGENTS.md",
    "docs/WORKFLOW.md",
    "docs/ARCHITECTURE.md",
    "docs/ROADMAP.md",
    ".githooks/pre-commit",
    "codex/scripts/validate_suite.py",
    "codex/tests/test_validate_suite.py",
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


def check_required_paths(root: Path) -> list[str]:
    """Ensure every Phase 1 conformance consumer is present."""
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
    check_documentation,
    check_hook,
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
