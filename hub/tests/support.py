"""Shared fixtures: real coordination-schema database for Hub tests."""
from __future__ import annotations

import sqlite3
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "codex" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "hub"))

import coordination  # noqa: E402

HEX40 = "a" * 40


def create_state_db(state_root: Path) -> Path:
    state_root.mkdir(parents=True, exist_ok=True)
    database = state_root / "state.sqlite3"
    connection = sqlite3.connect(database)
    try:
        for statement in coordination.SCHEMA_STATEMENTS:
            connection.execute(statement)
        connection.execute(f"PRAGMA user_version = {coordination.SCHEMA_VERSION}")
        connection.commit()
        connection.execute("PRAGMA journal_mode = WAL")
    finally:
        connection.close()
    return database


def task_row(**overrides) -> dict:
    row = {
        "id": str(uuid.uuid4()), "label": "Sample task",
        "repository": "/tmp/repo", "worktree": "/tmp/worktrees/repo/sample",
        "branch": "orchestra/sample", "base_revision": HEX40,
        "head_revision": HEX40, "tier": "standard",
        "stage": "implementation", "status": "active", "summary": "Working",
        "blocker": "", "next_action": "Continue",
        "created_at": "2026-08-02T18:00:00Z",
        "updated_at": "2026-08-02T18:00:00Z",
    }
    row.update(overrides)
    return row


def insert_task(database: Path, **overrides) -> dict:
    row = task_row(**overrides)
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            """
            INSERT INTO tasks (
                id, label, repository, worktree, branch, base_revision,
                head_revision, tier, stage, status, summary, blocker,
                next_action, created_at, updated_at
            ) VALUES (
                :id, :label, :repository, :worktree, :branch, :base_revision,
                :head_revision, :tier, :stage, :status, :summary, :blocker,
                :next_action, :created_at, :updated_at
            )
            """,
            row,
        )
        connection.commit()
    finally:
        connection.close()
    return row


def insert_activity(database: Path, task_id: str, **overrides) -> dict:
    row = {
        "task_id": task_id,
        "agent_id": "agent-1",
        "capability": "implementation",
        "state": "running",
        "summary": "Implementing",
        "updated_at": "2026-08-02T18:00:00Z",
    }
    row.update(overrides)
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            """
            INSERT INTO activities (
                task_id, agent_id, capability, state, summary, updated_at
            ) VALUES (
                :task_id, :agent_id, :capability, :state, :summary, :updated_at
            )
            """,
            row,
        )
        connection.commit()
    finally:
        connection.close()
    return row


def insert_artifact(
    database: Path, task_id: str, *, path: str, **overrides
) -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "task_id": task_id,
        "kind": "implementation-report",
        "phase": 1,
        "path": path,
        "revision": HEX40,
        "producer": "worker-1",
        "created_at": "2026-08-02T18:00:00Z",
    }
    row.update(overrides)
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            """
            INSERT INTO artifacts (
                id, task_id, kind, phase, path, revision, producer, created_at
            ) VALUES (
                :id, :task_id, :kind, :phase, :path, :revision, :producer,
                :created_at
            )
            """,
            row,
        )
        connection.commit()
    finally:
        connection.close()
    return row
