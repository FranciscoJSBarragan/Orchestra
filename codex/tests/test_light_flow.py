"""Static contract tests for the Orchestra light workflow."""

from __future__ import annotations

from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]


class LightFlowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "codex/skills/orchestra/SKILL.md").read_text()
        self.commit_skill = (
            ROOT / "codex/skills/orchestra-phase-commit/SKILL.md"
        ).read_text()

    def test_light_tiering_fails_closed_and_declares_reason(self) -> None:
        self.assertIn("Tier: light|standard|critical — reason", self.skill)
        self.assertIn("Fail closed to `standard` on any ambiguity", self.skill)
        self.assertIn("Select `critical` for security-sensitive work", self.skill)

    def test_root_owns_judgment_and_packet_stays_in_memory(self) -> None:
        for responsibility in (
            "problem framing",
            "tier selection",
            "user alignment",
            "routing",
            "compact synthesis",
            "blocker resolution",
            "final technical judgment",
        ):
            self.assertIn(responsibility, self.skill)
        self.assertIn("Keep one compact packet in memory", self.skill)
        for field in (
            "objective",
            "known decisions and context",
            "allowed paths",
            "acceptance",
            "verification",
            "exclusions",
            "stop conditions",
            "references and revision",
        ):
            self.assertIn(field, self.skill)

    def test_review_is_independent_read_only_and_fixes_return_to_owner(self) -> None:
        reviewer = (ROOT / "codex/agents/reviewer.toml").read_text()
        self.assertIn("one independent `reviewer`", self.skill)
        self.assertIn("Do not ask the reviewer to edit", self.skill)
        self.assertIn("same implementation owner", self.skill)
        self.assertIn("Remain read-only: do not edit files", reviewer)
        self.assertIn("accepted findings return to the same implementation owner", reviewer)

    def test_light_profiles_remain_behavior_only_contracts(self) -> None:
        profile_paths = [
            ROOT / "codex/agents/implementation_worker.toml",
            ROOT / "codex/agents/reviewer.toml",
            ROOT / "codex/agents/phase_committer.toml",
        ]
        self.assertTrue(all(path.is_file() for path in profile_paths))
        for path in profile_paths:
            profile = tomllib.loads(path.read_text())
            self.assertEqual(
                set(profile), {"name", "description", "developer_instructions"}
            )
            self.assertNotIn("model", profile["developer_instructions"].lower())
            self.assertIn("## Input", profile["developer_instructions"])
            self.assertIn("## Output", profile["developer_instructions"])
            self.assertIn("## Stop conditions", profile["developer_instructions"])

    def test_role_matrix_is_unique_and_light_uses_luna_max(self) -> None:
        roles = tomllib.loads((ROOT / "codex/config/roles.toml").read_text())
        self.assertEqual(set(roles), {"tiers"})
        self.assertEqual(set(roles["tiers"]), {"light", "standard", "critical"})
        self.assertEqual(
            roles["tiers"]["light"],
            {
                "implementation_worker": {
                    "model": "gpt-5.6-luna",
                    "reasoning_effort": "max",
                },
                "reviewer": {
                    "model": "gpt-5.6-luna",
                    "reasoning_effort": "max",
                },
                "phase_committer": {
                    "model": "gpt-5.6-luna",
                    "reasoning_effort": "max",
                },
            },
        )
        self.assertIn("only machine-readable model and reasoning matrix", self.skill)
        self.assertIn(
            "pass its `model` and `reasoning_effort` as explicit overrides", self.skill
        )
        self.assertIn("`phase_committer`", self.skill)

    def test_commit_path_rejects_parallel_git_machinery(self) -> None:
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

    def test_runtime_managed_block_routes_without_installing(self) -> None:
        runtime = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        self.assertEqual(runtime.count("<!-- orchestra:start -->"), 1)
        self.assertEqual(runtime.count("<!-- orchestra:end -->"), 1)
        self.assertIn("codex/skills/orchestra/SKILL.md", runtime)
        self.assertIn("codex/config/roles.toml", runtime)
        self.assertIn("Do not take delivery actions", runtime)
        self.assertIn("install or synchronize", runtime)


if __name__ == "__main__":
    unittest.main()
