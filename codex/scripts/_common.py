#!/usr/bin/env python3
"""Shared helpers for Orchestra git-helper scripts.

Only pieces whose duplicated variants are semantically identical across
consumers live here. Materially different variants stay local to their script.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any


SHA_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
PRIVATE_STATE_DIRECTORY = ".orchestra"
PRIVATE_STATE_MARKER = ".gitignore"
PRIVATE_STATE_MARKER_CONTENT = (
    "# Orchestra task-private state; removed after successful delivery.\n"
    "*\n"
)
PRIVATE_STATE_PLAN = "plan.md"
PRIVATE_STATE_ARTIFACTS = "artifacts"


@dataclass(frozen=True)
class GitRepositoryIdentity:
    """One checkout plus the primary worktree identity shared by its clone."""

    checkout_root: Path
    repository_root: Path
    common_dir: Path
    head: str


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
    return resolve_commit(repo, "HEAD")


def git_repository_identity(path: Path) -> GitRepositoryIdentity | None:
    """Resolve checkout state without confusing a linked worktree for its repository."""
    checkout = worktree_root(path)
    if checkout is None:
        return None
    common_dir = common_git_dir(checkout)
    head = head_commit(checkout)
    if common_dir is None or head is None:
        return None

    repository = _primary_worktree(checkout, common_dir)
    return GitRepositoryIdentity(
        checkout_root=checkout,
        repository_root=repository,
        common_dir=common_dir,
        head=head,
    )


def _primary_worktree(checkout: Path, common_dir: Path) -> Path:
    """Return Git's primary worktree, falling back to the current checkout."""
    if common_dir.name == ".git":
        candidate = common_dir.parent.resolve()
        if worktree_root(candidate) == candidate and common_git_dir(candidate) == common_dir:
            return candidate

    listed = _git(checkout, "worktree", "list", "--porcelain", "-z")
    if listed.returncode:
        return checkout
    record = listed.stdout.split("\0\0", 1)[0]
    fields = record.split("\0")
    if "bare" in fields:
        return checkout
    entry = next((field[9:] for field in fields if field.startswith("worktree ")), "")
    if entry:
        candidate = Path(entry).resolve()
        if worktree_root(candidate) == candidate and common_git_dir(candidate) == common_dir:
            return candidate
    return checkout


def resolve_commit(repo: Path, revision: str) -> str | None:
    result = _git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}")
    sha = result.stdout.strip()
    return sha if not result.returncode and SHA_PATTERN.fullmatch(sha) else None


def require_expected_revision(
    repo: Path, revision: str, expected_revision: str
) -> tuple[str | None, dict[str, Any] | None]:
    """Resolve one revision and require the exact full SHA supplied by the plan."""
    if not SHA_PATTERN.fullmatch(expected_revision):
        return None, blocked("expected task revision must be a full commit SHA")
    actual_revision = resolve_commit(repo, revision)
    if actual_revision is None:
        return None, blocked("task revision does not resolve to a commit")
    if actual_revision != expected_revision:
        return None, blocked(
            "task revision does not match the completed plan revision",
            expected_task_revision=expected_revision,
            task_revision=actual_revision,
        )
    return actual_revision, None


def head_branch(repo: Path) -> str | None:
    result = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
    branch = result.stdout.strip()
    return branch if not result.returncode and branch else None


def is_clean(repo: Path) -> bool:
    result = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return not result.returncode and not result.stdout


def _legacy_private_task_state(repo: Path) -> Path | None:
    result = _git(repo, "rev-parse", "--absolute-git-dir")
    if result.returncode:
        return None
    return Path(result.stdout.strip()) / "orchestra"


def _state_paths(private: Path, layout: str, *, exists: bool) -> dict[str, Any]:
    return {
        "layout": layout,
        "state": str(private),
        "plan": str(private / PRIVATE_STATE_PLAN),
        "artifacts": str(private / PRIVATE_STATE_ARTIFACTS),
        "exists": exists,
    }


def _workspace_state_error(private: Path) -> str | None:
    marker = private / PRIVATE_STATE_MARKER
    plan = private / PRIVATE_STATE_PLAN
    artifacts = private / PRIVATE_STATE_ARTIFACTS
    if private.is_symlink() or not private.is_dir():
        return "private task state is not a safe directory"
    if marker.is_symlink() or not marker.is_file():
        return "private task state ownership marker is missing or unsafe"
    try:
        if marker.read_text(encoding="utf-8") != PRIVATE_STATE_MARKER_CONTENT:
            return "private task state ownership marker is not recognized"
        unknown = {
            entry.name
            for entry in private.iterdir()
            if entry.name
            not in {PRIVATE_STATE_MARKER, PRIVATE_STATE_PLAN, PRIVATE_STATE_ARTIFACTS}
        }
    except OSError as error:
        return f"cannot inspect private task state: {error}"
    if unknown:
        return "private task state contains unknown entries"
    if plan.is_symlink() or (plan.exists() and not plan.is_file()):
        return "private task plan is not a regular file"
    if artifacts.is_symlink() or (artifacts.exists() and not artifacts.is_dir()):
        return "private task artifacts path is not a directory"
    return None


