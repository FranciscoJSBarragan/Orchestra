"""Behavioral tests for scoped dirty-worktree adoption."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SOURCE_ROOT = Path(__file__).resolve().parents[2]
HELPER = SOURCE_ROOT / "codex/scripts/adopt_worktree.py"
SCRIPTS = SOURCE_ROOT / "codex/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
_SPEC = importlib.util.spec_from_file_location("orchestra_adopt_worktree", HELPER)
assert _SPEC is not None and _SPEC.loader is not None
adopt = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(adopt)


class AdoptWorktreeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        self.base = root / "repo"
        self.task = root / "task"
        self.base.mkdir()
        self.git(self.base, "init", "-q", "-b", "main")
        self.git(self.base, "config", "user.name", "Orchestra Test")
        self.git(self.base, "config", "user.email", "orchestra@example.invalid")
        self.git(self.base, "config", "core.hooksPath", ".git/hooks")
        (self.base / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        (self.base / "tracked.txt").write_text("base\n", encoding="utf-8")
        (self.base / "keep.txt").write_text("keep\n", encoding="utf-8")
        (self.base / "gone.txt").write_text("gone\n", encoding="utf-8")
        self.git(self.base, "add", ".gitignore", "tracked.txt", "keep.txt", "gone.txt")
        self.git(self.base, "commit", "-q", "-m", "initial")
        self.head = self.git(self.base, "rev-parse", "HEAD").stdout.strip()
        self.git(
            self.base,
            "worktree",
            "add",
            "-b",
            "orchestra/adopt-task",
            str(self.task),
            self.head,
        )
        self.paths_file = root / "paths.json"

    def git(self, repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "--literal-pathspecs", *args],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def write_paths(self, *paths: str) -> None:
        self.paths_file.write_text(json.dumps(list(paths)) + "\n", encoding="utf-8")

    def source_snapshot(self) -> dict[str, object]:
        status = self.git(
            self.base, "status", "--porcelain=v1", "--untracked-files=all"
        ).stdout
        index = self.git(self.base, "ls-files", "-s").stdout
        branch = self.git(self.base, "symbolic-ref", "--short", "HEAD").stdout.strip()
        head = self.git(self.base, "rev-parse", "HEAD").stdout.strip()
        files = {
            path.name: path.read_bytes()
            for path in self.base.iterdir()
            if path.is_file() and not path.name.startswith(".")
        }
        return {
            "status": status,
            "index": index,
            "branch": branch,
            "head": head,
            "files": files,
        }

    def run_helper(self, *paths: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        self.write_paths(*paths)
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--source-worktree",
                str(self.base),
                "--task-worktree",
                str(self.task),
                "--expected-source-head",
                self.head,
                "--paths-file",
                str(self.paths_file),
            ],
            cwd=self.base,
            check=False,
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def test_imports_mixed_dirty_paths_and_preserves_source(self) -> None:
        (self.base / "tracked.txt").write_text("changed\n", encoding="utf-8")
        (self.base / "added.txt").write_text("new\n", encoding="utf-8")
        (self.base / "gone.txt").unlink()
        (self.base / "binary.bin").write_bytes(b"\x00\x01\xff Orchestra")
        (self.base / "link.txt").symlink_to("tracked.txt")
        executable = self.base / "tool.sh"
        executable.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        before = self.source_snapshot()

        result, payload = self.run_helper(
            "tracked.txt",
            "added.txt",
            "gone.txt",
            "binary.bin",
            "link.txt",
            "tool.sh",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["head"], self.head)
        self.assertEqual(
            payload["imported_paths"],
            [
                "tracked.txt",
                "added.txt",
                "gone.txt",
                "binary.bin",
                "link.txt",
                "tool.sh",
            ],
        )
        self.assertEqual((self.task / "tracked.txt").read_text(encoding="utf-8"), "changed\n")
        self.assertEqual((self.task / "added.txt").read_text(encoding="utf-8"), "new\n")
        self.assertFalse((self.task / "gone.txt").exists())
        self.assertEqual((self.task / "binary.bin").read_bytes(), b"\x00\x01\xff Orchestra")
        self.assertTrue((self.task / "link.txt").is_symlink())
        self.assertEqual(os.readlink(self.task / "link.txt"), "tracked.txt")
        self.assertTrue((self.task / "tool.sh").stat().st_mode & stat.S_IXUSR)
        self.assertEqual((self.task / "keep.txt").read_text(encoding="utf-8"), "keep\n")
        self.assertIn(
            "tracked.txt",
            self.git(self.task, "status", "--porcelain=v1", "--untracked-files=all").stdout,
        )
        self.assertEqual(self.source_snapshot(), before)

    def test_rejects_unsafe_ignored_gitlink_dirty_wrong_head_and_special(self) -> None:
        (self.base / "ignored.txt").write_text("secret\n", encoding="utf-8")
        self.assertEqual(self.run_helper("ignored.txt")[1]["status"], "blocked")
        self.assertEqual(self.run_helper("../outside.txt")[1]["status"], "blocked")

        outside_directory = Path(self.temporary_directory.name) / "outside"
        outside_directory.mkdir()
        (outside_directory / "escaped.txt").write_text("outside\n", encoding="utf-8")
        (self.base / "escape").symlink_to(outside_directory, target_is_directory=True)
        self.assertEqual(self.run_helper("escape/escaped.txt")[1]["status"], "blocked")

        with mock.patch.object(adopt, "_load_paths", return_value=(["tracked\0.txt"], None)):
            nul_payload = adopt.adopt_worktree(
                self.base, self.task, self.head, self.paths_file
            )
        self.assertEqual(nul_payload["status"], "blocked")
        self.assertIn("NUL", nul_payload["reason"])

        gitlink_sha = "0123456789abcdef0123456789abcdef01234567"
        self.git(
            self.base,
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{gitlink_sha},vendor/mod",
        )
        self.assertEqual(self.run_helper("vendor/mod")[1]["status"], "blocked")
        self.git(self.base, "rm", "--cached", "-f", "--", "vendor/mod")

        (self.task / "dirty.txt").write_text("dirty\n", encoding="utf-8")
        self.assertEqual(self.run_helper("tracked.txt")[1]["status"], "blocked")
        (self.task / "dirty.txt").unlink()

        self.write_paths("tracked.txt")
        (self.base / "tracked.txt").write_text("changed\n", encoding="utf-8")
        wrong = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--source-worktree",
                str(self.base),
                "--task-worktree",
                str(self.task),
                "--expected-source-head",
                "0" * 40,
                "--paths-file",
                str(self.paths_file),
            ],
            cwd=self.base,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(wrong.stdout)["status"], "blocked")
        (self.base / "tracked.txt").write_text("base\n", encoding="utf-8")

        if hasattr(os, "mkfifo"):
            fifo = self.base / "pipe.fifo"
            os.mkfifo(fifo)
            self.addCleanup(lambda: fifo.unlink(missing_ok=True))
            self.assertEqual(self.run_helper("pipe.fifo")[1]["status"], "blocked")

    def test_rejects_addition_collision_on_clean_task(self) -> None:
        (self.base / "added.txt").write_text("new\n", encoding="utf-8")
        collision = self.task / "added.txt"
        collision.write_text("preexisting secret\n", encoding="utf-8")
        self.git(self.base, "config", "extensions.worktreeConfig", "true")
        exclude_file = Path(self.temporary_directory.name) / "task.exclude"
        exclude_file.write_text("added.txt\n", encoding="utf-8")
        self.git(self.task, "config", "--worktree", "core.excludesFile", str(exclude_file))
        self.assertEqual(
            self.git(self.task, "status", "--porcelain=v1", "--untracked-files=all").stdout,
            "",
        )
        before = collision.read_text(encoding="utf-8")

        result, payload = self.run_helper("added.txt")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(collision.read_text(encoding="utf-8"), before)

    def test_reports_applied_paths_after_write_failure(self) -> None:
        (self.base / "tracked.txt").write_text("changed\n", encoding="utf-8")
        (self.base / "added.txt").write_text("new\n", encoding="utf-8")
        self.write_paths("tracked.txt", "added.txt")
        original = adopt._apply_one
        calls = {"count": 0}

        def fail_after_first(source: Path, task: Path, relative: str):
            calls["count"] += 1
            if calls["count"] == 1:
                return original(source, task, relative)
            return "simulated apply failure"

        with mock.patch.object(adopt, "_apply_one", side_effect=fail_after_first):
            payload = adopt.adopt_worktree(
                self.base, self.task, self.head, self.paths_file
            )

        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["applied_paths"], ["tracked.txt", "added.txt"])
        self.assertEqual((self.task / "tracked.txt").read_text(encoding="utf-8"), "changed\n")
        self.assertFalse((self.task / "added.txt").exists())


if __name__ == "__main__":
    unittest.main()
