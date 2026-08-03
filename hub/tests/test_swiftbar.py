"""SwiftBar plugin regression tests for IR-P3-001 and IR-P3-002."""
from __future__ import annotations

import importlib.util
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


PLUGIN_PATH = (
    Path(__file__).resolve().parents[1] / "swiftbar" / "orchestra_hub.1m.py"
)


def load_plugin():
    spec = importlib.util.spec_from_file_location(
        "orchestra_hub_swiftbar", PLUGIN_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def task(
    task_id: str,
    *,
    label: str = "Task",
    stage: str = "implementation",
    status: str = "active",
    blocker: str = "",
    next_action: str = "Continue",
    fingerprint: str = "fp-1",
) -> dict:
    return {
        "id": task_id,
        "label": label,
        "stage": stage,
        "status": status,
        "blocker": blocker,
        "next_action": next_action,
        "material_fingerprint": fingerprint,
    }


def attention_entry(
    task_id: str,
    *,
    label: str,
    reasons: list[str],
    blocker: str = "",
    next_action: str = "",
) -> dict:
    return {
        "task_id": task_id,
        "label": label,
        "reasons": reasons,
        "blocker": blocker,
        "next_action": next_action,
    }


def summary_payload(
    *,
    tasks: list[dict],
    attention: list[dict],
    version: str = "v1",
) -> dict:
    return {
        "status": "ok",
        "material_fingerprint_version": version,
        "tasks": tasks,
        "attention": attention,
    }


class SwiftBarPluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plugin = load_plugin()
        self.notifications: list[tuple[str, str]] = []
        self.saved_states: list[dict] = []

        def fake_notify(title: str, message: str) -> None:
            self.notifications.append((title, message))

        def fake_save(state: dict) -> None:
            self.saved_states.append(state)

        self.notify_patch = mock.patch.object(
            self.plugin, "notify", side_effect=fake_notify
        )
        self.save_patch = mock.patch.object(
            self.plugin, "save_state", side_effect=fake_save
        )
        self.load_patch = mock.patch.object(
            self.plugin, "load_state", return_value=None
        )
        self.fetch_patch = mock.patch.object(self.plugin, "fetch_summary")
        self.notify_patch.start()
        self.save_patch.start()
        self.load_patch.start()
        self.fetch_patch.start()

    def tearDown(self) -> None:
        self.notify_patch.stop()
        self.save_patch.stop()
        self.load_patch.stop()
        self.fetch_patch.stop()

    def run_main(self, summary: dict) -> str:
        self.plugin.fetch_summary.return_value = summary
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.plugin.main()
        return buffer.getvalue()

    def test_stale_only_first_baseline_emits_no_notification(self) -> None:
        stale = task("stale-1", label="Stale task", fingerprint="fp-stale")
        summary = summary_payload(
            tasks=[stale],
            attention=[
                attention_entry(
                    "stale-1",
                    label="Stale task",
                    reasons=["stale"],
                    next_action="Continue",
                )
            ],
        )

        output = self.run_main(summary)

        self.assertEqual(self.notifications, [])
        self.assertIn("O 1", output.splitlines()[0])
        self.assertEqual(len(self.saved_states), 1)

    def test_blocker_first_baseline_aggregates_blocker_entries_only(
        self,
    ) -> None:
        blocked = task(
            "blocked-1",
            label="Blocked task",
            blocker="waiting",
            fingerprint="fp-blocked",
        )
        stale = task("stale-1", label="Stale task", fingerprint="fp-stale")
        summary = summary_payload(
            tasks=[blocked, stale],
            attention=[
                attention_entry(
                    "blocked-1",
                    label="Blocked task",
                    reasons=["blocker"],
                    blocker="waiting",
                ),
                attention_entry(
                    "stale-1",
                    label="Stale task",
                    reasons=["stale"],
                    next_action="Continue",
                ),
            ],
        )

        self.run_main(summary)

        self.assertEqual(
            self.notifications,
            [("Orchestra Hub", "1 task(s) may need attention")],
        )

    def test_dynamic_text_cannot_inject_swiftbar_parameters_or_lines(
        self,
    ) -> None:
        injected = task(
            "inject-1",
            label="Evil|bash=/bin/echo param=1",
            stage="impl\nextra-line",
            status="active\rstatus-break",
            blocker="detail|href=http://evil.example",
            fingerprint="fp-inject",
        )
        summary = summary_payload(
            tasks=[injected],
            attention=[
                attention_entry(
                    "inject-1",
                    label="Evil|bash=/bin/echo param=1",
                    reasons=["blocker"],
                    blocker="detail|href=http://evil.example",
                )
            ],
        )

        output = self.run_main(summary)
        lines = output.splitlines()

        self.assertTrue(any("¦" in line for line in lines))
        self.assertNotIn("extra-line", lines)
        self.assertNotIn("status-break", lines)
        for line in lines:
            if "|" not in line:
                continue
            _text, params = line.split("|", 1)
            self.assertNotIn("bash=", params)
            self.assertNotIn("href=http://evil.example", params)
        attention_lines = [
            line
            for line in lines
            if line.startswith("Evil¦bash=/bin/echo param=1 (blocker)")
        ]
        self.assertEqual(
            attention_lines,
            ["Evil¦bash=/bin/echo param=1 (blocker) | color=red"],
        )
        detail_lines = [line for line in lines if line.startswith("-- ")]
        self.assertEqual(detail_lines, ["-- detail¦href=http://evil.example"])
        task_lines = [
            line
            for line in lines
            if line.startswith("Evil¦bash=/bin/echo param=1 — ")
        ]
        self.assertEqual(
            task_lines,
            ["Evil¦bash=/bin/echo param=1 — impl extra-line/active status-break"],
        )
        self.assertIn("Open panel | href=http://127.0.0.1:7343/", lines)


if __name__ == "__main__":
    unittest.main()
