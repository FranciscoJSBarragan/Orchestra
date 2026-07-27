"""Temporary-repository tests for conservative local integration and cleanup."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "codex/scripts/integrate_local.py"


class LocalIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        self.base = root / "base"
        self.task = root / "task"
        self.base.mkdir()
        self.git(self.base, "init", "-q", "-b", "main")
        self.git(self.base, "config", "user.name", "Orchestra Test")
        self.git(self.base, "config", "user.email", "orchestra@example.invalid")
        self.write_policy(self.base, [sys.executable, "-c", "pass"])
        (self.base / "base.txt").write_text("base\n", encoding="utf-8")
        self.git(self.base, "add", "base.txt", "orchestra.toml")
        self.git(self.base, "commit", "-q", "-m", "base")
        self.git(self.base, "branch", "task")
        self.git(self.base, "worktree", "add", "-q", str(self.task), "task")
        (self.task / "feature.txt").write_text("feature\n", encoding="utf-8")
        self.git(self.task, "add", "feature.txt")
        self.git(self.task, "commit", "-q", "-m", "feature")
        self.task_sha = self.git(self.task, "rev-parse", "HEAD").stdout.strip()

    def git(
        self, repo: Path, *args: str, fail_test: bool = True
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode and fail_test:
            self.fail(result.stdout + result.stderr)
        return result

    def write_policy(self, repo: Path, command: list[str], mode: str = "hybrid") -> None:
        argv = ", ".join(json.dumps(argument) for argument in command)
        (repo / "orchestra.toml").write_text(
            f'[delivery]\nmode = "{mode}"\n\n'
            f'[[checks]]\nname = "suite"\ncommand = [{argv}]\n',
            encoding="utf-8",
        )

    def commit_task_policy(self, command: list[str]) -> None:
        self.write_policy(self.task, command)
        self.git(self.task, "add", "orchestra.toml")
        self.git(self.task, "commit", "-q", "-m", "adjust check")
        self.task_sha = self.git(self.task, "rev-parse", "HEAD").stdout.strip()

    def run_helper(self, authorized: bool = True) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [
            sys.executable,
            str(HELPER),
            "--task-worktree",
            str(self.task),
            "--base-worktree",
            str(self.base),
            "--task-branch",
            "task",
            "--base-branch",
            "main",
        ]
        if authorized:
            command.append("--authorized")
        result = subprocess.run(
            command,
            cwd=self.base,
            check=False,
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def test_clean_fast_forward_integrates_and_cleans_resources(self) -> None:
        result, payload = self.run_helper()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["task_sha"], self.task_sha)
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), self.task_sha)
        self.assertEqual((self.base / "feature.txt").read_text(), "feature\n")
        self.assertFalse(self.task.exists())
        self.assertEqual(self.git(self.base, "branch", "--list", "task").stdout, "")
        self.assertEqual(payload["cleanup"], ["worktree", "branch"])

    def test_explicit_authority_is_required_without_mutation(self) -> None:
        base_before = self.git(self.base, "rev-parse", "HEAD").stdout.strip()

        result, payload = self.run_helper(authorized=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authorization", payload["reason"])
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), base_before)
        self.assertTrue(self.task.exists())

    def test_dirty_task_worktree_is_preserved(self) -> None:
        (self.task / "private.txt").write_text("private\n", encoding="utf-8")

        result, payload = self.run_helper()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("task worktree is dirty", payload["reason"])
        self.assertTrue((self.task / "private.txt").exists())
        self.assertTrue(self.git(self.base, "branch", "--list", "task").stdout.strip())

    def test_divergence_blocks_without_cleanup(self) -> None:
        (self.base / "base-only.txt").write_text("base change\n", encoding="utf-8")
        self.git(self.base, "add", "base-only.txt")
        self.git(self.base, "commit", "-q", "-m", "base diverges")
        base_before = self.git(self.base, "rev-parse", "HEAD").stdout.strip()

        result, payload = self.run_helper()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fast-forward", payload["reason"])
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), base_before)
        self.assertTrue(self.task.exists())
        self.assertTrue(self.git(self.base, "branch", "--list", "task").stdout.strip())

    def test_failed_check_blocks_before_integration(self) -> None:
        self.commit_task_policy([sys.executable, "-c", "raise SystemExit(5)"])
        base_before = self.git(self.base, "rev-parse", "HEAD").stdout.strip()

        result, payload = self.run_helper()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("check suite failed", payload["reason"])
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), base_before)
        self.assertTrue(self.task.exists())

    def test_unmerged_moved_branch_is_preserved(self) -> None:
        self.commit_task_policy(["git", "commit", "--allow-empty", "-m", "check moved head"])
        captured = self.task_sha

        result, payload = self.run_helper()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("checks changed the task worktree or HEAD", payload["reason"])
        moved = self.git(self.task, "rev-parse", "HEAD").stdout.strip()
        self.assertNotEqual(moved, captured)
        self.assertNotEqual(
            self.git(
                self.base, "merge-base", "--is-ancestor", moved, "main", fail_test=False
            ).returncode,
            0,
        )
        self.assertTrue(self.task.exists())
        self.assertTrue(self.git(self.base, "branch", "--list", "task").stdout.strip())


if __name__ == "__main__":
    unittest.main()
