"""Structural entrypoint contracts; behavioral policy is reviewed, not phrase-pinned."""

from pathlib import Path
import re
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RoutingActivationContractTests(unittest.TestCase):
    def test_entrypoints_keep_names_and_invocation_metadata(self) -> None:
        for name, implicit in (
            ("orchestra-task", "false"),
            ("orchestra-repo-onboard", "false"),
            ("orchestra-project-start", "true"),
            ("orchestra-delegate", "true"),
        ):
            with self.subTest(skill=name):
                directory = ROOT / "codex/skills" / name
                text = (directory / "SKILL.md").read_text()
                frontmatter = text.split("---", 2)[1]
                self.assertRegex(frontmatter, rf"(?m)^name: {re.escape(name)}$")
                self.assertRegex(frontmatter, r"(?m)^description: .+")
                metadata = (directory / "agents/openai.yaml").read_text()
                self.assertRegex(metadata, rf"(?m)^\s+allow_implicit_invocation: {implicit}$")
                self.assertIn(f"${name}", metadata)

    def test_runtime_block_has_one_owned_boundary_and_canonical_pointer(self) -> None:
        runtime = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        for marker in ("<!-- orchestra:start -->", "<!-- orchestra:end -->"):
            self.assertEqual(runtime.count(marker), 1)
        self.assertIn("WORKFLOW.md", runtime)
        self.assertIn("$orchestra", runtime)


if __name__ == "__main__":
    unittest.main()
