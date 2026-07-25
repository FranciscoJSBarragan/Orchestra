#!/usr/bin/env python3
"""Import selected dirty paths from a source worktree into a clean task worktree.

One-shot selected-path copier. The source stays unchanged. The task must be
clean and at the expected source HEAD. Each imported path is verified for
content, type, and executable mode.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
from typing import Any

from _common import SHA_PATTERN


def _git(repo: Path, *args: str, literal_pathspecs: bool = True) -> subprocess.CompletedProcess[str]:
    command = ["git"]
    if literal_pathspecs:
        command.append("--literal-pathspecs")
    command.extend(args)
    return subprocess.run(command, cwd=repo, check=False, capture_output=True, text=True)


def _blocked(reason: str, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": "blocked", "reason": " ".join(reason.split())[:500]}
    payload.update(extra)
    return payload


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


def _clean(repo: Path) -> bool:
    result = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return not result.returncode and not result.stdout


def _join(root: Path, relative: str) -> Path:
    return root.joinpath(*PurePosixPath(relative).parts)


def _parent_is_inside(root: Path, relative: str) -> bool:
    try:
        _join(root, relative).parent.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _entry_kind(path: Path) -> str:
    if path.is_symlink():
        return "symlink"
    if path.is_file():
        return "file"
    if path.exists():
        return "special"
    return "missing"


def _executable_bits(path: Path) -> int:
    return stat.S_IMODE(path.lstat().st_mode) & 0o111


def _load_paths(paths_file: Path) -> tuple[list[str] | None, str | None]:
    try:
        raw = json.loads(paths_file.read_text(encoding="utf-8"))
    except OSError as error:
        return None, f"cannot read paths file: {error}"
    except json.JSONDecodeError as error:
        return None, f"paths file is not valid JSON: {error}"
    if isinstance(raw, dict):
        raw = raw.get("paths")
    if not isinstance(raw, list) or not raw:
        return None, "paths file must contain a non-empty JSON array of paths"
    if not all(isinstance(item, str) for item in raw):
        return None, "paths file entries must be strings"
    return list(raw), None


def _validate_paths(repo: Path, raw_paths: list[str]) -> tuple[list[str], str | None]:
    paths: list[str] = []
    seen: set[str] = set()
    for raw in raw_paths:
        if "\0" in raw:
            return [], f"invalid repository-relative path containing NUL: {raw!r}"
        candidate = PurePosixPath(raw)
        if (
            not raw
            or "\\" in raw
            or candidate.is_absolute()
            or raw != candidate.as_posix()
            or raw in (".", "..")
            or ".." in candidate.parts
        ):
            return [], f"invalid repository-relative path: {raw!r}"
        if raw in seen:
            return [], f"duplicate selected path: {raw}"
        if not _parent_is_inside(repo, raw):
            return [], f"selected path escapes the source worktree: {raw}"
        ignored = _git(repo, "check-ignore", "-q", "--", raw, literal_pathspecs=False)
        if ignored.returncode == 0:
            return [], f"selected path is ignored: {raw}"
        if ignored.returncode not in {0, 1}:
            return [], f"cannot evaluate ignore state for path: {raw}"
        staged = _git(repo, "ls-files", "-s", "--", raw)
        if staged.returncode:
            return [], f"cannot inspect index state for path: {raw}"
        if any(line.startswith("160000 ") for line in staged.stdout.splitlines()):
            return [], f"selected path is a submodule gitlink: {raw}"
        head = _git(repo, "ls-tree", "-z", "HEAD", "--", raw)
        if head.returncode == 0 and head.stdout.startswith("160000 "):
            return [], f"selected path is a submodule gitlink: {raw}"
        kind = _entry_kind(_join(repo, raw))
        if kind == "special":
            return [], f"unsupported special source entry: {raw}"
        if kind == "missing":
            tracked = _git(repo, "ls-files", "--error-unmatch", "--", raw)
            if tracked.returncode:
                return [], f"selected path does not exist and is not tracked: {raw}"
        seen.add(raw)
        paths.append(raw)
    return paths, None


def _reject_addition_collision(task: Path, source: Path, paths: list[str]) -> str | None:
    for relative in paths:
        head = _git(source, "ls-tree", "-z", "HEAD", "--", relative)
        if head.returncode:
            return f"cannot inspect HEAD for path: {relative}"
        if head.stdout:
            continue
        if not _parent_is_inside(task, relative):
            return f"selected path escapes the task worktree: {relative}"
        target = _join(task, relative)
        if target.exists() or target.is_symlink():
            return f"selected addition already exists on task: {relative}"
    return None


def _apply_one(source: Path, task: Path, relative: str) -> str | None:
    source_path = _join(source, relative)
    task_path = _join(task, relative)
    if not _parent_is_inside(task, relative):
        return f"selected path escapes the task worktree: {relative}"
    kind = _entry_kind(source_path)
    if kind == "missing":
        if task_path.is_symlink() or task_path.is_file():
            try:
                task_path.unlink()
            except OSError as error:
                return f"cannot remove deleted path {relative}: {error}"
        elif task_path.exists():
            return f"cannot remove non-file path {relative}"
        return None
    parent = task_path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        return f"cannot create parent directory for {relative}: {error}"
    if parent.is_symlink() or not parent.is_dir():
        return f"parent path is not a directory: {relative}"
    if task_path.is_symlink() or task_path.is_file():
        try:
            task_path.unlink()
        except OSError as error:
            return f"cannot replace task path {relative}: {error}"
    elif task_path.exists():
        return f"cannot replace non-file task path {relative}"
    if kind == "symlink":
        try:
            os.symlink(os.readlink(source_path), task_path)
        except OSError as error:
            return f"cannot recreate symlink {relative}: {error}"
        return None
    if kind == "file":
        try:
            shutil.copy2(source_path, task_path, follow_symlinks=False)
        except OSError as error:
            return f"cannot copy {relative}: {error}"
        return None
    return f"unsupported special source entry: {relative}"


def _verify_one(source: Path, task: Path, relative: str) -> str | None:
    source_path = _join(source, relative)
    task_path = _join(task, relative)
    source_kind = _entry_kind(source_path)
    task_kind = _entry_kind(task_path)
    if source_kind != task_kind:
        return f"task path type mismatch for {relative}: {task_kind} != {source_kind}"
    if source_kind == "missing":
        return None
    if source_kind == "symlink":
        if os.readlink(source_path) != os.readlink(task_path):
            return f"task symlink target mismatch for {relative}"
        return None
    if source_kind == "file":
        if source_path.read_bytes() != task_path.read_bytes():
            return f"task file content mismatch for {relative}"
        if _executable_bits(source_path) != _executable_bits(task_path):
            return f"task executable mode mismatch for {relative}"
        return None
    return f"unsupported special source entry: {relative}"


def adopt_worktree(
    source_worktree: Path,
    task_worktree: Path,
    expected_source_head: str,
    paths_file: Path,
) -> dict[str, Any]:
    if not SHA_PATTERN.fullmatch(expected_source_head):
        return _blocked("expected source HEAD must be a full Git object name")

    source = _worktree_root(source_worktree)
    task = _worktree_root(task_worktree)
    if source is None or task is None:
        return _blocked("source and task must be Git worktree roots")
    if source == task:
        return _blocked("source and task worktrees must be distinct")
    if _common_git_dir(source) != _common_git_dir(task):
        return _blocked("source and task worktrees do not share a Git repository")

    source_head = _head(source)
    task_head = _head(task)
    if source_head is None or task_head is None:
        return _blocked("source or task HEAD is invalid")
    if source_head != expected_source_head:
        return _blocked("source HEAD does not match expected source HEAD")
    if task_head != expected_source_head:
        return _blocked("task HEAD does not match expected source HEAD")
    if not _clean(task):
        return _blocked("task worktree is dirty")

    raw_paths, load_error = _load_paths(paths_file)
    if load_error:
        return _blocked(load_error)
    assert raw_paths is not None
    paths, path_error = _validate_paths(source, raw_paths)
    if path_error:
        return _blocked(path_error)

    collision = _reject_addition_collision(task, source, paths)
    if collision:
        return _blocked(collision)

    applied_paths: list[str] = []
    for relative in paths:
        apply_error = _apply_one(source, task, relative)
        if apply_error:
            return _blocked(apply_error, applied_paths=[*applied_paths, relative])
        applied_paths.append(relative)
        verify_error = _verify_one(source, task, relative)
        if verify_error:
            return _blocked(verify_error, applied_paths=applied_paths)

    return {
        "status": "ok",
        "imported_paths": paths,
        "source_worktree": str(source),
        "task_worktree": str(task),
        "head": expected_source_head,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import selected dirty paths from a source worktree into a clean "
            "task worktree without mutating the source."
        )
    )
    parser.add_argument("--source-worktree", type=Path, required=True)
    parser.add_argument("--task-worktree", type=Path, required=True)
    parser.add_argument("--expected-source-head", required=True)
    parser.add_argument("--paths-file", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = adopt_worktree(
            args.source_worktree,
            args.task_worktree,
            args.expected_source_head,
            args.paths_file,
        )
    except Exception as error:  # noqa: BLE001 - CLI must always emit structured JSON
        result = _blocked(f"unexpected adoption failure: {error}")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
