from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "codex/scripts/prepare_source.py"


class PrepareSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.repository = self.root / "repository"
        self.repository.mkdir()
        self.git("init", "--quiet")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        for relative in (
            "docs/WORKFLOW.md", "codex/skills/orchestra/SKILL.md",
            "codex/skills/orchestra/runtime.md", "codex/scripts/delegate.py",
        ):
            path = self.repository / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "initial fixture")
        self.revision = self.git("rev-parse", "HEAD")
        self.destination = self.root / "prepared with spaces" / "orchestra"

    def git(self, *arguments: str, root: Path | None = None) -> str:
        return subprocess.run(
            ["git", "-C", str(root or self.repository), *arguments],
            text=True, capture_output=True, check=True,
        ).stdout.strip()

    def prepare(self, revision: str | None = None, destination: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--repository", str(self.repository),
             "--revision", revision or self.revision, "--destination", str(destination or self.destination)],
            cwd=self.root, text=True, capture_output=True, check=False,
        )

    def test_pins_older_revision_and_reuses_it_without_network(self) -> None:
        (self.repository / "docs/WORKFLOW.md").write_text("new policy\n")
        self.git("commit", "--quiet", "-am", "change fixture")
        result = self.prepare()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        roots = json.loads(result.stdout)
        self.assertEqual(roots["revision"], self.revision)
        self.assertEqual(Path(roots["workflow"]).read_text(), "fixture\n")
        self.assertEqual(Path(roots["skills_root"]), self.destination / "codex/skills")
        self.assertEqual(Path(roots["runtime_root"]), self.destination / "codex")
        self.assertEqual(self.git("rev-parse", "HEAD", root=self.destination), self.revision)
        self.assertEqual(self.git("status", "--porcelain", root=self.destination), "")
        self.repository.rename(self.root / "unavailable")
        repeated = self.prepare()
        self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
        self.assertEqual(json.loads(repeated.stdout), roots)

    def test_existing_changes_and_untracked_files_are_preserved(self) -> None:
        for relative in ("docs/WORKFLOW.md", "private-notes.txt"):
            with self.subTest(path=relative):
                destination = self.root / relative.replace("/", "-")
                self.assertEqual(self.prepare(destination=destination).returncode, 0)
                changed = destination / relative
                changed.write_text("unique work\n")
                result = self.prepare(destination=destination)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("local changes", result.stdout)
                self.assertEqual(changed.read_text(), "unique work\n")

    def test_wrong_revision_is_not_reset(self) -> None:
        self.assertEqual(self.prepare().returncode, 0)
        (self.repository / "docs/WORKFLOW.md").write_text("new policy\n")
        self.git("commit", "--quiet", "-am", "change fixture")
        result = self.prepare(revision=self.git("rev-parse", "HEAD"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different revision", result.stdout)
        self.assertEqual(self.git("rev-parse", "HEAD", root=self.destination), self.revision)

    def test_existing_non_checkout_and_symlink_are_preserved(self) -> None:
        self.destination.mkdir(parents=True)
        note = self.destination / "notes"
        note.write_text("keep\n")
        self.assertNotEqual(self.prepare().returncode, 0)
        self.assertEqual(note.read_text(), "keep\n")
        link = self.root / "source-link"
        link.symlink_to(self.repository, target_is_directory=True)
        result = self.prepare(destination=link)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(link.is_symlink())

    def test_failed_fetch_and_invalid_runtime_leave_no_destination(self) -> None:
        result = self.prepare(revision="0" * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.destination.parent.iterdir()), [])
        self.git("rm", "--quiet", "docs/WORKFLOW.md")
        self.git("commit", "--quiet", "-m", "remove required resource")
        result = self.prepare(revision=self.git("rev-parse", "HEAD"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Orchestra resource", result.stdout)
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.destination.parent.iterdir()), [])

    def test_moving_ref_is_rejected_before_creating_destination(self) -> None:
        result = self.prepare(revision="main")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("full 40-character", result.stdout)
        self.assertFalse(self.destination.parent.exists())


if __name__ == "__main__":
    unittest.main()
