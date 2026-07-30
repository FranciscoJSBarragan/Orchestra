"""Behavioral tests for fail-soft Orchestra task coordination."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "codex/scripts/coordination.py"


class CoordinationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        self.state_root = root / "state"
        self.repository = root / "repository"
        self.task_one = root / "task-one"
        self.task_two = root / "task-two"
        self.repository.mkdir()
        self.git(self.repository, "init", "-q", "-b", "main")
        self.git(self.repository, "config", "user.name", "Orchestra Test")
        self.git(self.repository, "config", "user.email", "orchestra@example.invalid")
        (self.repository / "seed.txt").write_text("seed\n", encoding="utf-8")
        self.git(self.repository, "add", "seed.txt")
        self.git(self.repository, "commit", "-q", "-m", "seed")
        self.head = self.git(self.repository, "rev-parse", "HEAD").stdout.strip()
        self.git(
            self.repository,
            "worktree",
            "add",
            "-q",
            "-b",
            "orchestra/task-one",
            str(self.task_one),
            self.head,
        )
        self.git(
            self.repository,
            "worktree",
            "add",
            "-q",
            "-b",
            "orchestra/task-two",
            str(self.task_two),
            self.head,
        )

    def git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def command(self, *args: str) -> list[str]:
        return [
            sys.executable,
            str(HELPER),
            "--state-root",
            str(self.state_root),
            *args,
        ]

    def run_cli(self, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            self.command(*args),
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(result.stdout + result.stderr)
        return result, payload

    def create_task(self, worktree: Path, label: str = "Task") -> dict:
        result, payload = self.run_cli(
            "task",
            "create",
            "--repository",
            str(self.repository),
            "--worktree",
            str(worktree),
            "--base-revision",
            self.head,
            "--tier",
            "standard",
            "--label",
            label,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        return payload

    def test_tasks_are_idempotent_queryable_and_freely_updatable(self) -> None:
        first = self.create_task(self.task_one, "First")
        second = self.create_task(self.task_two, "Second")
        repeated = self.create_task(self.task_one, "Ignored duplicate")

        self.assertTrue(first["created"])
        self.assertTrue(second["created"])
        self.assertFalse(repeated["created"])
        self.assertEqual(repeated["task"]["id"], first["task"]["id"])

        task_id = first["task"]["id"]
        result, updated = self.run_cli(
            "task",
            "update",
            "--task",
            task_id,
            "--tier",
            "critical",
            "--stage",
            "custom-stage-without-transition",
            "--status",
            "paused-for-observation",
            "--summary",
            "  concise   material update ",
            "--blocker",
            "",
            "--next-action",
            "Resume directly",
            "--head-revision",
            self.head,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(updated["task"]["tier"], "critical")
        self.assertEqual(updated["task"]["stage"], "custom-stage-without-transition")
        self.assertEqual(updated["task"]["status"], "paused-for-observation")
        self.assertEqual(updated["task"]["summary"], "concise material update")

        result, listed = self.run_cli("task", "list")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({task["id"] for task in listed["tasks"]}, {
            first["task"]["id"],
            second["task"]["id"],
        })

        result, filtered = self.run_cli(
            "task", "list", "--status", "paused-for-observation"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([task["id"] for task in filtered["tasks"]], [task_id])

    def test_completed_task_does_not_reserve_a_reused_worktree_path(self) -> None:
        first = self.create_task(self.task_one)
        result, _ = self.run_cli(
            "task",
            "update",
            "--task",
            first["task"]["id"],
            "--status",
            "completed",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        second = self.create_task(self.task_one)

        self.assertTrue(second["created"])
        self.assertNotEqual(second["task"]["id"], first["task"]["id"])
        result, listed = self.run_cli("task", "list")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(listed["tasks"]), 2)

    def test_concurrent_activity_updates_keep_each_agent(self) -> None:
        task_id = self.create_task(self.task_one)["task"]["id"]
        processes = [
            subprocess.Popen(
                self.command(
                    "activity",
                    "set",
                    "--task",
                    task_id,
                    "--agent",
                    f"agent-{index}",
                    "--capability",
                    "runtime_verification",
                    "--state",
                    "running",
                    "--summary",
                    f"check {index}",
                ),
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for index in range(8)
        ]
        for process in processes:
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, stdout + stderr)
            self.assertEqual(json.loads(stdout)["status"], "ok")

        result, shown = self.run_cli("task", "show", "--task", task_id)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(shown["activities"]), 8)
        self.assertEqual(
            {activity["agent_id"] for activity in shown["activities"]},
            {f"agent-{index}" for index in range(8)},
        )

        result, cleared = self.run_cli(
            "activity",
            "clear",
            "--task",
            task_id,
            "--agent",
            "agent-0",
            "--capability",
            "runtime_verification",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(cleared["cleared"])

    def test_concurrent_task_creation_uses_one_active_snapshot(self) -> None:
        processes = [
            subprocess.Popen(
                self.command(
                    "task",
                    "create",
                    "--repository",
                    str(self.repository),
                    "--worktree",
                    str(self.task_one),
                    "--base-revision",
                    self.head,
                    "--tier",
                    "standard",
                    "--label",
                    f"Concurrent {index}",
                ),
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for index in range(8)
        ]
        payloads = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, stdout + stderr)
            payloads.append(json.loads(stdout))

        self.assertEqual(sum(payload["created"] for payload in payloads), 1)
        self.assertEqual(
            len({payload["task"]["id"] for payload in payloads}),
            1,
        )
        result, listed = self.run_cli("task", "list")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(listed["tasks"]), 1)

    def test_artifacts_are_atomic_private_and_queryable(self) -> None:
        task_id = self.create_task(self.task_one)["task"]["id"]
        report = Path(self.temporary_directory.name) / "context.md"
        report.write_text("# Context\n\nEvidence.\n", encoding="utf-8")
        status_before = self.git(
            self.task_one, "status", "--porcelain=v1", "--untracked-files=all"
        ).stdout

        result, published = self.run_cli(
            "artifact",
            "put",
            "--task",
            task_id,
            "--kind",
            "repository-context",
            "--revision",
            self.head,
            "--producer",
            "analyst-1",
            "--file",
            str(report),
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        artifact = published["artifact"]
        destination = Path(artifact["path"])
        self.assertTrue(destination.is_file())
        self.assertEqual(destination.read_text(encoding="utf-8"), report.read_text())
        self.assertIn("/.git/worktrees/task-one/orchestra/artifacts/", destination.as_posix())
        self.assertEqual(destination.stat().st_mode & 0o777, 0o600)
        self.assertEqual(
            self.git(
                self.task_one, "status", "--porcelain=v1", "--untracked-files=all"
            ).stdout,
            status_before,
        )

        result, listed = self.run_cli(
            "artifact",
            "list",
            "--task",
            task_id,
            "--kind",
            "repository-context",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([item["id"] for item in listed["artifacts"]], [artifact["id"]])
        self.assertTrue(listed["artifacts"][0]["available"])

        result, fetched = self.run_cli(
            "artifact",
            "get",
            "--task",
            task_id,
            "--artifact",
            artifact["id"],
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(fetched["status"], "ok")
        self.assertEqual(fetched["artifact"]["path"], str(destination))

    def test_plan_phases_and_replacements_remain_exact_distinct_artifacts(self) -> None:
        task_id = self.create_task(self.task_one)["task"]["id"]
        root = Path(self.temporary_directory.name)
        phase_one = root / "phase-one.md"
        phase_two = root / "phase-two.md"
        phase_one_replacement = root / "phase-one-replacement.md"
        phase_one.write_text("# Phase 1\n\nOriginal.\n", encoding="utf-8")
        phase_two.write_text("# Phase 2\n\nIndependent.\n", encoding="utf-8")
        phase_one_replacement.write_text(
            "# Phase 1\n\nComplete replacement.\n",
            encoding="utf-8",
        )

        published = []
        for phase, source in (
            (1, phase_one),
            (2, phase_two),
            (1, phase_one_replacement),
        ):
            result, payload = self.run_cli(
                "artifact",
                "put",
                "--task",
                task_id,
                "--kind",
                "plan-phase",
                "--phase",
                str(phase),
                "--revision",
                self.head,
                "--producer",
                "planner-1",
                "--file",
                str(source),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            published.append(payload["artifact"])

        result, listed = self.run_cli(
            "artifact",
            "list",
            "--task",
            task_id,
            "--kind",
            "plan-phase",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(listed["artifacts"]), 3)
        self.assertEqual(
            {artifact["id"] for artifact in listed["artifacts"]},
            {artifact["id"] for artifact in published},
        )
        self.assertEqual(
            [artifact["phase"] for artifact in published],
            [1, 2, 1],
        )
        self.assertEqual(len({artifact["path"] for artifact in published}), 3)

        result, original = self.run_cli(
            "artifact",
            "get",
            "--task",
            task_id,
            "--artifact",
            published[0]["id"],
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            Path(original["artifact"]["path"]).read_text(encoding="utf-8"),
            phase_one.read_text(encoding="utf-8"),
        )

    def test_rejects_unsafe_inputs_and_unrelated_worktrees(self) -> None:
        task_id = self.create_task(self.task_one)["task"]["id"]
        source = Path(self.temporary_directory.name) / "source.md"
        source.write_text("safe\n", encoding="utf-8")
        symlink = Path(self.temporary_directory.name) / "source-link.md"
        symlink.symlink_to(source)

        result, payload = self.run_cli(
            "artifact",
            "put",
            "--task",
            task_id,
            "--kind",
            "context",
            "--revision",
            self.head,
            "--producer",
            "analyst",
            "--file",
            str(symlink),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "invalid")

        binary = Path(self.temporary_directory.name) / "binary.md"
        binary.write_bytes(b"\xff")
        result, payload = self.run_cli(
            "artifact",
            "put",
            "--task",
            task_id,
            "--kind",
            "context",
            "--revision",
            self.head,
            "--producer",
            "analyst",
            "--file",
            str(binary),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "invalid")

        unrelated = Path(self.temporary_directory.name) / "unrelated"
        unrelated.mkdir()
        self.git(unrelated, "init", "-q", "-b", "main")
        self.git(unrelated, "config", "user.name", "Orchestra Test")
        self.git(unrelated, "config", "user.email", "orchestra@example.invalid")
        (unrelated / "file.txt").write_text("unrelated\n", encoding="utf-8")
        self.git(unrelated, "add", "file.txt")
        self.git(unrelated, "commit", "-q", "-m", "unrelated")
        result, payload = self.run_cli(
            "task",
            "create",
            "--repository",
            str(self.repository),
            "--worktree",
            str(unrelated),
            "--base-revision",
            self.head,
            "--tier",
            "standard",
            "--label",
            "Invalid",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "invalid")

    def test_removed_worktree_keeps_metadata_and_marks_artifact_unavailable(self) -> None:
        task_id = self.create_task(self.task_one)["task"]["id"]
        report = Path(self.temporary_directory.name) / "report.md"
        report.write_text("report\n", encoding="utf-8")
        _, published = self.run_cli(
            "artifact",
            "put",
            "--task",
            task_id,
            "--kind",
            "review",
            "--revision",
            self.head,
            "--producer",
            "reviewer",
            "--file",
            str(report),
        )
        self.git(self.repository, "worktree", "remove", str(self.task_one))

        result, shown = self.run_cli("task", "show", "--task", task_id)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(shown["task"]["worktree"], str(self.task_one.resolve()))
        self.assertFalse(shown["artifacts"][0]["available"])

        result, fetched = self.run_cli(
            "artifact",
            "get",
            "--task",
            task_id,
            "--artifact",
            published["artifact"]["id"],
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(fetched["status"], "unavailable")

    def test_damaged_database_is_reported_without_replacement(self) -> None:
        self.state_root.mkdir()
        database = self.state_root / "state.sqlite3"
        database.write_bytes(b"not a sqlite database")
        before = database.read_bytes()

        result, payload = self.run_cli("task", "list")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "unavailable")
        self.assertEqual(database.read_bytes(), before)

    def test_empty_existing_database_is_safely_initialized(self) -> None:
        self.state_root.mkdir()
        database = self.state_root / "state.sqlite3"
        database.touch()

        result, payload = self.run_cli("task", "list")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload, {"status": "ok", "tasks": []})
        self.assertEqual(database.stat().st_mode & 0o777, 0o600)
        with sqlite3.connect(database) as connection:
            self.assertEqual(
                connection.execute("PRAGMA user_version").fetchone()[0],
                1,
            )

    def test_partial_version_zero_database_is_not_reconstructed(self) -> None:
        self.state_root.mkdir()
        database = self.state_root / "state.sqlite3"
        with sqlite3.connect(database) as connection:
            connection.execute("CREATE TABLE interrupted (id TEXT PRIMARY KEY)")
        before = database.read_bytes()

        result, payload = self.run_cli("task", "list")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "unavailable")
        self.assertIn("schema version: 0", payload["reason"])
        self.assertEqual(database.read_bytes(), before)

    def test_concurrent_empty_database_initialization_converges(self) -> None:
        processes = [
            subprocess.Popen(
                self.command("task", "list"),
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in range(8)
        ]
        for process in processes:
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, stdout + stderr)
            self.assertEqual(json.loads(stdout), {"status": "ok", "tasks": []})
        database = self.state_root / "state.sqlite3"
        self.assertEqual(database.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.state_root.stat().st_mode & 0o777, 0o700)

    def test_revision_lengths_are_exact_and_states_remain_descriptive(self) -> None:
        task_id = self.create_task(self.task_one)["task"]["id"]
        for revision in ("a" * 41, "b" * 63):
            result, payload = self.run_cli(
                "task",
                "update",
                "--task",
                task_id,
                "--head-revision",
                revision,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(payload["status"], "invalid")

        for revision in (self.head, "c" * 64):
            result, payload = self.run_cli(
                "task",
                "update",
                "--task",
                task_id,
                "--head-revision",
                revision,
                "--stage",
                "free-form-stage",
                "--status",
                "paused-for-observation",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(payload["task"]["head_revision"], revision)
            self.assertEqual(payload["task"]["stage"], "free-form-stage")
            self.assertEqual(payload["task"]["status"], "paused-for-observation")

    def test_state_root_symlink_is_unavailable(self) -> None:
        target = Path(self.temporary_directory.name) / "real-state"
        target.mkdir()
        self.state_root.symlink_to(target, target_is_directory=True)

        result, payload = self.run_cli("task", "list")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "unavailable")

    def test_cli_validation_errors_are_compact_json(self) -> None:
        result = subprocess.run(
            self.command("task", "show"),
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "invalid")
        self.assertNotIn("blocked", payload)


if __name__ == "__main__":
    unittest.main()
