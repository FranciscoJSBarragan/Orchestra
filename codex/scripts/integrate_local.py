#!/usr/bin/env python3
"""Safely fast-forward a reviewed task worktree into its authorized local base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from policy import blocked, load_policy, run_checks


SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}\Z")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def _command_reason(name: str, result: subprocess.CompletedProcess[str]) -> str:
    detail = result.stderr.strip() or result.stdout.strip() or "no output"
    return f"{name} failed: {detail}"


def _worktree_root(path: Path) -> Path | None:
    resolved = path.resolve()
    result = _git(resolved, "rev-parse", "--show-toplevel")
    if result.returncode or Path(result.stdout.strip()).resolve() != resolved:
        return None
    return resolved


def _common_git_dir(repo: Path) -> Path | None:
    result = _git(repo, "rev-parse", "--git-common-dir")
    if result.returncode:
        return None
    path = Path(result.stdout.strip())
    return (repo / path).resolve() if not path.is_absolute() else path.resolve()


def _head(repo: Path) -> str | None:
    result = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    sha = result.stdout.strip()
    return sha if not result.returncode and SHA_PATTERN.fullmatch(sha) else None


def _branch(repo: Path) -> str | None:
    result = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    branch = result.stdout.strip()
    return branch if not result.returncode and branch else None


def _clean(repo: Path) -> bool:
    result = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return not result.returncode and not result.stdout


def integrate_local(
    task_worktree: Path,
    base_worktree: Path,
    task_branch: str,
    base_branch: str,
    authorized: bool,
    policy_path: Path | None,
) -> dict[str, Any]:
    """Verify, fast-forward, confirm containment, and clean only safe resources."""
    if not authorized:
        return blocked("explicit task-level local integration authorization is required")
    task = _worktree_root(task_worktree)
    base = _worktree_root(base_worktree)
    if task is None or base is None or task == base:
        return blocked("task and base must be distinct Git worktree roots")
    if _common_git_dir(task) != _common_git_dir(base):
        return blocked("task and base worktrees do not share a Git repository")
    if _branch(task) != task_branch or _branch(base) != base_branch:
        return blocked("task or base worktree is on an unexpected branch")
    if not _clean(task):
        return blocked("task worktree is dirty")
    if not _clean(base):
        return blocked("base worktree is dirty")

    policy, policy_result = load_policy(
        policy_path.resolve() if policy_path else task / "orchestra.toml"
    )
    if policy is None:
        return policy_result
    if policy["mode"] not in {"hybrid", "local-direct"}:
        return blocked("delivery policy does not permit local integration")

    task_sha = _head(task)
    base_sha = _head(base)
    if task_sha is None or base_sha is None:
        return blocked("task or base HEAD is invalid")
    branch_ref = _git(task, "rev-parse", "--verify", f"refs/heads/{task_branch}")
    if branch_ref.returncode or branch_ref.stdout.strip() != task_sha:
        return blocked("task branch does not identify the task HEAD")

    check_result = run_checks(task, policy["checks"])
    if check_result["status"] != "ok":
        return check_result
    if not _clean(task) or _head(task) != task_sha:
        return blocked("configured checks changed the task worktree or HEAD")
    if not _clean(base) or _head(base) != base_sha:
        return blocked("base worktree changed before integration")

    ancestor = _git(base, "merge-base", "--is-ancestor", base_sha, task_sha)
    if ancestor.returncode:
        return blocked("task cannot be integrated by fast-forward; root resolution required")
    merge = _git(base, "merge", "--ff-only", task_sha)
    if merge.returncode:
        return blocked(_command_reason("git merge --ff-only", merge))
    contained = _git(base, "merge-base", "--is-ancestor", task_sha, "HEAD")
    if contained.returncode or _head(base) != task_sha:
        return {
            "status": "partial",
            "reason": "integration completed but exact task SHA verification failed",
            "task_sha": task_sha,
        }
    if not _clean(base) or not _clean(task):
        return {
            "status": "partial",
            "reason": "integration completed but a worktree is dirty; cleanup skipped",
            "task_sha": task_sha,
        }
    branch_ref = _git(task, "rev-parse", "--verify", f"refs/heads/{task_branch}")
    if branch_ref.returncode or branch_ref.stdout.strip() != task_sha:
        return {
            "status": "partial",
            "reason": "integration completed but task branch moved; cleanup skipped",
            "task_sha": task_sha,
        }

    remove = _git(base, "worktree", "remove", str(task))
    if remove.returncode:
        return {
            "status": "partial",
            "reason": _command_reason("git worktree remove", remove),
            "task_sha": task_sha,
        }
    merged = _git(base, "branch", "--merged", base_branch, "--format=%(refname:short)")
    merged_branches = set(merged.stdout.splitlines()) if not merged.returncode else set()
    if task_branch not in merged_branches:
        return {
            "status": "partial",
            "reason": "task branch is not fully merged; branch deletion skipped",
            "task_sha": task_sha,
        }
    delete = _git(base, "branch", "-d", task_branch)
    if delete.returncode:
        return {
            "status": "partial",
            "reason": _command_reason("git branch -d", delete),
            "task_sha": task_sha,
        }
    return {
        "status": "ok",
        "action": "integrated",
        "task_sha": task_sha,
        "base_branch": base_branch,
        "checks": check_result["checks"],
        "cleanup": ["worktree", "branch"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-worktree", type=Path, required=True)
    parser.add_argument("--base-worktree", type=Path, required=True)
    parser.add_argument("--task-branch", required=True)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--authorized", action="store_true")
    parser.add_argument("--policy", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = integrate_local(
        args.task_worktree,
        args.base_worktree,
        args.task_branch,
        args.base_branch,
        args.authorized,
        args.policy,
    )
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
