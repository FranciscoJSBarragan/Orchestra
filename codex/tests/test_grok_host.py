from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
ROLES = ROOT / "hosts/grok/config/roles.grok.toml"
SPAWN = ROOT / "hosts/grok/references/spawn.md"


class GrokHostTests(unittest.TestCase):
    def test_matrix_assigns_minimal_and_standard_only(self) -> None:
        roles = tomllib.loads(ROLES.read_text(encoding="utf-8"))
        self.assertEqual(set(roles["tiers"]), {"minimal", "standard"})
        self.assertNotIn("critical", roles["tiers"])
        for tier, model in (("minimal", "grok-4.5"), ("standard", "grok-4.6")):
            for assignment in roles["tiers"][tier].values():
                self.assertEqual(assignment["subagent_type"], "general-purpose")
                self.assertEqual(assignment["model"], model)
                self.assertEqual(assignment["effort"], "inherit")

    def test_spawn_adapter_names_grok_primitives_and_forbids_host_worktrees(self) -> None:
        spawn = SPAWN.read_text(encoding="utf-8")
        for required in (
            "spawn_subagent",
            "get_command_or_subagent_output",
            "isolation: none",
            "GROK_SESSION_ID",
            "Playwright",
        ):
            self.assertIn(required, spawn)
        self.assertIn("Never pass `isolation: worktree`", spawn)
        self.assertIn("`general-purpose`", spawn)
        self.assertIn("unofficial Claude-compat worker types", spawn)


if __name__ == "__main__":
    unittest.main()
