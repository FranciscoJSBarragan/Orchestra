"""Server-rendered panel escaping and section tests (SPEC §9, §11 / PLAN Task 7)."""
from __future__ import annotations

import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import support  # noqa: F401  # path setup before orchestra_hub imports

from orchestra_hub.api import summary_payload  # noqa: E402
from orchestra_hub.config import HubConfig, PinnedRepository  # noqa: E402
from orchestra_hub.panel import render_degraded, render_panel  # noqa: E402


NOW = datetime(2026, 8, 2, 19, 0, tzinfo=timezone.utc)
REPO_PATH = "/obs/alpha"


class PanelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state_root = Path(tempfile.mkdtemp())
        self.database = support.create_state_db(self.state_root)
        self.config = HubConfig(
            state_root=self.state_root,
            port=7343,
            stale_after_minutes=60,
            pinned_repositories=(
                PinnedRepository(path="/pinned/repo", name="Pinned"),
            ),
        )

    def _summary(self) -> dict:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        try:
            return summary_payload(connection, self.config, NOW)
        finally:
            connection.close()

    def test_hostile_payloads_are_escaped(self) -> None:
        support.insert_task(
            self.database,
            label="<script>alert(1)</script>",
            summary="<img src=x onerror=alert(2)>",
            blocker='"><svg onload=alert(3)>',
            next_action='<b onmouseover=alert(4)>go</b>',
            repository=REPO_PATH,
            updated_at="2026-08-02T18:48:00Z",
        )
        html = render_panel(self._summary(), NOW)

        for raw in (
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(2)>",
            '"><svg onload=alert(3)>',
            "<b onmouseover=alert(4)>go</b>",
        ):
            self.assertNotIn(raw, html)

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)

    def test_required_sections_age_and_refresh(self) -> None:
        support.insert_task(
            self.database,
            label="Blocked task",
            repository=REPO_PATH,
            blocker="waiting on review",
            updated_at="2026-08-02T18:48:00Z",
        )
        html = render_panel(self._summary(), NOW)

        self.assertIn("Possible attention", html)
        self.assertIn("Repositories", html)
        self.assertIn("12 min ago", html)
        self.assertIn('http-equiv="refresh"', html)

    def test_render_degraded_standalone(self) -> None:
        html = render_degraded("missing", "database not found")
        self.assertIn("degraded", html.lower())
        self.assertIn("missing", html)
