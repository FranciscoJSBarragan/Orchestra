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

from orchestra_hub import artifacts  # noqa: E402

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


def make_worktree(root: Path, *, linked: bool = False) -> Path:
    """Create a primary- or linked-worktree-shaped directory."""
    worktree = root / "worktree"
    worktree.mkdir(parents=True, exist_ok=True)
    if linked:
        gitdir = root / "repo" / ".git" / "worktrees" / "worktree"
        gitdir.mkdir(parents=True, exist_ok=True)
        (worktree / ".git").write_text(f"gitdir: {gitdir}\n", encoding="utf-8")
    else:
        (worktree / ".git").mkdir(exist_ok=True)
    return worktree


def write_artifact(worktree: Path, name: str, body: str = "report\n") -> Path:
    """Publish an artifact file the way an Orchestra agent does."""
    state = worktree / ".orchestra"
    if not state.exists():
        state.mkdir()
        (state / ".gitignore").write_text(
            artifacts.STATE_MARKER_CONTENT,
            encoding="utf-8",
        )
    directory = artifacts.artifacts_directory(worktree)
    assert directory is not None
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path
