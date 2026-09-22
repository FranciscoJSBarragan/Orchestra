"""Prove that the initiative canary discriminates local and joint acceptance."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


FIXTURE = Path(__file__).parent / "fixtures/modular_engineering/make_fixture.py"
spec = importlib.util.spec_from_file_location("modular_fixture", FIXTURE)
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


class ModularFixtureTests(unittest.TestCase):
    def test_green_children_are_insufficient_and_evidence_tracks_repaired_revision(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = fixture.create_fixture(Path(temporary) / "initiative")
            for name in ("service", "client"):
                subprocess.run([sys.executable, "check.py"], cwd=root / name, check=True)
            command = [sys.executable, "verify_integration.py"]
            before = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(before.returncode, 1)
            self.assertIn("FAIL: real response", before.stdout)
            service_sha = fixture.git(root / "service", "rev-parse", "HEAD")
            client = root / "client"
            for name in ("client.py", "check.py"):
                path = client / name
                path.write_text(path.read_text().replace('"label"', '"display_name"'))
            dirty = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(dirty.returncode, 0)
            self.assertIn("uncommitted changes", dirty.stderr)
            fixture.git(client, "add", "--", "client.py", "check.py")
            fixture.git(client, "commit", "-q", "-m", "fix: consume shared contract")
            subprocess.run([sys.executable, "check.py"], cwd=client, check=True)
            after = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(after.returncode, 0, after.stdout + after.stderr)
            self.assertIn(service_sha, after.stdout)
            self.assertIn(fixture.git(client, "rev-parse", "HEAD"), after.stdout)
            self.assertIn("PASS: real service", after.stdout)


if __name__ == "__main__":
    unittest.main()
