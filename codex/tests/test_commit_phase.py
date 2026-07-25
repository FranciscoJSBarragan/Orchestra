"""Behavioral tests for the thin phase commit helper."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[2]
HELPER = SOURCE_ROOT / "codex/scripts/commit_phase.py"


class CommitPhaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Orchestra Test")
        self.git("config", "user.email", "orchestra@example.invalid")
        self.git("config", "core.hooksPath", ".git/hooks")
        self.write("target.txt", "base\n")
        self.write("unrelated.txt", "base\n")
        self.git("add", "target.txt", "unrelated.txt")
        self.git("commit", "-q", "-m", "initial")
        self.initial_sha = self.git("rev-parse", "HEAD").stdout.strip()
        self.message_file = Path(self.temporary_directory.name) / "message.txt"
        self.message_file.write_text(
            "Implement bounded phase\n\n"
            "Commit the accepted target path while preserving unrelated work.\n"
            "Validated by the focused helper tests.\n",
            encoding="utf-8",
        )

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", "--literal-pathspecs", *args],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def write(self, relative: str, content: str) -> None:
        (self.root / relative).write_text(content, encoding="utf-8")

    def run_helper(self, *paths: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [
            sys.executable,
            str(HELPER),
            "--repo",
            str(self.root),
            "--message-file",
            str(self.message_file),
        ]
        for path in paths:
            command.extend(("--path", path))
        result = subprocess.run(
            command,
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def test_commits_exact_path_and_returns_sha(self) -> None:
        self.write("target.txt", "changed\n")

        result, payload = self.run_helper("target.txt")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "committed")
        self.assertEqual(payload["sha"], self.git("rev-parse", "HEAD").stdout.strip())
        self.assertEqual(self.git("show", "HEAD:target.txt").stdout, "changed\n")

    def test_returns_nothing_to_commit_for_unchanged_path(self) -> None:
        result, payload = self.run_helper("target.txt")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload, {"status": "nothing_to_commit"})
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.initial_sha)

    def test_blocks_unrelated_staged_path_without_staging_target(self) -> None:
        self.write("target.txt", "target work\n")
        self.write("unrelated.txt", "staged elsewhere\n")
        self.git("add", "unrelated.txt")

        result, payload = self.run_helper("target.txt")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("unrelated staged paths: unrelated.txt", payload["reason"])
        self.assertEqual(self.git("diff", "--cached", "--name-only").stdout, "unrelated.txt\n")
        self.assertEqual(self.git("diff", "--name-only").stdout, "target.txt\n")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.initial_sha)

    def test_preserves_unrelated_unstaged_and_untracked_work(self) -> None:
        self.write("target.txt", "target work\n")
        self.write("unrelated.txt", "unstaged elsewhere\n")
        self.write("untracked.txt", "private work\n")

        result, payload = self.run_helper("target.txt")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "committed")
        self.assertEqual((self.root / "unrelated.txt").read_text(), "unstaged elsewhere\n")
        self.assertEqual((self.root / "untracked.txt").read_text(), "private work\n")
        status = self.git("status", "--short").stdout.splitlines()
        self.assertIn(" M unrelated.txt", status)
        self.assertIn("?? untracked.txt", status)
        self.assertNotIn("untracked.txt", self.git("ls-tree", "-r", "--name-only", "HEAD").stdout)

    def test_pathspec_metacharacters_are_literal(self) -> None:
        self.write("*.txt", "literal base\n")
        self.git("add", "--", "*.txt")
        self.git("commit", "-q", "-m", "add literal path")
        self.write("*.txt", "literal changed\n")
        self.write("target.txt", "must remain unstaged\n")

        result, payload = self.run_helper("*.txt")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "committed")
        self.assertEqual(self.git("show", "HEAD:*.txt").stdout, "literal changed\n")
        self.assertEqual(self.git("show", "HEAD:target.txt").stdout, "base\n")
        self.assertEqual(self.git("diff", "--name-only").stdout, "target.txt\n")

    def test_rename_authorizing_only_destination_blocks_without_commit(self) -> None:
        self.git("mv", "target.txt", "renamed.txt")

        result, payload = self.run_helper("renamed.txt")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("unrelated staged paths: target.txt", payload["reason"])
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.initial_sha)
        staged = set(
            self.git(
                "diff", "--cached", "--no-renames", "--name-only"
            ).stdout.splitlines()
        )
        self.assertEqual(staged, {"target.txt", "renamed.txt"})

    def test_rename_authorizing_source_and_destination_commits(self) -> None:
        self.git("mv", "target.txt", "renamed.txt")

        result, payload = self.run_helper("target.txt", "renamed.txt")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "committed")
        tree = self.git("ls-tree", "-r", "--name-only", "HEAD").stdout.splitlines()
        self.assertIn("renamed.txt", tree)
        self.assertNotIn("target.txt", tree)

    def test_invalid_path_fails_closed_without_mutating_index(self) -> None:
        self.write("target.txt", "target work\n")

        result, payload = self.run_helper("../escape.txt")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("invalid repository-relative exact path", payload["reason"])
        self.assertEqual(self.git("diff", "--cached", "--name-only").stdout, "")
        self.assertEqual(self.git("diff", "--name-only").stdout, "target.txt\n")

    def test_commit_hook_failure_returns_blocked_without_recovery(self) -> None:
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\necho intentional-hook-failure >&2\nexit 1\n")
        hook.chmod(0o755)
        self.write("target.txt", "target work\n")

        result, payload = self.run_helper("target.txt")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("intentional-hook-failure", payload["reason"])
        self.assertIn("no commit was created", payload["reason"])
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), self.initial_sha)
        self.assertEqual(self.git("diff", "--cached", "--name-only").stdout, "target.txt\n")

    def test_pre_commit_hook_mutation_blocks_with_created_sha(self) -> None:
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_text(
            "#!/bin/sh\nprintf 'staged by hook\\n' > unrelated.txt\n"
            "git add -- unrelated.txt\n"
        )
        hook.chmod(0o755)
        self.write("target.txt", "target work\n")

        result, payload = self.run_helper("target.txt")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("commit exists", payload["reason"])
        self.assertIn("unauthorized paths: unrelated.txt", payload["reason"])
        self.assertEqual(payload["sha"], self.git("rev-parse", "HEAD").stdout.strip())
        self.assertNotEqual(payload["sha"], self.initial_sha)
        committed = set(
            self.git(
                "diff-tree",
                "--root",
                "--no-commit-id",
                "--no-renames",
                "--name-only",
                "-r",
                "HEAD",
            ).stdout.splitlines()
        )
        self.assertEqual(committed, {"target.txt", "unrelated.txt"})
        self.assertEqual(
            self.git("rev-list", "--count", "HEAD").stdout.strip(),
            "2",
        )

    def test_commit_message_hook_trailer_is_accepted(self) -> None:
        hook = self.root / ".git/hooks/commit-msg"
        hook.write_text("#!/bin/sh\nprintf '\\nHook trailer\\n' >> \"$1\"\n")
        hook.chmod(0o755)
        self.write("target.txt", "target work\n")

        result, payload = self.run_helper("target.txt")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "committed")
        self.assertEqual(payload["sha"], self.git("rev-parse", "HEAD").stdout.strip())
        self.assertNotEqual(payload["sha"], self.initial_sha)
        self.assertIn("Hook trailer", self.git("log", "-1", "--pretty=%B").stdout)


if __name__ == "__main__":
    unittest.main()
