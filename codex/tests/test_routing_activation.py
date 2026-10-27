"""Structural entrypoint contracts; behavioral policy is reviewed, not phrase-pinned."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RoutingActivationContractTests(unittest.TestCase):
    def test_entrypoints_keep_names_and_invocation_metadata(self) -> None:
        for name, implicit in (
            ("orchestra-repo-readiness", "false"),
            ("orchestra-project-start", "true"),
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


if __name__ == "__main__":
    unittest.main()
