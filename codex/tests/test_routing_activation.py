"""Structural entrypoint contracts; behavioral policy is reviewed, not phrase-pinned."""

import importlib.util
from pathlib import Path
import re
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("orchestra_sync_routing", ROOT / "codex/scripts/sync.py")
assert _SPEC is not None and _SPEC.loader is not None
_sync = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_sync)


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

    def test_native_and_external_expose_only_their_approved_tiers(self) -> None:
        source_roles = {
            modelconfig: tomllib.loads(
                (ROOT / f"codex/config/roles.{modelconfig}.toml").read_text()
            )
            for modelconfig in ("native", "external")
        }
        self.assertEqual(
            set(source_roles["native"]["tiers"]),
            {"standard", "critical"},
        )
        self.assertEqual(
            set(source_roles["external"]["tiers"]),
            {"luna", "standard", "critical"},
        )
        for roles in source_roles.values():
            self.assertEqual(set(roles), {"tiers"})
            for assignments in roles["tiers"].values():
                self.assertEqual(len(assignments), 10)
        dual = tomllib.loads(
            _sync.compose_dual_matrix(
                (ROOT / "codex/config/roles.native.toml").read_text(),
                (ROOT / "codex/config/roles.external.toml").read_text(),
            )
        )
        self.assertEqual(set(dual), {"modes"})
        self.assertEqual(set(dual["modes"]), {"native", "external"})
        self.assertEqual(
            set(dual["modes"]["native"]["tiers"]), {"standard", "critical"}
        )
        self.assertEqual(
            set(dual["modes"]["external"]["tiers"]),
            {"luna", "standard", "critical"},
        )
        for mode in dual["modes"].values():
            self.assertEqual(set(mode), {"tiers"})
            for assignments in mode["tiers"].values():
                self.assertEqual(len(assignments), 10)


if __name__ == "__main__":
    unittest.main()
