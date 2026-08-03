#!/usr/bin/env python3
"""Commit one reviewed phase while preserving work outside its exact path scope."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess

from _common import SHA_PATTERN, blocked as _blocked
from _common import _git as _common_git


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _common_git(repo, *args, literal_pathspecs=True)


def _staged_paths(repo: Path) -> tuple[set[str] | None, str | None]:
    staged = _git(repo, "diff", "--cached", "--no-renames", "--name-only", "-z")
    if staged.returncode:
        return None, "cannot inspect staged paths"
    return {path for path in staged.stdout.split("\0") if path}, None


def _head_sha(repo: Path) -> str | None:
    result = _git(repo, "rev-parse", "--verify", "HEAD")
    sha = result.stdout.strip()
    if result.returncode or not SHA_PATTERN.fullmatch(sha):
        return None
    return sha


def _validate_paths(repo: Path, raw_paths: list[str]) -> tuple[list[str], str | None]:
    if not raw_paths:
        return [], "at least one --path is required"

    paths: list[str] = []
    seen: set[str] = set()
    for raw in raw_paths:
        candidate = PurePosixPath(raw)
        if (
            not raw
            or "\\" in raw
            or candidate.is_absolute()
            or raw != candidate.as_posix()
            or raw in (".", "..")
            or ".." in candidate.parts
        ):
            return [], f"invalid repository-relative exact path: {raw!r}"
        if raw in seen:
            return [], f"duplicate authorized path: {raw}"

        worktree_path = repo.joinpath(*candidate.parts)
        if worktree_path.is_dir():
            return [], f"authorized path must name a file, not a directory: {raw}"
        if not worktree_path.exists() and not worktree_path.is_symlink():
            tracked = _git(repo, "ls-tree", "-r", "--name-only", "-z", "HEAD", "--", raw)
            tracked_paths = {path for path in tracked.stdout.split("\0") if path}
            if tracked.returncode or raw not in tracked_paths:
                return [], f"authorized path does not exist and is not tracked in HEAD: {raw}"
        seen.add(raw)
        paths.append(raw)
    return paths, None


def commit_phase(repo: Path, paths: list[str], message_file: Path) -> dict[str, str]:
    repo = repo.resolve()
    top_level = _git(repo, "rev-parse", "--show-toplevel")
    if top_level.returncode:
        return _blocked("repository is not a Git worktree")
    if Path(top_level.stdout.strip()).resolve() != repo:
        return _blocked("--repo must be the Git worktree root")

    paths, path_error = _validate_paths(repo, paths)
    if path_error:
        return _blocked(path_error)

    try:
        message = message_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return _blocked(f"cannot read message file: {error}")
    if not message.strip():
        return _blocked("commit message file is empty")

    staged_paths, staged_error = _staged_paths(repo)
    if staged_error:
        return _blocked(staged_error)
    assert staged_paths is not None
    unrelated = sorted(staged_paths.difference(paths))
    if unrelated:
        return _blocked("unrelated staged paths: " + ", ".join(unrelated))

    add_paths: list[str] = []
    for path in paths:
        worktree_path = repo.joinpath(*PurePosixPath(path).parts)
        indexed = _git(repo, "ls-files", "--error-unmatch", "--", path)
        if worktree_path.exists() or worktree_path.is_symlink() or not indexed.returncode:
            add_paths.append(path)
    if add_paths:
        add = _git(repo, "add", "-A", "--", *add_paths)
        if add.returncode:
            detail = add.stderr.strip() or add.stdout.strip() or "git add failed"
            return _blocked(detail)

    staged_paths, staged_error = _staged_paths(repo)
    if staged_error:
        return _blocked(staged_error)
    assert staged_paths is not None
    unrelated = sorted(staged_paths.difference(paths))
    if unrelated:
        return _blocked("unrelated paths became staged: " + ", ".join(unrelated))
    if not staged_paths:
        return {"status": "nothing_to_commit"}

    before_sha = _head_sha(repo)
    commit = _git(
        repo,
        "commit",
        "--cleanup=verbatim",
        "-F",
        str(message_file.resolve()),
        "--",
        *paths,
    )
    after_sha = _head_sha(repo)
    commit_created = after_sha is not None and after_sha != before_sha
    if not commit_created:
        if not commit.returncode:
            return _blocked(
                "git commit reported success but no commit was created; "
                "authorized changes remain staged"
            )
        detail = commit.stderr.strip() or commit.stdout.strip() or "git commit failed"
        return _blocked(f"git commit failed; no commit was created: {detail}")
    assert after_sha is not None

    changed = _git(
        repo,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--no-renames",
        "--name-only",
        "-z",
        "-r",
        after_sha,
    )
    if changed.returncode:
        return _blocked(
            "commit exists but its changed paths could not be verified", sha=after_sha
        )
    committed_paths = {path for path in changed.stdout.split("\0") if path}
    if not committed_paths:
        return _blocked("commit exists but its changed path set is empty", sha=after_sha)
    unexpected = sorted(committed_paths.difference(paths))
    if unexpected:
        return _blocked(
            "commit exists but contains unauthorized paths: " + ", ".join(unexpected),
            sha=after_sha,
        )
    result = {"status": "committed", "sha": after_sha}
    if commit.returncode:
        detail = commit.stderr.strip() or commit.stdout.strip()
        if detail:
            result["warning"] = " ".join(detail.split())[:500]
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--message-file", type=Path, required=True)
    parser.add_argument("--path", action="append", dest="paths", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = commit_phase(args.repo, args.paths, args.message_file)
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
