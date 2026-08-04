"""Allowlisted Hub API payloads and attention model (SPEC §7-8)."""
from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Mapping

from orchestra_hub.artifacts import ARTIFACT_FIELDS, artifact_entries
from orchestra_hub.config import HubConfig, PinnedRepository
from orchestra_hub.fingerprint import (
    MATERIAL_FINGERPRINT_VERSION,
    material_fingerprint,
)

TASK_FIELDS = (
    "id", "label", "repository", "worktree", "branch", "base_revision",
    "head_revision", "tier", "stage", "status", "summary", "blocker",
    "next_action", "created_at", "updated_at",
)
ACTIVITY_FIELDS = ("agent_id", "capability", "state", "summary", "updated_at")

__all__ = [
    "ACTIVITY_FIELDS",
    "ARTIFACT_FIELDS",
    "TASK_FIELDS",
    "attention_entries",
    "repository_entries",
    "summary_payload",
    "task_detail_payload",
    "task_summary",
    "tasks_payload",
]


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def task_summary(
    row: Mapping[str, object],
    *,
    now: datetime,
    stale_after: timedelta,
) -> dict:
    task = {field: row[field] for field in TASK_FIELDS}
    task["material_fingerprint"] = material_fingerprint(task)
    updated_at = parse_timestamp(str(task["updated_at"]))
    task["stale"] = (
        task["status"] != "completed"
        and now - updated_at > stale_after
    )
    return task


def attention_entries(tasks: list[dict]) -> list[dict]:
    entries: list[dict] = []
    for task in tasks:
        if task["status"] == "completed":
            continue
        reasons: list[str] = []
        if task["blocker"]:
            reasons.append("blocker")
        if task["stale"]:
            reasons.append("stale")
        if not reasons:
            continue
        entries.append(
            {
                "task_id": task["id"],
                "label": task["label"],
                "repository": task["repository"],
                "reasons": reasons,
                "blocker": task["blocker"],
                "next_action": task["next_action"],
                "updated_at": task["updated_at"],
            }
        )
    return entries


def repository_entries(
    tasks: list[dict],
    pinned: tuple[PinnedRepository, ...],
) -> list[dict]:
    repos: dict[str, dict] = {}
    for entry in pinned:
        repos[entry.path] = {
            "path": entry.path,
            "name": entry.name,
            "pinned": True,
            "observed": False,
            "active_tasks": 0,
            "completed_tasks": 0,
        }
    for task in tasks:
        path = str(task["repository"])
        current = repos.get(path)
        if current is None:
            current = {
                "path": path,
                "name": Path(path).name,
                "pinned": False,
                "observed": False,
                "active_tasks": 0,
                "completed_tasks": 0,
            }
            repos[path] = current
        current["observed"] = True
        if task["status"] == "completed":
            current["completed_tasks"] += 1
        else:
            current["active_tasks"] += 1
    return sorted(repos.values(), key=lambda item: (item["name"], item["path"]))


def _stale_after(config: HubConfig) -> timedelta:
    return timedelta(minutes=config.stale_after_minutes)


def _tasks(
    connection: sqlite3.Connection,
    *,
    now: datetime,
    stale_after: timedelta,
    status: str | None = None,
) -> list[dict]:
    if status is None:
        rows = connection.execute(
            "SELECT * FROM tasks ORDER BY updated_at DESC, id"
        ).fetchall()
    else:
        rows = connection.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY updated_at DESC, id",
            (status,),
        ).fetchall()
    return [
        task_summary(row, now=now, stale_after=stale_after) for row in rows
    ]


def summary_payload(
    connection: sqlite3.Connection,
    config: HubConfig,
    now: datetime,
) -> dict:
    stale_after = _stale_after(config)
    tasks = _tasks(connection, now=now, stale_after=stale_after)
    return {
        "status": "ok",
        "material_fingerprint_version": MATERIAL_FINGERPRINT_VERSION,
        "repositories": repository_entries(
            tasks, config.pinned_repositories
        ),
        "tasks": tasks,
        "attention": attention_entries(tasks),
    }


def tasks_payload(
    connection: sqlite3.Connection,
    config: HubConfig,
    now: datetime,
    *,
    status: str | None = None,
) -> dict:
    stale_after = _stale_after(config)
    tasks = _tasks(
        connection, now=now, stale_after=stale_after, status=status
    )
    return {
        "status": "ok",
        "material_fingerprint_version": MATERIAL_FINGERPRINT_VERSION,
        "tasks": tasks,
    }


def task_detail_payload(
    connection: sqlite3.Connection,
    config: HubConfig,
    now: datetime,
    task_id: str,
) -> dict | None:
    stale_after = _stale_after(config)
    row = connection.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()
    if row is None:
        return None
    task = task_summary(row, now=now, stale_after=stale_after)
    activities = [
        {field: activity[field] for field in ACTIVITY_FIELDS}
        for activity in connection.execute(
            """
            SELECT * FROM activities
            WHERE task_id = ?
            ORDER BY updated_at DESC, agent_id, capability
            """,
            (task_id,),
        ).fetchall()
    ]
    return {
        "status": "ok",
        "material_fingerprint_version": MATERIAL_FINGERPRINT_VERSION,
        "task": task,
        "activities": activities,
        "artifacts": artifact_entries(str(task["worktree"])),
    }
