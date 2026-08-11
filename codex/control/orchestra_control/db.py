"""Secure SQLite storage for the local Orchestra task control plane."""

from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import stat


SCHEMA_VERSION = 2
SCHEMA = (
    """
    CREATE TABLE tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        brief TEXT NOT NULL,
        brief_revision INTEGER NOT NULL DEFAULT 1,
        source_harness TEXT NOT NULL,
        source_conversation TEXT NOT NULL,
        source_message TEXT NOT NULL,
        repository TEXT,
        rank INTEGER NOT NULL,
        disposition TEXT NOT NULL CHECK (disposition IN ('open', 'archived')),
        idempotency_key TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE task_notes (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL REFERENCES tasks(id),
        body TEXT NOT NULL,
        source_harness TEXT NOT NULL,
        source_reference TEXT NOT NULL,
        idempotency_key TEXT NOT NULL UNIQUE,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE runs (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL REFERENCES tasks(id),
        repository TEXT NOT NULL,
        base_revision TEXT NOT NULL,
        delivery TEXT NOT NULL CHECK (delivery = 'hold'),
        status TEXT NOT NULL,
        thread_uuid TEXT,
        active_turn_id TEXT,
        last_turn_id TEXT,
        last_result_kind TEXT,
        last_result_json TEXT,
        retained_resources_json TEXT NOT NULL DEFAULT '[]',
        cancel_requested_at TEXT,
        cancelled_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE interactions (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL REFERENCES runs(id),
        turn_record_id TEXT NOT NULL REFERENCES turns(id),
        thread_uuid TEXT NOT NULL,
        turn_uuid TEXT NOT NULL,
        item_id TEXT,
        method TEXT NOT NULL,
        params_json TEXT NOT NULL,
        fingerprint TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending', 'resolved', 'consumed')),
        response_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE turns (
        id TEXT PRIMARY KEY,
        run_id TEXT NOT NULL REFERENCES runs(id),
        idempotency_key TEXT NOT NULL UNIQUE,
        input_digest TEXT NOT NULL,
        input_text TEXT NOT NULL,
        response_to TEXT,
        status TEXT NOT NULL,
        turn_uuid TEXT,
        result_json TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX tasks_disposition_rank ON tasks(disposition, rank, created_at)",
    "CREATE INDEX notes_task_id ON task_notes(task_id, created_at)",
    "CREATE INDEX runs_task_id ON runs(task_id, created_at)",
    "CREATE INDEX turns_run_id ON turns(run_id, created_at)",
    "CREATE INDEX interactions_run_id ON interactions(run_id, created_at)",
)


class StorageError(Exception):
    """Storage is unsafe, unavailable, or incompatible."""


def state_root(explicit: Path | None = None) -> Path:
    if explicit is not None:
        root = Path(os.path.abspath(explicit))
    else:
        home = os.environ.get("HOME")
        if not home:
            raise StorageError("HOME is unavailable")
        root = Path(home) / ".orchestra"
    try:
        root.mkdir(parents=True, mode=0o700, exist_ok=True)
    except OSError as error:
        raise StorageError(f"cannot create state root: {error}") from error
    if root.is_symlink() or not root.is_dir():
        raise StorageError(f"state root is unsafe: {root}")
    return root


def _restrict(path: Path) -> None:
    for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
        try:
            mode = os.lstat(candidate).st_mode
        except FileNotFoundError:
            continue
        except OSError as error:
            raise StorageError(f"cannot inspect state file: {error}") from error
        if not stat.S_ISREG(mode):
            raise StorageError(f"state file is not regular: {candidate}")
        if stat.S_IMODE(mode) != 0o600:
            try:
                os.chmod(candidate, 0o600)
            except OSError as error:
                raise StorageError(f"cannot restrict state file: {error}") from error


def connect(explicit_root: Path | None = None) -> sqlite3.Connection:
    database = state_root(explicit_root) / "control.sqlite3"
    if database.is_symlink() or (database.exists() and not database.is_file()):
        raise StorageError(f"state database is unsafe: {database}")
    if not database.exists():
        flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(database, flags, 0o600)
        except FileExistsError:
            pass
        except OSError as error:
            raise StorageError(f"cannot create state database: {error}") from error
        else:
            os.close(descriptor)
    _restrict(database)
    connection: sqlite3.Connection | None = None
    try:
        connection = sqlite3.connect(database, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("BEGIN IMMEDIATE")
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        objects = connection.execute(
            "SELECT name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
        ).fetchall()
        if version == 0 and not objects:
            for statement in SCHEMA:
                connection.execute(statement)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        elif version != SCHEMA_VERSION:
            connection.rollback()
            raise StorageError(f"unsupported control schema version: {version}")
        connection.commit()
        connection.execute("PRAGMA journal_mode = WAL")
        _restrict(database)
        return connection
    except StorageError:
        if connection is not None:
            connection.close()
        raise
    except (OSError, sqlite3.Error) as error:
        if connection is not None:
            connection.rollback()
            connection.close()
        raise StorageError(f"control database is unavailable: {error}") from error
