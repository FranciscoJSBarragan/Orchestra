"""Static contracts for the proportional Orchestra light workflow."""

from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LightFlowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "codex/skills/orchestra/SKILL.md").read_text()
        self.workflow = (ROOT / "docs/WORKFLOW.md").read_text()
        self.agents = (ROOT / "AGENTS.md").read_text()
        self.commit_skill = (
            ROOT / "codex/skills/orchestra-phase-commit/SKILL.md"
        ).read_text()

    def test_old_frontend_blanket_tier_rule_is_removed(self) -> None:
        for text in (self.skill, self.workflow, self.agents):
            self.assertNotIn(
                "Frontend implementation or named browser acceptance", text
            )

    def test_old_light_three_dispatch_sentence_is_removed(self) -> None:
        self.assertNotIn(
            "Light has assignments only for `general_implementation`, "
            "`independent_review`, and `runtime_verification`",
            self.skill,
        )

    def test_light_tiering_fails_closed_and_declares_reason(self) -> None:
        self.assertIn("Tier: light|standard|critical — reason", self.skill)
        self.assertIn("Fail closed to `standard` on ambiguity", self.skill)
        self.assertIn("Select `critical` for security-sensitive work", self.skill)
        self.assertIn("Named browser acceptance makes a task at least standard", self.skill)
        self.assertIn("A frontend change may be light only when", self.skill)
        frontend = (
            ROOT / "codex/skills/orchestra/references/frontend_implementation.md"
        ).read_text()
        self.assertIn(
            "including one direct targeted verification",
            frontend,
        )

    def test_root_owns_judgment_and_packet_stays_in_memory(self) -> None:
        for responsibility in (
            "problem framing",
            "tier selection",
            "user alignment",
            "capability routing",
            "compact synthesis",
            "blocker resolution",
            "final technical judgment",
        ):
            self.assertIn(responsibility, self.skill)
        self.assertIn("compact in-memory packet", self.skill)
        for field in (
            "explicit capability",
            "objective",
            "known decisions and context delta",
            "allowed paths or interactions",
            "acceptance",
            "verification",
            "exclusions",
            "stop conditions",
            "relevant references and revision",
        ):
            self.assertIn(field, self.skill)

    def test_review_and_verification_are_independent_and_fixes_return(self) -> None:
        reviewer = (ROOT / "codex/agents/reviewer.toml").read_text()
        verifier = (ROOT / "codex/agents/verifier.toml").read_text()
        self.assertIn("one read-only `reviewer`", self.skill)
        self.assertIn("The root itself runs the single direct targeted verification", self.skill)
        self.assertIn("Light has no `verifier` dispatch", self.skill)
        self.assertIn("same implementation owner", self.skill)
        self.assertIn("Remain read-only and report-only", reviewer)
        self.assertIn("Accepted findings return to the same implementation owner", reviewer)
        self.assertIn("Remain read-only with respect to repository source", verifier)

    def test_all_four_profiles_are_behavior_only_contracts(self) -> None:
        profile_paths = sorted((ROOT / "codex/agents").glob("*.toml"))
        self.assertEqual(
            {path.stem for path in profile_paths},
            {"analyst", "implementation_worker", "reviewer", "verifier"},
        )
        for path in profile_paths:
            profile = tomllib.loads(path.read_text())
            self.assertEqual(
                set(profile), {"name", "description", "developer_instructions"}
            )
            self.assertNotIn("gpt-5.", profile["developer_instructions"].lower())
            self.assertIn("## Input", profile["developer_instructions"])
            self.assertIn("## Output", profile["developer_instructions"])
            self.assertIn("## Stop conditions", profile["developer_instructions"])

    def test_light_matrix_is_exactly_two_terra_max_capabilities(self) -> None:
        roles = tomllib.loads((ROOT / "codex/config/roles.toml").read_text())
        self.assertEqual(set(roles), {"tiers"})
        self.assertEqual(set(roles["tiers"]), {"light", "standard", "critical"})
        self.assertEqual(
            roles["tiers"]["light"],
            {
                "general_implementation": {
                    "profile": "implementation_worker",
                    "model": "gpt-5.6-terra",
                    "reasoning_effort": "max",
                },
                "independent_review": {
                    "profile": "reviewer",
                    "model": "gpt-5.6-terra",
                    "reasoning_effort": "max",
                },
            },
        )
        self.assertIn("only machine-readable assignment matrix", self.skill)
        self.assertIn("explicit model and reasoning overrides", self.skill)
        self.assertIn("root has no assignment", self.skill)

    def test_commit_path_is_direct_and_rejects_parallel_git_machinery(self) -> None:
        helper = (ROOT / "codex/scripts/commit_phase.py").read_text()
        self.assertIn('"commit",', helper)
        self.assertIn('"-F",', helper)
        for rejected in (
            "GIT_INDEX_FILE",
            "recovery journal",
            "reflog ownership",
            "workflow state",
            "transaction layer",
            "threading.Lock",
        ):
            self.assertNotIn(rejected, helper)
        self.assertIn("alternate index", self.commit_skill)
        self.assertIn("Git is the commit truth", self.commit_skill)
        self.assertIn("root directly run", self.commit_skill)
        self.assertIn("Do not resolve an assignment", self.commit_skill)

    def test_runtime_managed_block_routes_without_installing(self) -> None:
        runtime = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        self.assertEqual(runtime.count("<!-- orchestra:start -->"), 1)
        self.assertEqual(runtime.count("<!-- orchestra:end -->"), 1)
        self.assertIn("$orchestra", runtime)
        self.assertIn("${CODEX_HOME:-$HOME/.codex}/orchestra/roles.toml", runtime)
        self.assertIn("${CODEX_HOME:-$HOME/.codex}/agents/", runtime)
        self.assertIn("Read explicit repository policy", runtime)
        self.assertIn("never merge", runtime)
        self.assertIn("install or synchronize", runtime)

if __name__ == "__main__":
    unittest.main()
