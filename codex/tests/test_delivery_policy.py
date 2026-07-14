"""Tests for explicit delivery policy and ordered argv checks."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "codex/scripts/policy.py"


class DeliveryPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.repo = Path(self.temporary_directory.name)

    def run_policy(self, action: str = "show") -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [sys.executable, str(HELPER), "--repo", str(self.repo), action],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )
        return result, json.loads(result.stdout)

    def write_policy(self, mode: str, checks: str) -> None:
        (self.repo / "orchestra.toml").write_text(
            f'[delivery]\nmode = "{mode}"\n\n{checks}', encoding="utf-8"
        )

    def test_missing_policy_asks_once_and_recommends_hybrid(self) -> None:
        result, payload = self.run_policy()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["action"], "ask_user_once")
        self.assertEqual(payload["recommendation"], "hybrid")

    def test_hybrid_policy_and_argv_check_are_valid(self) -> None:
        self.write_policy(
            "hybrid",
            '[[checks]]\nname = "unit"\ncommand = ["python3", "-c", "pass"]\n',
        )

        result, payload = self.run_policy()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(payload, {"status": "ok", "mode": "hybrid", "checks": ["unit"]})

    def test_invalid_mode_fails_closed(self) -> None:
        self.write_policy(
            "automatic",
            '[[checks]]\nname = "unit"\ncommand = []\n',
        )

        result, payload = self.run_policy()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("delivery mode", payload["reason"])

    def test_empty_argv_check_fails_closed(self) -> None:
        self.write_policy(
            "hybrid",
            '[[checks]]\nname = "unit"\ncommand = []\n',
        )

        result, payload = self.run_policy()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("nonempty argv", payload["reason"])

    def test_checks_run_in_order_without_shell_strings(self) -> None:
        marker = self.repo / "order.txt"
        command = (
            f'[[checks]]\nname = "first"\ncommand = [{json.dumps(sys.executable)}, '
            f'"-c", "from pathlib import Path; Path({str(marker)!r}).write_text(\'1\')"]\n\n'
            f'[[checks]]\nname = "second"\ncommand = [{json.dumps(sys.executable)}, '
            f'"-c", "from pathlib import Path; p=Path({str(marker)!r}); p.write_text(p.read_text()+\'2\')"]\n'
        )
        self.write_policy("hybrid", command)

        result, payload = self.run_policy("run-checks")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload, {"status": "ok", "checks": ["first", "second"]})
        self.assertEqual(marker.read_text(encoding="utf-8"), "12")

    def test_failed_check_stops_later_checks(self) -> None:
        marker = self.repo / "must-not-exist"
        command = (
            f'[[checks]]\nname = "fail"\ncommand = [{json.dumps(sys.executable)}, '
            '"-c", "raise SystemExit(3)"]\n\n'
            f'[[checks]]\nname = "later"\ncommand = [{json.dumps(sys.executable)}, '
            f'"-c", "from pathlib import Path; Path({str(marker)!r}).touch()"]\n'
        )
        self.write_policy("hybrid", command)

        result, payload = self.run_policy("run-checks")

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["check"], "fail")
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
