"""Pure presentation helpers for the TUI (no textual import)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

TASK_ROW_FIELDS = (
    "label", "tier", "stage", "status", "branch", "worktree",
    "summary", "blocker", "next_action", "created_at", "updated_at",
    "stale",
)


@dataclass(frozen=True)
class RepoNode:
    name: str
    path: str
    active: int
    completed: int
    tasks: tuple[dict, ...]


def build_tree(summary: dict) -> list[RepoNode]:
    tasks_by_repo: dict[str, list[dict]] = {}
    for task in summary.get("tasks", ()):
        tasks_by_repo.setdefault(str(task.get("repository", "")), []).append(task)
    nodes: list[RepoNode] = []
    seen: set[str] = set()
    for repo in summary.get("repositories", ()):
        path = str(repo.get("path", ""))
        seen.add(path)
        nodes.append(_node(
            name=str(repo.get("name", "")) or path,
            path=path,
            tasks=tasks_by_repo.get(path, []),
        ))
    for path, tasks in tasks_by_repo.items():
        if path not in seen:
            nodes.append(_node(name=path, path=path, tasks=tasks))
    return nodes


def _node(*, name: str, path: str, tasks: list[dict]) -> RepoNode:
    active = [task for task in tasks if task.get("status") != "completed"]
    completed = [task for task in tasks if task.get("status") == "completed"]
    return RepoNode(
        name=name,
        path=path,
        active=len(active),
        completed=len(completed),
        tasks=tuple(active + completed),
    )


def task_rows(task: dict) -> list[tuple[str, str]]:
    rows = []
    for field in TASK_ROW_FIELDS:
        value = task.get(field, "")
        if isinstance(value, bool):
            value = "true" if value else "false"
        rows.append((field, str(value)))
    return rows


def attention_flags(task: dict) -> frozenset[str]:
    flags = set()
    completed = task.get("status") == "completed"
    if not completed and str(task.get("blocker", "")):
        flags.add("blocker")
    if task.get("stale") is True:
        flags.add("stale")
    return frozenset(flags)


def phase_progress(artifacts: list[dict] | tuple) -> tuple[int, int] | None:
    """Best-effort (current, total) phase derived from published documents.

    Total = number of plan-phase documents. Current = highest phase with an
    available non-plan document, else the first planned phase. Returns None
    when the plan has no per-phase documents (nothing to derive).
    """
    planned = {
        int(artifact.get("phase", 0))
        for artifact in artifacts
        if artifact.get("kind") == "plan-phase"
    }
    if not planned:
        return None
    worked = {
        int(artifact.get("phase", 0))
        for artifact in artifacts
        if artifact.get("kind") not in ("plan-phase", "plan-overview")
        and artifact.get("available")
    }
    current = max(worked & planned) if worked & planned else min(planned)
    return current, len(planned)


def snapshot_age(updated_at: str, now: datetime) -> str:
    try:
        moment = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except ValueError:
        return updated_at
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    seconds = (now - moment).total_seconds()
    if seconds < 60:
        return "just now"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} h ago"
    return f"{hours // 24} d ago"
