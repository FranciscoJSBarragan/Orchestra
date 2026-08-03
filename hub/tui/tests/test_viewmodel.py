"""Tests for the TUI view-model (pure functions, no textual import)."""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

import support  # noqa: F401  (sys.path setup)
from orchestra_hub_tui.viewmodel import (
    attention_flags,
    build_tree,
    phase_progress,
    snapshot_age,
    task_rows,
)


def _artifact(kind: str, phase: int, available: bool = True) -> dict:
    return {"id": f"{kind}-{phase}", "kind": kind, "phase": phase,
            "revision": "b" * 40, "producer": "agent-1",
            "created_at": "2026-08-03T17:00:00Z", "available": available}


class PhaseProgressTest(unittest.TestCase):
    def test_no_plan_phases_returns_none(self) -> None:
        self.assertIsNone(phase_progress([_artifact("plan-overview", 0)]))
        self.assertIsNone(phase_progress([]))

    def test_planned_without_work_is_phase_one(self) -> None:
        artifacts = [_artifact("plan-phase", 1), _artifact("plan-phase", 2)]
        self.assertEqual(phase_progress(artifacts), (1, 2))

    def test_work_artifacts_advance_current_phase(self) -> None:
        artifacts = [
            _artifact("plan-overview", 0),
            _artifact("plan-phase", 1),
            _artifact("plan-phase", 2),
            _artifact("plan-phase", 3),
            _artifact("implementation-report", 1),
            _artifact("review-report", 1),
            _artifact("implementation-report", 2),
        ]
        self.assertEqual(phase_progress(artifacts), (2, 3))

    def test_unavailable_work_artifacts_do_not_count(self) -> None:
        artifacts = [
            _artifact("plan-phase", 1),
            _artifact("plan-phase", 2),
            _artifact("implementation-report", 2, available=False),
        ]
        self.assertEqual(phase_progress(artifacts), (1, 2))


def _task(**overrides: object) -> dict:
    task = {
        "id": "task-1",
        "label": "Task One",
        "repository": "/repos/alpha",
        "worktree": "/wt/alpha-task",
        "branch": "orchestra/task-one",
        "base_revision": "a" * 40,
        "head_revision": "b" * 40,
        "tier": "standard",
        "stage": "implementation",
        "status": "active",
        "summary": "working",
        "blocker": "",
        "next_action": "continue",
        "created_at": "2026-08-03T10:00:00Z",
        "updated_at": "2026-08-03T11:00:00Z",
        "material_fingerprint": "sha256:" + "0" * 64,
        "stale": False,
    }
    task.update(overrides)
    return task


def _summary() -> dict:
    return {
        "status": "ok",
        "material_fingerprint_version": 1,
        "repositories": [
            {"path": "/repos/alpha", "name": "Alpha", "pinned": False,
             "observed": True, "active_tasks": 1, "completed_tasks": 1},
            {"path": "/repos/pinned", "name": "Pinned", "pinned": True,
             "observed": False, "active_tasks": 0, "completed_tasks": 0},
        ],
        "tasks": [
            _task(id="done-1", label="Done", status="completed",
                  repository="/repos/alpha"),
            _task(id="task-1", repository="/repos/alpha"),
        ],
        "attention": [],
    }


class BuildTreeTest(unittest.TestCase):
    def test_repositories_preserved_including_pinned_empty(self) -> None:
        tree = build_tree(_summary())
        self.assertEqual([node.name for node in tree], ["Alpha", "Pinned"])
        self.assertEqual(tree[1].tasks, ())
        self.assertEqual(tree[1].active, 0)
        self.assertEqual(tree[1].completed, 0)

    def test_tasks_grouped_and_active_first(self) -> None:
        tree = build_tree(_summary())
        alpha = tree[0]
        self.assertEqual(alpha.active, 1)
        self.assertEqual(alpha.completed, 1)
        self.assertEqual([task["id"] for task in alpha.tasks],
                         ["task-1", "done-1"])

    def test_task_with_unlisted_repository_still_appears(self) -> None:
        summary = _summary()
        summary["tasks"].append(_task(id="task-2", repository="/repos/other"))
        tree = build_tree(summary)
        names = [node.path for node in tree]
        self.assertIn("/repos/other", names)


class TaskRowsTest(unittest.TestCase):
    def test_rows_are_ordered_and_stringified(self) -> None:
        rows = task_rows(_task(stale=True))
        self.assertEqual(rows[0], ("label", "Task One"))
        keys = [key for key, _ in rows]
        self.assertEqual(keys, [
            "label", "tier", "stage", "status", "branch", "worktree",
            "summary", "blocker", "next_action", "created_at",
            "updated_at", "stale",
        ])
        self.assertEqual(dict(rows)["stale"], "true")

    def test_missing_field_renders_empty(self) -> None:
        task = _task()
        del task["summary"]
        self.assertEqual(dict(task_rows(task))["summary"], "")


class AttentionFlagsTest(unittest.TestCase):
    def test_blocker_flag(self) -> None:
        self.assertEqual(attention_flags(_task(blocker="stuck")),
                         frozenset({"blocker"}))

    def test_completed_task_with_blocker_has_no_flag(self) -> None:
        self.assertEqual(
            attention_flags(_task(blocker="stuck", status="completed")),
            frozenset(),
        )

    def test_stale_flag(self) -> None:
        self.assertEqual(attention_flags(_task(stale=True)),
                         frozenset({"stale"}))

    def test_both_flags(self) -> None:
        self.assertEqual(attention_flags(_task(blocker="x", stale=True)),
                         frozenset({"blocker", "stale"}))

    def test_clean_task_has_no_flags(self) -> None:
        self.assertEqual(attention_flags(_task()), frozenset())


class SnapshotAgeTest(unittest.TestCase):
    NOW = datetime(2026, 8, 3, 12, 0, 0, tzinfo=timezone.utc)

    def test_minutes(self) -> None:
        self.assertEqual(
            snapshot_age("2026-08-03T11:57:00Z", self.NOW), "3 min ago"
        )

    def test_hours(self) -> None:
        self.assertEqual(
            snapshot_age("2026-08-03T10:00:00Z", self.NOW), "2 h ago"
        )

    def test_days(self) -> None:
        self.assertEqual(
            snapshot_age("2026-08-01T12:00:00Z", self.NOW), "2 d ago"
        )

    def test_just_now(self) -> None:
        self.assertEqual(
            snapshot_age("2026-08-03T11:59:40Z", self.NOW), "just now"
        )

    def test_unparsable_returns_raw(self) -> None:
        self.assertEqual(snapshot_age("not-a-time", self.NOW), "not-a-time")


if __name__ == "__main__":
    unittest.main()
