from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "codex/scripts"))
from validate_suite import check_claude_host


class ClaudeHostTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        shutil.copytree(ROOT / "hosts/claude", self.root / "hosts/claude")
        self.roles = self.root / "hosts/claude/config/roles.claude.toml"
        self.agents = self.root / "hosts/claude/agents"

    def test_source_adapter_is_dispatchable(self) -> None:
        self.assertEqual(check_claude_host(ROOT), [])

    def test_row_without_registered_effort_agent_fails(self) -> None:
        text = self.roles.read_text(encoding="utf-8")
        self.roles.write_text(
            text.replace(
                'subagent_type = "orchestra_verifier_medium"\nmodel = "claude-sonnet-5-5"\neffort = "medium"',
                'subagent_type = "orchestra_verifier_xhigh"\nmodel = "claude-sonnet-5-5"\neffort = "xhigh"',
                1,
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("agents/" in failure for failure in check_claude_host(self.root)))

    def test_agent_that_pins_a_model_fails(self) -> None:
        agent = self.agents / "orchestra_reviewer_high.md"
        agent.write_text(
            agent.read_text(encoding="utf-8").replace("effort: high\n", "effort: high\nmodel: haiku\n"),
            encoding="utf-8",
        )
        self.assertTrue(any("orchestra_reviewer_high" in failure for failure in check_claude_host(self.root)))

    def test_model_without_agent_alias_fails(self) -> None:
        text = self.roles.read_text(encoding="utf-8")
        self.roles.write_text(text.replace("claude-opus-5-5", "claude-unknown-9", 1), encoding="utf-8")
        self.assertTrue(any("no Agent alias" in failure for failure in check_claude_host(self.root)))


class PackageReadHookTests(unittest.TestCase):
    def decide(self, root: Path, target: object) -> str:
        result = subprocess.run(
            [sys.executable, str(ROOT / "hosts/claude/plugin/hooks/read_package.py")],
            input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": target}}),
            env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(root)},
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] if result.stdout else "none"

    def test_only_package_paths_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            package = base / "orchestra"
            (package / "skills").mkdir(parents=True)
            (package / "skills/escape").symlink_to(base)
            self.assertEqual(self.decide(package, str(package / "skills/role/SKILL.md")), "allow")
            for target in (str(base / "secret.txt"), str(package / "../secret.txt"),
                           str(package / "skills/escape/secret.txt"), "skills/role/SKILL.md", None):
                with self.subTest(target=target):
                    self.assertEqual(self.decide(package, target), "none")


if __name__ == "__main__":
    unittest.main()
