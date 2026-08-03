#!/usr/bin/env python3
"""Shared helpers for Orchestra git-helper scripts.

Only pieces whose duplicated variants are semantically identical across
consumers live here. Materially different variants stay local to their script.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
from typing import Any


SHA_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


def _run(repo: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def _git(
    repo: Path, *args: str, literal_pathspecs: bool = False
) -> subprocess.CompletedProcess[str]:
    command = ["git"]
    if literal_pathspecs:
        command.append("--literal-pathspecs")
    command.extend(args)
    return _run(repo, command)


def blocked(reason: str, **details: Any) -> dict[str, Any]:
    result: dict[str, Any] = {
        "status": "blocked",
        "reason": " ".join(reason.split())[:500],
    }
    result.update(details)
    return result


def worktree_root(path: Path) -> Path | None:
    resolved = path.resolve()
    result = _git(resolved, "rev-parse", "--show-toplevel")
    if result.returncode or Path(result.stdout.strip()).resolve() != resolved:
        return None
    return resolved


def common_git_dir(repo: Path) -> Path | None:
    result = _git(repo, "rev-parse", "--git-common-dir")
    if result.returncode:
        return None
    path = Path(result.stdout.strip())
    return (repo / path).resolve() if not path.is_absolute() else path.resolve()


def head_commit(repo: Path) -> str | None:
    result = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    sha = result.stdout.strip()
    return sha if not result.returncode and SHA_PATTERN.fullmatch(sha) else None


def head_branch(repo: Path) -> str | None:
    result = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    branch = result.stdout.strip()
    return branch if not result.returncode and branch else None


def is_clean(repo: Path) -> bool:
    result = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return not result.returncode and not result.stdout
