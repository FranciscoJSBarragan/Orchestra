from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "codex/scripts"))
from update_local import promote


class PromoteTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def build(self, name: str, version: str) -> None:
        (self.root / name).mkdir()
        (self.root / name / "version").write_text(version)

    def version(self, name: str) -> str:
        return (self.root / name / "version").read_text()

    def test_first_build_becomes_current_without_previous(self) -> None:
        self.build("next", "1")
        promote(self.root)
        self.assertEqual(self.version("current"), "1")
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["current"])

    def test_new_build_moves_current_to_previous_and_drops_the_older_one(self) -> None:
        self.build("previous", "1")
        self.build("current", "2")
        self.build("next", "3")
        promote(self.root)
        self.assertEqual(self.version("current"), "3")
        self.assertEqual(self.version("previous"), "2")
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), ["current", "previous"])


if __name__ == "__main__":
    unittest.main()
