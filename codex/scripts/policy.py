#!/usr/bin/env python3
"""Load Orchestra delivery policy and run its ordered argv checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tomllib
from typing import Any

from _common import blocked


VALID_MODES = {"pr-required", "hybrid", "local-direct"}


def load_policy(path: Path) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Return validated policy data and a compact result."""
    if not path.is_file():
        return None, blocked(
            "delivery policy is missing",
            action="ask_user_once",
            recommendation="hybrid",
        )
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        return None, blocked(f"delivery policy is invalid: {error}")

    if set(raw) != {"delivery", "checks"}:
        return None, blocked("delivery policy must contain only delivery and checks")
    delivery = raw.get("delivery")
    if not isinstance(delivery, dict) or set(delivery) != {"mode"}:
        return None, blocked("delivery must contain only mode")
    mode = delivery.get("mode")
    if mode not in VALID_MODES:
        return None, blocked("delivery mode must be pr-required, hybrid, or local-direct")

    raw_checks = raw.get("checks")
    if not isinstance(raw_checks, list) or not raw_checks:
        return None, blocked("at least one ordered argv check is required")
    checks: list[dict[str, Any]] = []
    names: set[str] = set()
    for index, raw_check in enumerate(raw_checks, start=1):
        if not isinstance(raw_check, dict) or set(raw_check) != {"name", "command"}:
            return None, blocked(f"check {index} must contain only name and command")
        name = raw_check.get("name")
        command = raw_check.get("command")
        if not isinstance(name, str) or not name.strip() or name in names:
            return None, blocked(f"check {index} needs a unique nonempty name")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(argument, str) and argument for argument in command)
        ):
            return None, blocked(f"check {name} needs a nonempty argv command")
        names.add(name)
        checks.append({"name": name, "command": tuple(command)})
    return {"mode": mode, "checks": checks}, {"status": "ok", "mode": mode}


def run_checks(repo: Path, checks: list[dict[str, Any]]) -> dict[str, Any]:
    """Run checks in declaration order without a shell."""
    passed: list[str] = []
    for check in checks:
        try:
            result = subprocess.run(
                list(check["command"]),
                cwd=repo,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as error:
            return blocked(f"check {check['name']} could not start: {error}", checks=passed)
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip() or "no output"
            return blocked(
                f"check {check['name']} failed: {detail}",
                check=check["name"],
                checks=passed,
            )
        passed.append(check["name"])
    return {"status": "ok", "checks": passed}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--policy", type=Path)
    parser.add_argument("action", choices=("show", "run-checks"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = args.repo.resolve()
    policy_path = args.policy.resolve() if args.policy else repo / "orchestra.toml"
    policy, result = load_policy(policy_path)
    if policy is not None and args.action == "run-checks":
        result = run_checks(repo, policy["checks"])
    elif policy is not None:
        result = {
            "status": "ok",
            "mode": policy["mode"],
            "checks": [check["name"] for check in policy["checks"]],
        }
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