def resolve_private_task_state(repo: Path) -> tuple[dict[str, Any] | None, str | None]:
    """Resolve workspace-local state, with read compatibility for legacy tasks."""
    root = worktree_root(repo)
    if root is None:
        return None, "cannot resolve Git worktree root"
    private = root / PRIVATE_STATE_DIRECTORY
    legacy = _legacy_private_task_state(root)
    if legacy is None:
        return None, "cannot resolve legacy task Git directory"

    workspace_exists = private.exists() or private.is_symlink()
    legacy_plan = legacy / PRIVATE_STATE_PLAN
    legacy_artifacts = legacy / PRIVATE_STATE_ARTIFACTS
    legacy_exists = any(
        path.exists() or path.is_symlink() for path in (legacy_plan, legacy_artifacts)
    )
    if workspace_exists and legacy_exists:
        return None, "workspace and legacy private task state both exist"
    if workspace_exists:
        error = _workspace_state_error(private)
        if error:
            return None, error
        return _state_paths(private, "workspace", exists=True), None
    if legacy_exists:
        if legacy.is_symlink() or not legacy.is_dir():
            return None, "legacy private task state is not a safe directory"
        if legacy_plan.is_symlink() or (
            legacy_plan.exists() and not legacy_plan.is_file()
        ):
            return None, "legacy private task plan is not a regular file"
        if legacy_artifacts.is_symlink() or (
            legacy_artifacts.exists() and not legacy_artifacts.is_dir()
        ):
            return None, "legacy private task artifacts path is not a directory"
        return _state_paths(legacy, "legacy", exists=True), None
    return _state_paths(private, "workspace", exists=False), None


def initialize_private_task_state(repo: Path) -> dict[str, Any]:
    """Create one ignored, worktree-local state directory for a new task."""
    resolved, error = resolve_private_task_state(repo)
    if error:
        return blocked(error)
    assert resolved is not None
    if resolved["layout"] == "legacy":
        return {"status": "ok", **resolved, "initialized": False}

    root = worktree_root(repo)
    assert root is not None
    private = Path(resolved["state"])
    tracked = _git(root, "ls-files", "--", PRIVATE_STATE_DIRECTORY)
    if tracked.returncode:
        return blocked("cannot inspect private task state tracking")
    if tracked.stdout.strip():
        return blocked("private task state path is tracked by the repository")

    created = not resolved["exists"]
    try:
        if created:
            private.mkdir(mode=0o700)
            (private / PRIVATE_STATE_MARKER).write_text(
                PRIVATE_STATE_MARKER_CONTENT, encoding="utf-8"
            )
        artifacts = private / PRIVATE_STATE_ARTIFACTS
        artifacts.mkdir(mode=0o700, exist_ok=True)
    except OSError as write_error:
        if created:
            try:
                shutil.rmtree(private)
            except OSError:
                pass
        return blocked(f"cannot initialize private task state: {write_error}")

    state_error = _workspace_state_error(private)
    ignored = _git(
        root,
        "check-ignore",
        "-q",
        "--",
        f"{PRIVATE_STATE_DIRECTORY}/{PRIVATE_STATE_MARKER}",
    )
    status = _git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        PRIVATE_STATE_DIRECTORY,
    )
    if state_error or ignored.returncode or status.returncode or status.stdout:
        if created:
            try:
                shutil.rmtree(private)
            except OSError:
                pass
        reason = state_error or "private task state is not ignored by Git"
        return blocked(reason)
    return {
        "status": "ok",
        **_state_paths(private, "workspace", exists=True),
        "initialized": created,
    }


def cleanup_private_task_state(repo: Path) -> str | None:
    """Remove only Orchestra plan/artifact state private to one checkout."""
    resolved, error = resolve_private_task_state(repo)
    if error:
        return error
    assert resolved is not None
    if not resolved["exists"]:
        return None
    private = Path(resolved["state"])
    plan = Path(resolved["plan"])
    artifacts = Path(resolved["artifacts"])
    try:
        if resolved["layout"] == "workspace":
            state_error = _workspace_state_error(private)
            if state_error:
                return state_error
            shutil.rmtree(private)
        else:
            if private.is_symlink() or plan.is_symlink() or artifacts.is_symlink():
                return "legacy private task state uses an unsafe symlink"
            if plan.exists():
                if not plan.is_file():
                    return "legacy private task plan is not a regular file"
                plan.unlink()
            if artifacts.exists():
                if not artifacts.is_dir():
                    return "legacy private task artifacts path is not a directory"
                shutil.rmtree(artifacts)
            if private.exists() and not any(private.iterdir()):
                private.rmdir()
    except OSError as error:
        return f"private task state cleanup failed: {error}"
    return None
