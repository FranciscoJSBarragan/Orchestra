"""Read-only artifact discovery from the task-private Git directory.

Orchestra artifacts have no database locator: they are UTF-8 Markdown files
named `<NN>-<kind>[-p<phase>].md` under the directory resolved by
`git rev-parse --git-path orchestra/artifacts` inside the task worktree. The
Hub resolves that directory without running Git and reads names and mtimes
only; artifact content is never read or served.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

ARTIFACT_FIELDS = ("id", "kind", "phase", "created_at")
ARTIFACT_NAME = re.compile(
    r"^\d+-(?P<kind>[a-z0-9-]+?)(?:-p(?P<phase>\d+))?\.md$"
)
GITDIR_PREFIX = "gitdir:"


def artifacts_directory(worktree: Path) -> Path | None:
    """Resolve `<git-dir>/orchestra/artifacts` for a worktree, or None."""
    marker = worktree / ".git"
    if marker.is_symlink():
        return None
    if marker.is_dir():
        return marker / "orchestra" / "artifacts"
    if not marker.is_file():
        return None
    try:
        text = marker.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        if not line.startswith(GITDIR_PREFIX):
            continue
        gitdir = Path(line[len(GITDIR_PREFIX):].strip())
        if not str(gitdir):
            return None
        if not gitdir.is_absolute():
            gitdir = worktree / gitdir
        return gitdir / "orchestra" / "artifacts"
    return None


def _created_at(path: Path) -> str:
    moment = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def artifact_entries(worktree: str) -> list[dict]:
    """List published artifacts for a task, newest ordinal first."""
    if not worktree:
        return []
    directory = artifacts_directory(Path(worktree))
    if directory is None or directory.is_symlink() or not directory.is_dir():
        return []
    entries: list[dict] = []
    try:
        candidates = sorted(directory.iterdir(), reverse=True)
    except OSError:
        return []
    for path in candidates:
        match = ARTIFACT_NAME.match(path.name)
        if match is None:
            continue
        try:
            if path.is_symlink() or not path.is_file():
                continue
            created_at = _created_at(path)
        except OSError:
            continue
        phase = match.group("phase")
        entries.append(
            {
                "id": path.name,
                "kind": match.group("kind"),
                "phase": int(phase) if phase else 0,
                "created_at": created_at,
            }
        )
    return entries
