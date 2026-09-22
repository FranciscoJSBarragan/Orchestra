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

    def initialize_state(self, repo: Path) -> Path:
        private = repo / ".orchestra"
        (private / "artifacts").mkdir(parents=True)
        (private / ".gitignore").write_text(
            "# Orchestra task-private state; removed after successful delivery.\n*\n",
            encoding="utf-8",
        )
        (private / "plan.md").write_text("status: completed\n", encoding="utf-8")
        (private / "artifacts/report.md").write_text("done\n", encoding="utf-8")
        return private

    def commit_task_policy(self, command: list[str]) -> None:
        self.write_policy(self.task, command)
        self.git(self.task, "add", "orchestra.toml")
        self.git(self.task, "commit", "-q", "-m", "adjust check")
        self.task_sha = self.git(self.task, "rev-parse", "HEAD").stdout.strip()

    def run_helper(
        self,
        authorized: bool = True,
        *,
        expected_task_revision: str | None = None,
        checkout_mode: str = "managed",
        start_revision: str | None = None,
        preserve_task_resources: bool = False,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
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
            "--expected-task-revision",
            expected_task_revision or self.task_sha,
        ]
        if authorized:
            command.append("--authorized")
        if checkout_mode != "managed":
            command.extend(("--checkout-mode", checkout_mode))
        if preserve_task_resources:
            command.append("--preserve-task-resources")
        if start_revision:
            command.extend(("--start-revision", start_revision))
        result = subprocess.run(
            command,
            cwd=self.base,
            check=False,
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def test_host_owned_checkout_is_preserved_after_verified_integration(self) -> None:
        private = self.initialize_state(self.task)
        process, result = self.run_helper(preserve_task_resources=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["delivery_revision"], self.task_sha)
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), self.task_sha)
        self.assertEqual(self.git(self.task, "branch", "--show-current").stdout.strip(), "task")
        self.assertTrue((private / "plan.md").is_file())
        self.assertEqual(result["cleanup"], [])
        self.assertEqual(result["retained_resources"][0]["resource"], "local_branch")

    def test_preservation_does_not_waive_authority_or_head_checks(self) -> None:
        for options in ({"authorized": False}, {"expected_task_revision": "0" * 40}):
            with self.subTest(options=options):
                process, result = self.run_helper(preserve_task_resources=True, **options)
                self.assertEqual(process.returncode, 1)
                self.assertEqual(result["status"], "blocked")
                self.assertNotEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), self.task_sha)

    def test_clean_fast_forward_integrates_and_cleans_resources(self) -> None:
        self.initialize_state(self.task)
        result, payload = self.run_helper()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["task_sha"], self.task_sha)
        self.assertTrue(payload["delivery_verified"])
        self.assertEqual(payload["delivery_revision"], self.task_sha)
        self.assertEqual(
            self.git(self.base, "rev-parse", "HEAD").stdout.strip(), self.task_sha
        )
        self.assertEqual((self.base / "feature.txt").read_text(), "feature\n")
        self.assertFalse(self.task.exists())
        self.assertEqual(self.git(self.base, "branch", "--list", "task").stdout, "")
        self.assertEqual(payload["cleanup"], ["private_state", "worktree", "branch"])

    def test_hybrid_integration_restores_base_branch_and_preserves_checkout(self) -> None:
        self.git(self.base, "worktree", "remove", str(self.task))
        self.git(self.base, "switch", "task")
        start_revision = self.git(self.base, "rev-parse", "main").stdout.strip()
        private = self.initialize_state(self.base)

        self.task = self.base
        result, payload = self.run_helper(
            checkout_mode="hybrid", start_revision=start_revision
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(self.git(self.base, "branch", "--show-current").stdout.strip(), "main")
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), self.task_sha)
        self.assertTrue(self.base.exists())
        self.assertEqual(self.git(self.base, "branch", "--list", "task").stdout, "")
        self.assertEqual(payload["cleanup"], ["branch", "private_state"])
        self.assertEqual(payload["preserved"], ["worktree"])
        self.assertFalse(private.exists())

    def test_private_state_cleanup_failure_is_partial_and_preserves_resources(self) -> None:
        private = self.initialize_state(self.task)
        (private / "unknown.txt").write_text("do not delete\n", encoding="utf-8")

        result, payload = self.run_helper()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "partial")
        self.assertTrue(payload["delivery_verified"])
        self.assertEqual(payload["delivery_revision"], self.task_sha)
        self.assertIn("unknown entries", payload["reason"])
        self.assertEqual(payload["cleanup"], [])
        self.assertEqual(
            payload["preserved"], ["worktree", "branch", "private_state"]
        )
        self.assertTrue((private / "unknown.txt").is_file())
        self.assertTrue(self.task.exists())
        self.assertTrue(self.git(self.base, "branch", "--list", "task").stdout.strip())

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
        self.assertIn("dirty", payload["reason"])
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
        self.assertIn("check", payload["reason"])
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), base_before)
        self.assertTrue(self.task.exists())

    def test_manifest_revision_mismatch_blocks_before_configured_checks(self) -> None:
        self.commit_task_policy([sys.executable, "-c", "raise SystemExit(23)"])
        base_before = self.git(self.base, "rev-parse", "HEAD").stdout.strip()

        result, payload = self.run_helper(expected_task_revision=base_before)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("completed plan revision", payload["reason"])
        self.assertEqual(payload["expected_task_revision"], base_before)
        self.assertEqual(payload["task_revision"], self.task_sha)
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), base_before)
        self.assertEqual(self.git(self.task, "rev-parse", "HEAD").stdout.strip(), self.task_sha)
        self.assertTrue(self.task.exists())

    def test_expected_revision_must_be_a_full_commit_sha(self) -> None:
        base_before = self.git(self.base, "rev-parse", "HEAD").stdout.strip()

        result, payload = self.run_helper(expected_task_revision="HEAD")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("full commit SHA", payload["reason"])
        self.assertEqual(self.git(self.base, "rev-parse", "HEAD").stdout.strip(), base_before)
        self.assertEqual(self.git(self.task, "rev-parse", "HEAD").stdout.strip(), self.task_sha)

    def test_hybrid_check_cannot_move_starting_branch_before_integration(self) -> None:
        self.commit_task_policy(["git", "branch", "-f", "main", "HEAD"])
        self.git(self.base, "worktree", "remove", str(self.task))
        self.git(self.base, "switch", "task")
        start_revision = self.git(self.base, "rev-parse", "main").stdout.strip()
        self.task = self.base

        result, payload = self.run_helper(
            checkout_mode="hybrid", start_revision=start_revision
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("starting branch changed", payload["reason"])
        self.assertEqual(
            self.git(self.base, "branch", "--show-current").stdout.strip(), "task"
        )

    def test_unmerged_moved_branch_is_preserved(self) -> None:
        self.commit_task_policy(["git", "commit", "--allow-empty", "-m", "check moved head"])
        captured = self.task_sha

        result, payload = self.run_helper()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("changed", payload["reason"])
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
