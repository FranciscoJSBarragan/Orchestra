"""Allowlisted API payloads and attention model tests (SPEC §7-8 / PLAN Task 6)."""
from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import support  # noqa: F401  # path setup before orchestra_hub imports

from orchestra_hub.api import (  # noqa: E402
    ACTIVITY_FIELDS,
    ARTIFACT_FIELDS,
    TASK_FIELDS,
    summary_payload,
    task_detail_payload,
    tasks_payload,
)
from orchestra_hub.config import HubConfig, PinnedRepository  # noqa: E402
from orchestra_hub.fingerprint import MATERIAL_FINGERPRINT_VERSION  # noqa: E402


NOW = datetime(2026, 8, 2, 19, 0, tzinfo=timezone.utc)
PINNED_PATH = "/pinned/repo"
OBS_PATH = "/obs/alpha"
TASK_PAYLOAD_KEYS = set(TASK_FIELDS) | {"material_fingerprint", "stale"}
ACTIVITY_PAYLOAD_KEYS = set(ACTIVITY_FIELDS)
ARTIFACT_PAYLOAD_KEYS = set(ARTIFACT_FIELDS) | {"available"}


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state_root = Path(tempfile.mkdtemp())
        self.database = support.create_state_db(self.state_root)
        self.config = HubConfig(
            state_root=self.state_root,
            port=7343,
            stale_after_minutes=60,
            pinned_repositories=(
                PinnedRepository(path=PINNED_PATH, name="Pinned"),
            ),
        )

    def _connect(self):
        import sqlite3

        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        return connection

    def test_task_payload_keys_are_exact_allowlist(self) -> None:
        support.insert_task(self.database, repository=OBS_PATH)
        connection = self._connect()
        try:
            payload = summary_payload(connection, self.config, NOW)
        finally:
            connection.close()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["material_fingerprint_version"],
            MATERIAL_FINGERPRINT_VERSION,
        )
        self.assertEqual(set(payload["tasks"][0]), TASK_PAYLOAD_KEYS)
        self.assertNotIn("generated_at", payload)

    def test_attention_rules(self) -> None:
        blocked = support.insert_task(
            self.database,
            id="blocked-task",
            label="Blocked",
            repository=OBS_PATH,
            blocker="waiting on review",
            updated_at="2026-08-02T18:30:00Z",
        )
        stale = support.insert_task(
            self.database,
            id="stale-task",
            label="Stale",
            repository=OBS_PATH,
            blocker="",
            updated_at="2026-08-02T17:00:00Z",
        )
        support.insert_task(
            self.database,
            id="completed-noise",
            label="Done",
            repository=OBS_PATH,
            status="completed",
            blocker="ignored blocker",
            updated_at="2026-08-02T16:00:00Z",
        )
        support.insert_task(
            self.database,
            id="fresh-task",
            label="Fresh",
            repository=OBS_PATH,
            blocker="",
            updated_at="2026-08-02T18:45:00Z",
        )

        connection = self._connect()
        try:
            payload = summary_payload(connection, self.config, NOW)
        finally:
            connection.close()

        attention = {
            entry["task_id"]: entry for entry in payload["attention"]
        }
        self.assertEqual(set(attention), {blocked["id"], stale["id"]})
        self.assertEqual(attention[blocked["id"]]["reasons"], ["blocker"])
        self.assertEqual(attention[stale["id"]]["reasons"], ["stale"])
        self.assertEqual(
            set(attention[blocked["id"]]),
            {
                "task_id",
                "label",
                "repository",
                "reasons",
                "blocker",
                "next_action",
                "updated_at",
            },
        )

    def test_repositories_aggregation_and_pinned_zero_tasks(self) -> None:
        support.insert_task(
            self.database,
            id="alpha-active",
            repository=OBS_PATH,
            status="active",
            updated_at="2026-08-02T18:50:00Z",
        )
        support.insert_task(
            self.database,
            id="alpha-done",
            repository=OBS_PATH,
            status="completed",
            updated_at="2026-08-02T18:40:00Z",
        )

        connection = self._connect()
        try:
            payload = summary_payload(connection, self.config, NOW)
        finally:
            connection.close()

        by_path = {entry["path"]: entry for entry in payload["repositories"]}
        self.assertEqual(
            by_path[OBS_PATH],
            {
                "path": OBS_PATH,
                "name": "alpha",
                "pinned": False,
                "observed": True,
                "active_tasks": 1,
                "completed_tasks": 1,
            },
        )
        self.assertEqual(
            by_path[PINNED_PATH],
            {
                "path": PINNED_PATH,
                "name": "Pinned",
                "pinned": True,
                "observed": False,
                "active_tasks": 0,
                "completed_tasks": 0,
            },
        )
        names_paths = [
            (entry["name"], entry["path"]) for entry in payload["repositories"]
        ]
        self.assertEqual(names_paths, sorted(names_paths))

    def test_tasks_payload_status_filter_and_ordering(self) -> None:
        older = support.insert_task(
            self.database,
            id="completed-older",
            repository=OBS_PATH,
            status="completed",
            updated_at="2026-08-02T17:00:00Z",
        )
        newer = support.insert_task(
            self.database,
            id="completed-newer",
            repository=OBS_PATH,
            status="completed",
            updated_at="2026-08-02T18:00:00Z",
        )
        support.insert_task(
            self.database,
            id="still-active",
            repository=OBS_PATH,
            status="active",
            updated_at="2026-08-02T18:30:00Z",
        )

        connection = self._connect()
        try:
            payload = tasks_payload(
                connection, self.config, NOW, status="completed"
            )
        finally:
            connection.close()

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["material_fingerprint_version"],
            MATERIAL_FINGERPRINT_VERSION,
        )
        ids = [task["id"] for task in payload["tasks"]]
        self.assertEqual(ids, [newer["id"], older["id"]])
        self.assertTrue(all(task["status"] == "completed" for task in payload["tasks"]))
        self.assertNotIn("generated_at", payload)

    def test_task_detail_availability_without_path(self) -> None:
        task = support.insert_task(self.database, repository=OBS_PATH)
        present = self.state_root / "present-artifact.md"
        present.write_text("ok\n", encoding="utf-8")
        missing = self.state_root / "missing-artifact.md"
        support.insert_artifact(
            self.database,
            task["id"],
            path=str(present),
            id="art-present",
            created_at="2026-08-02T18:10:00Z",
        )
        support.insert_artifact(
            self.database,
            task["id"],
            path=str(missing),
            id="art-missing",
            created_at="2026-08-02T18:20:00Z",
        )
        support.insert_activity(
            self.database,
            task["id"],
            agent_id="agent-z",
            capability="implementation",
            updated_at="2026-08-02T18:05:00Z",
        )
        support.insert_activity(
            self.database,
            task["id"],
            agent_id="agent-a",
            capability="review",
            updated_at="2026-08-02T18:15:00Z",
        )

        connection = self._connect()
        try:
            payload = task_detail_payload(
                connection, self.config, NOW, task["id"]
            )
            unknown = task_detail_payload(
                connection, self.config, NOW, "absent-id"
            )
        finally:
            connection.close()

        self.assertIsNone(unknown)
        assert payload is not None
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(
            payload["material_fingerprint_version"],
            MATERIAL_FINGERPRINT_VERSION,
        )
        self.assertEqual(set(payload["task"]), TASK_PAYLOAD_KEYS)
        self.assertNotIn("generated_at", payload)

        self.assertEqual(
            [activity["agent_id"] for activity in payload["activities"]],
            ["agent-a", "agent-z"],
        )
        for activity in payload["activities"]:
            self.assertEqual(set(activity), ACTIVITY_PAYLOAD_KEYS)

        self.assertEqual(
            [artifact["id"] for artifact in payload["artifacts"]],
            ["art-missing", "art-present"],
        )
        by_id = {artifact["id"]: artifact for artifact in payload["artifacts"]}
        self.assertEqual(set(by_id["art-present"]), ARTIFACT_PAYLOAD_KEYS)
        self.assertTrue(by_id["art-present"]["available"])
        self.assertFalse(by_id["art-missing"]["available"])
        self.assertNotIn("path", by_id["art-present"])
        self.assertNotIn("path", by_id["art-missing"])

    def test_stale_flag_uses_threshold(self) -> None:
        support.insert_task(
            self.database,
            id="barely-fresh",
            repository=OBS_PATH,
            updated_at="2026-08-02T18:00:00Z",
        )
        support.insert_task(
            self.database,
            id="just-stale",
            repository=OBS_PATH,
            updated_at="2026-08-02T17:59:00Z",
        )
        connection = self._connect()
        try:
            payload = tasks_payload(connection, self.config, NOW)
        finally:
            connection.close()
        by_id = {task["id"]: task for task in payload["tasks"]}
        self.assertFalse(by_id["barely-fresh"]["stale"])
        self.assertTrue(by_id["just-stale"]["stale"])
        self.assertEqual(
            NOW - datetime.fromisoformat("2026-08-02T18:00:00+00:00"),
            timedelta(minutes=60),
        )


if __name__ == "__main__":
    unittest.main()
