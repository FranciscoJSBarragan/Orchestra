#!/usr/bin/env python3
"""Safely fast-forward a reviewed task worktree into its authorized local base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
from typing import Any

from policy import load_policy, run_checks
from _common import (
    _git,
    blocked,
    cleanup_private_task_state,
    common_git_dir as _common_git_dir,
    head_branch as _branch,
    head_commit as _head,
    is_clean as _clean,
    require_expected_revision,
    worktree_root as _worktree_root,
)


def _command_reason(name: str, result: subprocess.CompletedProcess[str]) -> str:
    detail = result.stderr.strip() or result.stdout.strip() or "no output"
    return f"{name} failed: {detail}"


def integrate_local(
    task_worktree: Path,
    base_worktree: Path,
    task_branch: str,
    base_branch: str,
    authorized: bool,
    policy_path: Path | None,
    expected_task_revision: str,
    checkout_mode: str = "managed",
    start_revision: str | None = None,
) -> dict[str, Any]:
    """Verify, fast-forward, confirm containment, and clean only safe resources."""
    if not authorized:
        return blocked("explicit task-level local integration authorization is required")
    task = _worktree_root(task_worktree)
    base = _worktree_root(base_worktree)
    if checkout_mode not in {"managed", "hybrid"}:
        return blocked("checkout mode must be managed or hybrid")
    if task is None or base is None:
        return blocked("task and base must be Git worktree roots")
    if checkout_mode == "managed" and task == base:
        return blocked("managed task and base must be distinct Git worktree roots")
    if checkout_mode == "hybrid" and task != base:
        return blocked("hybrid task and base must be the same Git checkout")
    if _common_git_dir(task) != _common_git_dir(base):
        return blocked("task and base worktrees do not share a Git repository")
    if _branch(task) != task_branch:
        return blocked("task checkout is on an unexpected branch")
    if checkout_mode == "managed" and _branch(base) != base_branch:
        return blocked("base worktree is on an unexpected branch")
    if not _clean(task):
        return blocked("task worktree is dirty")
    if checkout_mode == "managed" and not _clean(base):
        return blocked("base worktree is dirty")

    task_sha, revision_error = require_expected_revision(
        task, "HEAD", expected_task_revision
    )
    if revision_error:
        return revision_error
    assert task_sha is not None

    policy, policy_result = load_policy(
        policy_path.resolve() if policy_path else task / "orchestra.toml"
    )
    if policy is None:
        return policy_result
    if policy["mode"] not in {"hybrid", "local-direct"}:
        return blocked("delivery policy does not permit local integration")

    base_sha = _head(base)
    if base_sha is None:
        return blocked("base HEAD is invalid")
    branch_ref = _git(task, "rev-parse", "--verify", f"refs/heads/{task_branch}")
    if branch_ref.returncode or branch_ref.stdout.strip() != task_sha:
        return blocked("task branch does not identify the task HEAD")
    if checkout_mode == "hybrid":
        if not start_revision:
            return blocked("hybrid integration requires the captured start revision")
        start_ref = _git(task, "rev-parse", "--verify", f"refs/heads/{base_branch}")
        if start_ref.returncode or start_ref.stdout.strip() != start_revision:
            return blocked("hybrid starting branch moved after task creation")
        base_sha = start_revision

    check_result = run_checks(task, policy["checks"])
    if check_result["status"] != "ok":
        return check_result
    if not _clean(task) or _head(task) != task_sha:
        return blocked("configured checks changed the task worktree or HEAD")
    if checkout_mode == "managed" and (not _clean(base) or _head(base) != base_sha):
        return blocked("base worktree changed before integration")
    if checkout_mode == "hybrid":
        current_start = _git(task, "rev-parse", "--verify", f"refs/heads/{base_branch}")
        if current_start.returncode or current_start.stdout.strip() != base_sha:
            return blocked("hybrid starting branch changed during configured checks")

    ancestor = _git(base, "merge-base", "--is-ancestor", base_sha, task_sha)
    if ancestor.returncode:
        return blocked("task cannot be integrated by fast-forward; root resolution required")
    if checkout_mode == "hybrid":
        switch = _git(task, "switch", base_branch)
        if switch.returncode:
            return blocked(_command_reason("git switch", switch))
        if not _clean(task) or _branch(task) != base_branch or _head(task) != base_sha:
            return {
                "status": "partial",
                "reason": "starting branch checkout changed during hybrid integration",
                "task_sha": task_sha,
            }
        base = task
    merge = _git(base, "merge", "--ff-only", task_sha)
    if merge.returncode:
        if checkout_mode == "hybrid":
            return {
                "status": "partial",
                "reason": _command_reason("git merge --ff-only", merge),
                "task_sha": task_sha,
                "preserved": ["worktree", "branch", "private_state"],
            }
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

    if checkout_mode == "hybrid":
        delete = _git(base, "branch", "-d", task_branch)
        if delete.returncode:
            return {
                "status": "partial",
                "reason": _command_reason("git branch -d", delete),
                "task_sha": task_sha,
            }
        cleanup_error = cleanup_private_task_state(base)
        if cleanup_error:
            return {
                "status": "partial",
                "reason": cleanup_error,
                "task_sha": task_sha,
                "cleanup": ["branch"],
                "preserved": ["worktree"],
            }
        return {
            "status": "ok",
            "action": "integrated",
            "task_sha": task_sha,
            "base_branch": base_branch,
            "checks": check_result["checks"],
            "cleanup": ["branch", "private_state"],
            "preserved": ["worktree"],
        }

    merged = _git(base, "branch", "--merged", base_branch, "--format=%(refname:short)")
    merged_branches = set(merged.stdout.splitlines()) if not merged.returncode else set()
    if task_branch not in merged_branches:
        return {
            "status": "partial",
            "reason": "task branch is not fully merged; cleanup skipped",
            "task_sha": task_sha,
            "cleanup": [],
            "preserved": ["worktree", "branch", "private_state"],
        }
    cleanup_error = cleanup_private_task_state(task)
    if cleanup_error:
        return {
            "status": "partial",
            "reason": cleanup_error,
            "task_sha": task_sha,
            "cleanup": [],
            "preserved": ["worktree", "branch", "private_state"],
        }
    remove = _git(base, "worktree", "remove", str(task))
    if remove.returncode:
        return {
            "status": "partial",
            "reason": _command_reason("git worktree remove", remove),
            "task_sha": task_sha,
            "cleanup": ["private_state"],
            "preserved": ["worktree", "branch"],
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
        "cleanup": ["private_state", "worktree", "branch"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-worktree", type=Path, required=True)
    parser.add_argument("--base-worktree", type=Path, required=True)
    parser.add_argument("--task-branch", required=True)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--expected-task-revision", required=True)
    parser.add_argument("--authorized", action="store_true")
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--checkout-mode", choices=("managed", "hybrid"), default="managed")
    parser.add_argument("--start-revision")
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
        args.expected_task_revision,
        args.checkout_mode,
        args.start_revision,
    )
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
