"""Fixture verification for Task 1 support helpers."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

import support
import coordination  # noqa: E402  # path setup happens in support


class SupportFixtureTests(unittest.TestCase):
    def test_schema_version_and_insert_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database = support.create_state_db(Path(temporary))
            connection = sqlite3.connect(database)
            try:
                version = connection.execute("PRAGMA user_version").fetchone()[0]
                self.assertEqual(version, coordination.SCHEMA_VERSION)

                task = support.insert_task(database)
                support.insert_activity(database, task["id"])
                support.insert_artifact(database, task["id"], path="/tmp/report.md")

                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM activities").fetchone()[0],
                    1,
                )
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0],
                    1,
                )
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
