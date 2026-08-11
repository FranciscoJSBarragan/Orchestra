"""Domain operations for durable task intake."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator
import uuid

from .db import StorageError, connect


class ControlError(Exception):
    """A validated user or runtime control error."""

    def __init__(self, status: str, reason: str) -> None:
        super().__init__(reason)
        self.status = status
        self.reason = reason


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def compact(value: str, limit: int) -> str:
    return " ".join(value.split())[:limit]


def bounded(value: str, limit: int) -> str:
    return value.strip()[:limit]


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def row_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    for key in (
        "last_result_json",
        "retained_resources_json",
        "result_json",
        "params_json",
        "response_json",
    ):
        value = result.get(key)
        if isinstance(value, str):
            try:
                result[key.removesuffix("_json")] = json.loads(value)
            except json.JSONDecodeError:
                result[key.removesuffix("_json")] = None
            del result[key]
    return result


class ControlService:
    def __init__(self, state_root: Path | None = None) -> None:
        self.state_root = state_root

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        try:
            connection = connect(self.state_root)
        except StorageError as error:
            raise ControlError("unavailable", str(error)) from error
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def create_task(
        self,
        *,
        title: str,
        brief: str,
        source_harness: str,
        source_conversation: str = "",
        source_message: str = "",
        repository: str | None = None,
        idempotency_key: str,
    ) -> dict[str, Any]:
        title = compact(title, 160)
        brief = bounded(brief, 8000)
        if not title or not brief or not idempotency_key.strip():
            raise ControlError("invalid", "title, brief, and idempotency key are required")
        timestamp = now()
        task_id = str(uuid.uuid4())
        with self._connection() as connection:
            existing = connection.execute(
                "SELECT * FROM tasks WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if existing is not None:
                expected = (
                    title,
                    brief,
                    compact(source_harness, 80),
                    compact(source_conversation, 500),
                    compact(source_message, 500),
                    repository,
                )
                observed = tuple(
                    existing[key]
                    for key in (
                        "title",
                        "brief",
                        "source_harness",
                        "source_conversation",
                        "source_message",
                        "repository",
                    )
                )
                if observed != expected:
                    raise ControlError("invalid", "idempotency key conflicts with another task")
                return row_dict(existing)
            rank = connection.execute(
                "SELECT COALESCE(MAX(rank), 0) + 1 FROM tasks WHERE disposition = 'open'"
            ).fetchone()[0]
            try:
                connection.execute(
                    """
                    INSERT INTO tasks VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
                    """,
                    (
                        task_id,
                        title,
                        brief,
                        compact(source_harness, 80),
                        compact(source_conversation, 500),
                        compact(source_message, 500),
                        repository,
                        rank,
                        idempotency_key,
                        timestamp,
                        timestamp,
                    ),
                )
            except sqlite3.IntegrityError:
                existing = connection.execute(
                    "SELECT * FROM tasks WHERE idempotency_key = ?", (idempotency_key,)
                ).fetchone()
                if existing is None:
                    raise
                return row_dict(existing)
            return row_dict(connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

    def get_task(self, task_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                raise ControlError("invalid", f"unknown task: {task_id}")
            result = row_dict(row)
            result["notes"] = [
                row_dict(item)
                for item in connection.execute(
                    "SELECT * FROM task_notes WHERE task_id = ? ORDER BY created_at, id",
                    (task_id,),
                ).fetchall()
            ]
            result["runs"] = [
                row_dict(item)
                for item in connection.execute(
                    "SELECT * FROM runs WHERE task_id = ? ORDER BY created_at, id",
                    (task_id,),
                ).fetchall()
            ]
            return result

    def list_tasks(self, include_archived: bool = False) -> list[dict[str, Any]]:
        where = "" if include_archived else "WHERE disposition = 'open'"
        with self._connection() as connection:
            tasks = [
                row_dict(row)
                for row in connection.execute(
                    f"SELECT * FROM tasks {where} ORDER BY rank, created_at, id"
                ).fetchall()
            ]
            for task in tasks:
                latest = connection.execute(
                    "SELECT * FROM runs WHERE task_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
                    (task["id"],),
                ).fetchone()
                task["latest_run"] = row_dict(latest) if latest is not None else None
                task["pending_interactions"] = connection.execute(
                    """
                    SELECT COUNT(*) FROM interactions i JOIN runs r ON r.id = i.run_id
                    WHERE r.task_id = ? AND i.status = 'pending'
                    """,
                    (task["id"],),
                ).fetchone()[0]
            return tasks

    def add_note(
        self,
        *,
        task_id: str,
        body: str,
        source_harness: str,
        source_reference: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        body = bounded(body, 8000)
        if not body or not idempotency_key.strip():
            raise ControlError("invalid", "note body and idempotency key are required")
        with self._connection() as connection:
            if connection.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,)).fetchone() is None:
                raise ControlError("invalid", f"unknown task: {task_id}")
            existing = connection.execute(
                "SELECT * FROM task_notes WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if existing is not None:
                expected = (
                    task_id,
                    body,
                    compact(source_harness, 80),
                    compact(source_reference, 500),
                )
                observed = tuple(
                    existing[key]
                    for key in ("task_id", "body", "source_harness", "source_reference")
                )
                if observed != expected:
                    raise ControlError("invalid", "idempotency key conflicts with another note")
                return row_dict(existing)
            note_id = str(uuid.uuid4())
            connection.execute(
                "INSERT INTO task_notes VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    note_id,
                    task_id,
                    body,
                    compact(source_harness, 80),
                    compact(source_reference, 500),
                    idempotency_key,
                    now(),
                ),
            )
            return row_dict(connection.execute("SELECT * FROM task_notes WHERE id = ?", (note_id,)).fetchone())

    def set_archived(self, task_id: str, archived: bool) -> dict[str, Any]:
        disposition = "archived" if archived else "open"
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if row is None:
                raise ControlError("invalid", f"unknown task: {task_id}")
            active = connection.execute(
                "SELECT active_turn_id FROM runs WHERE task_id = ? AND active_turn_id IS NOT NULL",
                (task_id,),
            ).fetchone()
            if archived and active is not None:
                raise ControlError("busy", "task has an unresolved active turn")
            connection.execute(
                "UPDATE tasks SET disposition = ?, updated_at = ? WHERE id = ?",
                (disposition, now(), task_id),
            )
            return row_dict(connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

    def prepare_run(self, task_id: str, repository: str, base_revision: str) -> dict[str, Any]:
        with self._connection() as connection:
            task = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if task is None:
                raise ControlError("invalid", f"unknown task: {task_id}")
            if task["disposition"] != "open":
                raise ControlError("invalid", "archived task must be restored before starting")
            connection.execute(
                "UPDATE tasks SET repository = ?, updated_at = ? WHERE id = ?",
                (repository, now(), task_id),
            )
            existing = connection.execute(
                """
                SELECT * FROM runs WHERE task_id = ?
                AND status NOT IN ('held', 'closed', 'cancelled')
                ORDER BY created_at DESC LIMIT 1
                """,
                (task_id,),
            ).fetchone()
            if existing is not None:
                return row_dict(existing)
            run_id = str(uuid.uuid4())
            timestamp = now()
            connection.execute(
                """
                INSERT INTO runs
                (id, task_id, repository, base_revision, delivery, status,
                 retained_resources_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'hold', 'starting', '[]', ?, ?)
                """,
                (run_id, task_id, repository, base_revision, timestamp, timestamp),
            )
            return row_dict(connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone())

    def latest_run(self, task_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM runs WHERE task_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if row is None:
                raise ControlError("invalid", f"task has no run: {task_id}")
            return row_dict(row)

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
            if row is None:
                raise ControlError("invalid", f"unknown run: {run_id}")
            result = row_dict(row)
            result["turns"] = [
                row_dict(item)
                for item in connection.execute(
                    "SELECT * FROM turns WHERE run_id = ? ORDER BY created_at, id", (run_id,)
                ).fetchall()
            ]
            return result

    def prepare_turn(
        self, *, run_id: str, text: str, idempotency_key: str, response_to: str | None = None
    ) -> dict[str, Any]:
        text = text.strip()
        if not text or not idempotency_key.strip():
            raise ControlError("invalid", "turn text and idempotency key are required")
        with self._connection() as connection:
            run = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
            if run is None:
                raise ControlError("invalid", f"unknown run: {run_id}")
            if run["cancel_requested_at"] is not None:
                raise ControlError("cancelled", "run is cancelled; reopen it before continuing")
            existing = connection.execute(
                "SELECT * FROM turns WHERE idempotency_key = ?", (idempotency_key,)
            ).fetchone()
            if existing is not None:
                if existing["run_id"] != run_id or existing["input_digest"] != digest(text):
                    raise ControlError("invalid", "idempotency key conflicts with another turn")
                return row_dict(existing)
            if run["active_turn_id"] is not None:
                raise ControlError("busy", "run has an unresolved active turn")
            turn_id = str(uuid.uuid4())
            timestamp = now()
            connection.execute(
                "INSERT INTO turns VALUES (?, ?, ?, ?, ?, ?, 'prepared', NULL, NULL, ?, ?)",
                (turn_id, run_id, idempotency_key, digest(text), text, response_to, timestamp, timestamp),
            )
            return row_dict(connection.execute("SELECT * FROM turns WHERE id = ?", (turn_id,)).fetchone())

    def request_cancel(self, task_id: str) -> dict[str, Any]:
        timestamp = now()
        with self._connection() as connection:
            run = connection.execute(
                "SELECT * FROM runs WHERE task_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if run is None:
                raise ControlError("invalid", f"task has no run: {task_id}")
            if run["cancel_requested_at"] is None:
                status = "cancelling" if run["active_turn_id"] is not None else "cancelled"
                cancelled_at = None if run["active_turn_id"] is not None else timestamp
                connection.execute(
                    "UPDATE runs SET cancel_requested_at = ?, cancelled_at = ?, status = ?, updated_at = ? WHERE id = ?",
                    (timestamp, cancelled_at, status, timestamp, run["id"]),
                )
            return row_dict(connection.execute("SELECT * FROM runs WHERE id = ?", (run["id"],)).fetchone())

    def cancellation_requested(self, run_id: str) -> bool:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT cancel_requested_at FROM runs WHERE id = ?", (run_id,)
            ).fetchone()
            return row is not None and row["cancel_requested_at"] is not None

    def mark_cancelled(self, run_id: str, turn_record_id: str) -> dict[str, Any]:
        timestamp = now()
        with self._connection() as connection:
            turn = connection.execute(
                "SELECT * FROM turns WHERE id = ? AND run_id = ?", (turn_record_id, run_id)
            ).fetchone()
            if turn is None:
                raise ControlError("invalid", "run or turn no longer exists")
            connection.execute(
                """
                UPDATE runs SET active_turn_id = NULL, status = 'cancelled',
                cancelled_at = ?, updated_at = ? WHERE id = ?
                """,
                (timestamp, timestamp, run_id),
            )
            connection.execute(
                "UPDATE turns SET status = 'interrupted', updated_at = ? WHERE id = ?",
                (timestamp, turn_record_id),
            )
            return row_dict(connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone())

    def mark_needs_user(self, run_id: str, turn_record_id: str) -> dict[str, Any]:
        timestamp = now()
        with self._connection() as connection:
            turn = connection.execute(
                "SELECT * FROM turns WHERE id = ? AND run_id = ?", (turn_record_id, run_id)
            ).fetchone()
            if turn is None:
                raise ControlError("invalid", "run or turn no longer exists")
            connection.execute(
                "UPDATE runs SET active_turn_id = NULL, status = 'waiting_user', updated_at = ? WHERE id = ?",
                (timestamp, run_id),
            )
            connection.execute(
                "UPDATE turns SET status = 'interrupted', updated_at = ? WHERE id = ?",
                (timestamp, turn_record_id),
            )
            return row_dict(connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone())

    def reopen(self, task_id: str) -> dict[str, Any]:
        timestamp = now()
        with self._connection() as connection:
            run = connection.execute(
                "SELECT * FROM runs WHERE task_id = ? ORDER BY created_at DESC, id DESC LIMIT 1",
                (task_id,),
            ).fetchone()
            if run is None:
                raise ControlError("invalid", f"task has no run: {task_id}")
            if run["active_turn_id"] is not None:
                raise ControlError("busy", "run still has an active turn")
            if run["cancel_requested_at"] is None and run["status"] != "cancelled":
                raise ControlError("invalid", "run is not cancelled")
            connection.execute(
                """
                UPDATE runs SET cancel_requested_at = NULL, cancelled_at = NULL,
                status = 'ready', updated_at = ? WHERE id = ?
                """,
                (timestamp, run["id"]),
            )
            return row_dict(connection.execute("SELECT * FROM runs WHERE id = ?", (run["id"],)).fetchone())

    def record_interaction(
        self,
        *,
        run_id: str,
        turn_record_id: str,
        thread_uuid: str,
        turn_uuid: str,
        item_id: str | None,
        method: str,
        params: dict[str, Any],
        fingerprint: str,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        timestamp = now()
        encoded = json.dumps(params, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._connection() as connection:
            resolved = connection.execute(
                """
                SELECT * FROM interactions WHERE run_id = ? AND fingerprint = ?
                AND status = 'resolved' ORDER BY created_at, id LIMIT 1
                """,
                (run_id, fingerprint),
            ).fetchone()
            if resolved is not None:
                connection.execute(
                    "UPDATE interactions SET status = 'consumed', updated_at = ? WHERE id = ?",
                    (timestamp, resolved["id"]),
                )
                decoded = json.loads(resolved["response_json"])
                return row_dict(connection.execute("SELECT * FROM interactions WHERE id = ?", (resolved["id"],)).fetchone()), decoded
            pending = connection.execute(
                """
                SELECT * FROM interactions WHERE run_id = ? AND fingerprint = ?
                AND status = 'pending' ORDER BY created_at, id LIMIT 1
                """,
                (run_id, fingerprint),
            ).fetchone()
            if pending is None:
                interaction_id = str(uuid.uuid4())
                connection.execute(
                    """
                    INSERT INTO interactions
                    (id, run_id, turn_record_id, thread_uuid, turn_uuid, item_id,
                     method, params_json, fingerprint, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
                    """,
                    (interaction_id, run_id, turn_record_id, thread_uuid, turn_uuid,
                     item_id, method, encoded, fingerprint, timestamp, timestamp),
                )
                pending = connection.execute(
                    "SELECT * FROM interactions WHERE id = ?", (interaction_id,)
                ).fetchone()
            return row_dict(pending), None

    def list_interactions(self, task_id: str, include_consumed: bool = False) -> list[dict[str, Any]]:
        condition = "" if include_consumed else "AND i.status != 'consumed'"
        with self._connection() as connection:
            return [
                row_dict(row)
                for row in connection.execute(
                    f"""
                    SELECT i.* FROM interactions i JOIN runs r ON r.id = i.run_id
                    WHERE r.task_id = ? {condition} ORDER BY i.created_at, i.id
                    """,
                    (task_id,),
                ).fetchall()
            ]

    def resolve_interaction(self, interaction_id: str, response: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(response, dict):
            raise ControlError("invalid", "interaction response must be a JSON object")
        timestamp = now()
        encoded = json.dumps(response, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        with self._connection() as connection:
            row = connection.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,)).fetchone()
            if row is None:
                raise ControlError("invalid", f"unknown interaction: {interaction_id}")
            if row["status"] == "consumed":
                raise ControlError("invalid", "interaction response was already consumed")
            if row["status"] == "resolved":
                if row["response_json"] != encoded:
                    raise ControlError("invalid", "interaction already has a different response")
                return row_dict(row)
            connection.execute(
                "UPDATE interactions SET status = 'resolved', response_json = ?, updated_at = ? WHERE id = ?",
                (encoded, timestamp, interaction_id),
            )
            return row_dict(connection.execute("SELECT * FROM interactions WHERE id = ?", (interaction_id,)).fetchone())

    def update_transport(
        self,
        *,
        run_id: str,
        turn_record_id: str,
        thread_uuid: str | None = None,
        active_turn_id: str | None = None,
        completed_result: dict[str, Any] | None = None,
        ambiguous: str | None = None,
    ) -> dict[str, Any]:
        timestamp = now()
        with self._connection() as connection:
            run = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
            turn = connection.execute("SELECT * FROM turns WHERE id = ?", (turn_record_id,)).fetchone()
            if run is None or turn is None or turn["run_id"] != run_id:
                raise ControlError("invalid", "run or turn no longer exists")
            if thread_uuid is not None:
                connection.execute(
                    "UPDATE runs SET thread_uuid = ?, status = 'ready', updated_at = ? WHERE id = ?",
                    (thread_uuid, timestamp, run_id),
                )
            if active_turn_id is not None:
                connection.execute(
                    "UPDATE runs SET active_turn_id = ?, status = 'running', updated_at = ? WHERE id = ?",
                    (active_turn_id, timestamp, run_id),
                )
                connection.execute(
                    "UPDATE turns SET turn_uuid = ?, status = 'started', updated_at = ? WHERE id = ?",
                    (active_turn_id, timestamp, turn_record_id),
                )
            if completed_result is not None:
                kind = str(completed_result.get("kind", "blocked"))
                run_status = {
                    "implementation_complete": "held",
                    "blocked": "blocked",
                    "needs_reconciliation": "needs_reconciliation",
                }.get(kind, "waiting_user")
                encoded = json.dumps(completed_result, ensure_ascii=False, sort_keys=True)
                connection.execute(
                    """
                    UPDATE runs SET active_turn_id = NULL, last_turn_id = ?, status = ?,
                    last_result_kind = ?, last_result_json = ?, updated_at = ? WHERE id = ?
                    """,
                    (active_turn_id or turn["turn_uuid"], run_status, kind, encoded, timestamp, run_id),
                )
                connection.execute(
                    "UPDATE turns SET status = 'completed', result_json = ?, updated_at = ? WHERE id = ?",
                    (encoded, timestamp, turn_record_id),
                )
            if ambiguous is not None:
                result = {"kind": "needs_reconciliation", "message": compact(ambiguous, 1000)}
                encoded = json.dumps(result, sort_keys=True)
                connection.execute(
                    "UPDATE runs SET status = 'needs_reconciliation', last_result_kind = 'needs_reconciliation', last_result_json = ?, updated_at = ? WHERE id = ?",
                    (encoded, timestamp, run_id),
                )
                connection.execute(
                    "UPDATE turns SET status = 'needs_reconciliation', result_json = ?, updated_at = ? WHERE id = ?",
                    (encoded, timestamp, turn_record_id),
                )
            return row_dict(connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone())
