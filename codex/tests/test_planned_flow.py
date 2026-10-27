from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
ROLE_SKILLS = (
    "orchestra-role-analyst",
    "orchestra-role-implementer",
    "orchestra-role-reviewer",
    "orchestra-role-verifier",
)
PLAYBOOK_NAMES = {
    "repository_context",
    "web_research",
    "technical_planning",
    "difficult_debugging",
    "frontend_implementation",
    "browser_acceptance",
    "runtime_verification",
}
CAPABILITY_PROFILES = {
    "repository_context": "orchestra_analyst",
    "web_research": "orchestra_analyst",
    "technical_planning": "orchestra_analyst",
    "architecture_analysis": "orchestra_analyst",
    "difficult_debugging": "orchestra_analyst",
    "general_implementation": "orchestra_implementation_worker",
    "frontend_implementation": "orchestra_implementation_worker",
    "independent_review": "orchestra_reviewer",
    "browser_acceptance": "orchestra_verifier",
    "runtime_verification": "orchestra_verifier",
}
REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max"}


class PlannedFlowInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "codex/skills/orchestra/SKILL.md").read_text()
        self.flow = tomllib.loads((ROOT / "codex/config/flow.toml").read_text())
        self.references = ROOT / "codex/skills/orchestra/references"

    def test_four_role_skills_are_complete_and_model_free(self) -> None:
        for name in ROLE_SKILLS:
            role = (ROOT / f"codex/skills/{name}/SKILL.md").read_text()
            for heading in ("## Input", "## Output", "## Stop conditions"):
                self.assertIn(heading, role, name)
            self.assertIn("shared_conduct.md", role, name)
            self.assertNotRegex(role, r"\b(?:gpt|claude|grok)-\d")

    def test_flow_assigns_every_capability_a_provider_and_model(self) -> None:
        self.assertEqual(set(self.flow["capabilities"]), set(CAPABILITY_PROFILES))
        entries = [*self.flow["capabilities"].values(), self.flow["review_pair"], *self.flow["escalation"]]
        for entry in entries:
            self.assertTrue(entry["provider"].strip())
            self.assertTrue(entry["model"].strip())
            self.assertIn(entry.get("effort", "high"), REASONING_EFFORTS)

    def test_playbook_inventory_is_closed_and_consumed(self) -> None:
        expected = {f"{name}.md" for name in PLAYBOOK_NAMES} | {
            "architecture_guidance.md",
            "shared_conduct.md",
            "source_preparation.md",
            "host_t3.md",
            "model_notes.md",
            "finding_triage.md",
            "planning_stage.md",
        }
        self.assertEqual({path.name for path in self.references.iterdir()}, expected)
        for name in PLAYBOOK_NAMES:
            self.assertIn(f"references/{name}.md", self.skill)
        for absent in (
            "general_implementation.md",
            "independent_review.md",
            "architecture_analysis.md",
        ):
            self.assertNotIn(absent, self.skill)

    def test_routing_skill_consumes_every_matrix_capability(self) -> None:
        for capability in CAPABILITY_PROFILES:
            self.assertIn(f"`{capability}`", self.skill)

    def test_normative_text_has_exactly_one_home(self) -> None:
        def ngrams(text: str, n: int = 25) -> set[str]:
            words = " ".join(text.lower().split()).split()
            return {
                " ".join(words[i : i + n]) for i in range(len(words) - n + 1)
            }

        sources = {
            "docs/WORKFLOW.md": (ROOT / "docs/WORKFLOW.md").read_text(),
            "codex/skills/orchestra/SKILL.md": self.skill,
            "AGENTS.md": (ROOT / "AGENTS.md").read_text(),
        }
        names = list(sources)
        grams = {name: ngrams(text) for name, text in sources.items()}
        for index, first in enumerate(names):
            for second in names[index + 1 :]:
                shared = grams[first] & grams[second]
                self.assertEqual(
                    shared,
                    set(),
                    f"duplicated normative passage between {first} and "
                    f"{second}: {sorted(shared)[:3]}",
                )

    def test_visible_primary_skill_identity_is_orchestra(self) -> None:
        lines = self.skill.splitlines()
        self.assertEqual(lines[0], "---")
        end = lines.index("---", 1)
        frontmatter = "\n".join(lines[1:end])
        self.assertIn("name: orchestra", frontmatter)
        metadata = (
            ROOT / "codex/skills/orchestra/agents/openai.yaml"
        ).read_text()
        self.assertIn("$orchestra", metadata)


if __name__ == "__main__":
    unittest.main()
