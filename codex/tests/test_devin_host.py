from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
ROLES = ROOT / "hosts/devin/config/roles.devin.toml"
SPAWN = ROOT / "hosts/devin/references/spawn.md"
AGENTS = ROOT / "hosts/devin/agents"
PLUGIN = ROOT / "hosts/devin/plugin"

PROFILES = (
    "orchestra_analyst",
    "orchestra_implementation_worker",
    "orchestra_reviewer",
    "orchestra_verifier",
)
CAPABILITIES = (
    "repository_context",
    "web_research",
    "runtime_verification",
    "browser_acceptance",
    "general_implementation",
    "frontend_implementation",
    "technical_planning",
    "architecture_analysis",
    "difficult_debugging",
    "independent_review",
)


class DevinHostTests(unittest.TestCase):

    def test_matrix_assigns_standard_and_critical_only(self) -> None:
        roles = tomllib.loads(ROLES.read_text(encoding="utf-8"))
        self.assertEqual(set(roles["tiers"]), {"standard", "critical"})
        self.assertNotIn("minimal", roles["tiers"])
        for tier in ("standard", "critical"):
            self.assertEqual(set(roles["tiers"][tier]), set(CAPABILITIES))
            for capability, assignment in roles["tiers"][tier].items():
                self.assertIn(assignment["profile"], PROFILES, capability)
                self.assertEqual(assignment["subagent_type"], assignment["profile"])
                self.assertEqual(assignment["model"], "swe-2-max")
                self.assertEqual(assignment["effort"], "inherit")

    def test_spawn_adapter_names_devin_primitives_and_blocks_browser(self) -> None:
        spawn = SPAWN.read_text(encoding="utf-8")
        for required in (
            "run_subagent",
            "read_subagent",
            "swe-2-max",
            "`in_app` is `blocked`",
            "`chrome` is `blocked`",
        ):
            self.assertIn(required, spawn)
        self.assertIn("`auto` is `blocked`", spawn)
        self.assertIn("orchestra:<subagent_type>", spawn)
        self.assertIn("orchestra:orchestra_analyst", spawn)
        self.assertIn(".devin-plugin/plugin.json", spawn)
        self.assertIn("/orchestra:orchestra", spawn)

    def test_agent_profiles_exist_with_pinned_model(self) -> None:
        for profile in PROFILES:
            path = AGENTS / f"{profile}.md"
            self.assertTrue(path.is_file(), profile)
            text = path.read_text(encoding="utf-8")
            self.assertIn(f"name: {profile}", text)
            self.assertIn("model: swe-2-max", text)





if __name__ == "__main__":
    unittest.main()
