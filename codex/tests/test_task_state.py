"""Behavioral tests for worktree-local Orchestra task state."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "codex/scripts/task_state.py"
SCRIPTS = ROOT / "codex/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
_SPEC = importlib.util.spec_from_file_location("orchestra_task_state", HELPER)
assert _SPEC is not None and _SPEC.loader is not None
task_state = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(task_state)


class TaskStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.repo = Path(self.temporary_directory.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Orchestra Test")
        self.git("config", "user.email", "orchestra@example.invalid")
        (self.repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        self.git("add", "tracked.txt")
        self.git("commit", "-q", "-m", "initial")

    def git(self, *args: str, fail_test: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode and fail_test:
            self.fail(result.stdout + result.stderr)
        return result

    def test_init_is_ignored_idempotent_and_resolvable(self) -> None:
        first = task_state.initialize_private_task_state(self.repo)
        self.assertEqual(first["status"], "ok")
        self.assertTrue(first["initialized"])
        self.assertEqual(first["layout"], "workspace")
        state = self.repo / ".orchestra"
        self.assertEqual(Path(first["state"]), state.resolve())
        self.assertTrue((state / ".gitignore").is_file())
        self.assertTrue((state / "artifacts").is_dir())

        (state / "plan.md").write_text("status: active\n", encoding="utf-8")
        (state / "artifacts/01-repository-context.md").write_text(
            "evidence\n", encoding="utf-8"
        )
        self.assertEqual(
            self.git("status", "--porcelain=v1", "--untracked-files=all").stdout,
            "",
        )

        second = task_state.initialize_private_task_state(self.repo)
        resolved = task_state.resolve(self.repo)
        self.assertFalse(second["initialized"])
        self.assertEqual(resolved["layout"], "workspace")
        self.assertTrue(resolved["exists"])

    def test_cleanup_removes_only_owned_state(self) -> None:
        self.assertEqual(
            task_state.initialize_private_task_state(self.repo)["status"], "ok"
        )
        unrelated = self.repo / "unrelated.txt"
        unrelated.write_text("keep\n", encoding="utf-8")

        result = task_state.cleanup(self.repo)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["cleanup"], ["private_state"])
        self.assertFalse((self.repo / ".orchestra").exists())
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep\n")
        self.assertEqual(task_state.cleanup(self.repo)["cleanup"], [])

    def test_tracked_collision_is_rejected_without_changes(self) -> None:
        collision = self.repo / ".orchestra"
        collision.mkdir()
        (collision / "tracked.txt").write_text("owned by project\n", encoding="utf-8")
        self.git("add", "-f", ".orchestra/tracked.txt")
        self.git("commit", "-q", "-m", "tracked collision")

        result = task_state.initialize_private_task_state(self.repo)

        self.assertEqual(result["status"], "blocked")
        self.assertTrue((collision / "tracked.txt").is_file())
        self.assertFalse((collision / ".gitignore").exists())

    def test_unknown_directory_and_symlink_are_rejected(self) -> None:
        state = self.repo / ".orchestra"
        state.mkdir()
        (state / "notes.txt").write_text("user data\n", encoding="utf-8")
        result = task_state.initialize_private_task_state(self.repo)
        self.assertEqual(result["status"], "blocked")
        self.assertTrue((state / "notes.txt").exists())

        (state / "notes.txt").unlink()
        state.rmdir()
        state.symlink_to(self.repo / "tracked.txt")
        result = task_state.cleanup(self.repo)
        self.assertEqual(result["status"], "blocked")
        self.assertTrue(state.is_symlink())

    def test_legacy_state_is_resolved_and_cleaned_without_migration(self) -> None:
        git_dir = Path(self.git("rev-parse", "--absolute-git-dir").stdout.strip())
        legacy = git_dir / "orchestra"
        (legacy / "artifacts").mkdir(parents=True)
        (legacy / "plan.md").write_text("status: active\n", encoding="utf-8")
        (legacy / "artifacts/01-plan-overview.md").write_text(
            "legacy\n", encoding="utf-8"
        )

        initialized = task_state.initialize_private_task_state(self.repo)
        self.assertEqual(initialized["status"], "ok")
        self.assertEqual(initialized["layout"], "legacy")
        self.assertFalse(initialized["initialized"])
        self.assertFalse((self.repo / ".orchestra").exists())

        cleaned = task_state.cleanup(self.repo)
        self.assertEqual(cleaned["status"], "ok")
        self.assertFalse(legacy.exists())


if __name__ == "__main__":
    unittest.main()
