"""Static contracts for explicit Orchestra activation."""

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]


class RoutingActivationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "codex/skills/orchestra/SKILL.md").read_text()
        self.workflow = (ROOT / "docs/WORKFLOW.md").read_text()
        self.agents = (ROOT / "AGENTS.md").read_text()
        self.runtime = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()

    def test_native_plan_mode_and_orchestra_are_mutually_exclusive(self) -> None:
        for text in (self.skill, self.workflow, self.agents, self.runtime):
            self.assertIn("Plan Mode", text)
            self.assertIn("mutually exclusive", text)
        self.assertIn("even for an explicit `$orchestra` request", self.skill)
        self.assertIn("tell the user to leave Plan Mode", self.skill)

    def test_direct_implementation_stays_outside_orchestra(self) -> None:
        for text in (self.skill, self.workflow, self.runtime):
            self.assertIn("direct", text.lower())
            self.assertIn("outside Orchestra", text)
        self.assertIn("implementation of a prior native Codex plan", self.skill)

    def test_explicit_planning_intent_starts_specification_gate(self) -> None:
        for phrase in ("create", "prepare", "write"):
            self.assertIn(phrase, self.skill)
        for field in (
            "Objective",
            "User-visible behavior",
            "Constraints",
            "Acceptance",
            "Exclusions",
            "Decisions",
            "Open questions",
        ):
            self.assertIn(field, self.skill)
        self.assertIn("ask only genuine gaps", self.skill)

    def test_only_standard_and_critical_assignments_exist(self) -> None:
        for modelconfig in ("native", "external"):
            roles = tomllib.loads(
                (
                    ROOT / f"codex/config/roles.{modelconfig}.toml"
                ).read_text()
            )
            self.assertEqual(set(roles), {"tiers"})
            self.assertEqual(set(roles["tiers"]), {"standard", "critical"})
            self.assertEqual(len(roles["tiers"]["standard"]), 10)
            self.assertEqual(len(roles["tiers"]["critical"]), 10)
        self.assertNotIn("Tier: light", self.skill)

    def test_plan_is_first_persisted_as_active(self) -> None:
        for text in (self.skill, self.workflow, self.runtime):
            self.assertIn("directly as `active`", text)
            self.assertNotIn("`draft`", text)
        self.assertIn("system temporary storage", self.skill)
        self.assertNotIn(".orchestra/", (ROOT / ".gitignore").read_text())


if __name__ == "__main__":
    unittest.main()
