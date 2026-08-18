"""Secure SQLite storage for the local Orchestra prepared-task Kanban."""

from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import stat


SCHEMA_VERSION = 6
PREPARATION_STATES = ("legacy", "draft", "ready", "adopted", "completed")
OWNER_HARNESSES = ("codex", "cursor", "grok")
TASKS_TABLE_SQL = """
    CREATE TABLE tasks (
        id TEXT PRIMARY KEY,
        short_id TEXT COLLATE NOCASE UNIQUE,
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
        preparation_status TEXT NOT NULL DEFAULT 'draft'
            CHECK (preparation_status IN ('legacy', 'draft', 'ready', 'adopted', 'completed')),
        prepared_revision TEXT,
        repository_context_digest TEXT,
        specification_digest TEXT,
        specification_confirmed_at TEXT,
        adopted_thread_id TEXT,
        adopted_harness TEXT CHECK (
            adopted_harness IS NULL OR adopted_harness IN ('codex', 'cursor', 'grok')
        ),
        adopted_revision TEXT,
        adopted_at TEXT,
        previous_thread_id TEXT,
        previous_harness TEXT CHECK (
            previous_harness IS NULL OR previous_harness IN ('codex', 'cursor', 'grok')
        ),
        transfer_generation INTEGER NOT NULL DEFAULT 0,
        transfer_requested_at TEXT,
        completed_at TEXT,
        initiative_id TEXT REFERENCES task_initiatives(id),
        decomposition_reason TEXT,
        repository_common_dir TEXT,
        completed_revision TEXT,
        delivered_task_revision TEXT,
        delivery_revision TEXT,
        delivery_kind TEXT CHECK (
            delivery_kind IS NULL OR delivery_kind IN ('local-integration', 'pr-merge')
        ),
        delivered_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
"""
SCHEMA = (
    """
    CREATE TABLE task_initiatives (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        brief TEXT NOT NULL,
        source_task_id TEXT NOT NULL UNIQUE,
        idempotency_key TEXT NOT NULL UNIQUE,
        manifest_digest TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    TASKS_TABLE_SQL,
    """
    CREATE TABLE task_dependencies (
        task_id TEXT NOT NULL REFERENCES tasks(id),
        blocked_by_task_id TEXT NOT NULL REFERENCES tasks(id),
        condition TEXT NOT NULL CHECK (condition IN ('completed', 'delivered')),
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        PRIMARY KEY (task_id, blocked_by_task_id),
        CHECK (task_id != blocked_by_task_id)
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
    # These three tables are retained for read-only compatibility with tasks
    # created by the retired App Server launcher. New code never writes them.
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
    """
    CREATE TABLE control_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    )
    """,
    "INSERT INTO control_metadata VALUES ('next_short_sequence', '1')",
    "CREATE INDEX tasks_disposition_rank ON tasks(disposition, rank, created_at)",
    "CREATE INDEX tasks_initiative ON tasks(initiative_id, rank, created_at)",
    "CREATE INDEX dependencies_blocked_by ON task_dependencies(blocked_by_task_id, task_id)",
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
    try:
        if stat.S_IMODE(os.lstat(root).st_mode) != 0o700:
            os.chmod(root, 0o700)
    except OSError as error:
        raise StorageError(f"cannot restrict state root: {error}") from error
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


def _migrate_v2(connection: sqlite3.Connection) -> None:
    """Add prepared-task fields without assigning IDs to legacy rows."""
    statements = (
        "ALTER TABLE tasks ADD COLUMN short_id TEXT",
        "ALTER TABLE tasks ADD COLUMN preparation_status TEXT NOT NULL DEFAULT 'legacy' CHECK (preparation_status IN ('legacy', 'draft', 'ready', 'adopted', 'completed'))",
        "ALTER TABLE tasks ADD COLUMN prepared_revision TEXT",
        "ALTER TABLE tasks ADD COLUMN repository_context_digest TEXT",
        "ALTER TABLE tasks ADD COLUMN specification_digest TEXT",
        "ALTER TABLE tasks ADD COLUMN specification_confirmed_at TEXT",
        "ALTER TABLE tasks ADD COLUMN adopted_thread_id TEXT",
        "ALTER TABLE tasks ADD COLUMN adopted_revision TEXT",
        "ALTER TABLE tasks ADD COLUMN adopted_at TEXT",
        "ALTER TABLE tasks ADD COLUMN previous_thread_id TEXT",
        "ALTER TABLE tasks ADD COLUMN transfer_generation INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE tasks ADD COLUMN transfer_requested_at TEXT",
        "ALTER TABLE tasks ADD COLUMN completed_at TEXT",
        "CREATE UNIQUE INDEX tasks_short_id ON tasks(short_id COLLATE NOCASE) WHERE short_id IS NOT NULL",
        "CREATE TABLE control_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)",
        "INSERT INTO control_metadata VALUES ('next_short_sequence', '1')",
    )
    for statement in statements:
        connection.execute(statement)


def _migrate_v3(connection: sqlite3.Connection) -> None:
    """Add immutable initiative relationships and delivery evidence."""
    statements = (
        "CREATE TABLE task_initiatives (id TEXT PRIMARY KEY, title TEXT NOT NULL, brief TEXT NOT NULL, source_task_id TEXT NOT NULL UNIQUE, idempotency_key TEXT NOT NULL UNIQUE, manifest_digest TEXT NOT NULL, created_at TEXT NOT NULL)",
        "ALTER TABLE tasks ADD COLUMN initiative_id TEXT REFERENCES task_initiatives(id)",
        "ALTER TABLE tasks ADD COLUMN decomposition_reason TEXT",
        "ALTER TABLE tasks ADD COLUMN repository_common_dir TEXT",
        "ALTER TABLE tasks ADD COLUMN completed_revision TEXT",
        "ALTER TABLE tasks ADD COLUMN delivered_task_revision TEXT",
        "ALTER TABLE tasks ADD COLUMN delivery_revision TEXT",
        "ALTER TABLE tasks ADD COLUMN delivery_kind TEXT CHECK (delivery_kind IS NULL OR delivery_kind IN ('local-integration', 'pr-merge'))",
        "ALTER TABLE tasks ADD COLUMN delivered_at TEXT",
        "CREATE TABLE task_dependencies (task_id TEXT NOT NULL REFERENCES tasks(id), blocked_by_task_id TEXT NOT NULL REFERENCES tasks(id), condition TEXT NOT NULL CHECK (condition IN ('completed', 'delivered')), reason TEXT NOT NULL, created_at TEXT NOT NULL, PRIMARY KEY (task_id, blocked_by_task_id), CHECK (task_id != blocked_by_task_id))",
        "CREATE INDEX tasks_initiative ON tasks(initiative_id, rank, created_at)",
        "CREATE INDEX dependencies_blocked_by ON task_dependencies(blocked_by_task_id, task_id)",
    )
    for statement in statements:
        connection.execute(statement)


def _migrate_v5(connection: sqlite3.Connection) -> None:
    """Namespace historical owner identities by execution harness."""
    statements = (
        "ALTER TABLE tasks ADD COLUMN adopted_harness TEXT CHECK (adopted_harness IS NULL OR adopted_harness IN ('codex', 'cursor'))",
        "ALTER TABLE tasks ADD COLUMN previous_harness TEXT CHECK (previous_harness IS NULL OR previous_harness IN ('codex', 'cursor'))",
        "UPDATE tasks SET adopted_harness = 'codex' WHERE adopted_thread_id IS NOT NULL",
        "UPDATE tasks SET previous_harness = 'codex' WHERE previous_thread_id IS NOT NULL",
    )
    for statement in statements:
        connection.execute(statement)


def _migrate_v6(connection: sqlite3.Connection) -> None:
    """Widen owner harness CHECK constraints to include grok."""
    row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'tasks'"
    ).fetchone()
    if row is not None and row[0] is not None and "'grok'" in row[0]:
        return
    columns = [
        info[1] for info in connection.execute("PRAGMA table_info(tasks)").fetchall()
    ]
    quoted = ", ".join(f'"{name}"' for name in columns)
    connection.execute(TASKS_TABLE_SQL.replace("CREATE TABLE tasks", "CREATE TABLE tasks_v6", 1))
    connection.execute(f"INSERT INTO tasks_v6 ({quoted}) SELECT {quoted} FROM tasks")
    connection.execute("DROP TABLE tasks")
    connection.execute("ALTER TABLE tasks_v6 RENAME TO tasks")
    connection.execute(
        "CREATE INDEX IF NOT EXISTS tasks_disposition_rank ON tasks(disposition, rank, created_at)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS tasks_initiative ON tasks(initiative_id, rank, created_at)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS tasks_short_id ON tasks(short_id COLLATE NOCASE) "
        "WHERE short_id IS NOT NULL"
    )


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
        elif version in {2, 3, 4, 5}:
            if version == 2:
                _migrate_v2(connection)
            if version in {2, 3}:
                _migrate_v3(connection)
            if version in {2, 3, 4}:
                _migrate_v5(connection)
            connection.commit()
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("BEGIN IMMEDIATE")
            _migrate_v6(connection)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            connection.commit()
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("BEGIN IMMEDIATE")
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
