"""Structural invariants for composable planned Orchestra work.

These tests pin machine-consumed structure: the four behavior-only profiles,
the capability-to-profile routing, the installed assignment matrices, the
closed playbook inventory, and the dual-matrix composition. Behavioral policy
lives only in `docs/WORKFLOW.md`; its wording is intentionally not frozen here.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
_SYNC_SPEC = importlib.util.spec_from_file_location(
    "orchestra_sync_planned", ROOT / "codex/scripts/sync.py"
)
assert _SYNC_SPEC is not None and _SYNC_SPEC.loader is not None
_sync = importlib.util.module_from_spec(_SYNC_SPEC)
_SYNC_SPEC.loader.exec_module(_sync)

PROFILE_NAMES = {
    "orchestra_analyst",
    "orchestra_implementation_worker",
    "orchestra_reviewer",
    "orchestra_verifier",
}
ROLE_SKILLS = {
    "orchestra_analyst": "orchestra-role-analyst",
    "orchestra_implementation_worker": "orchestra-role-implementer",
    "orchestra_reviewer": "orchestra-role-reviewer",
    "orchestra_verifier": "orchestra-role-verifier",
}
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
EXPECTED_TIERS = {
    "native": {"standard", "critical"},
    "external": {"luna", "standard", "critical"},
}
REASONING_EFFORTS = {"low", "medium", "high", "xhigh", "max"}


class PlannedFlowInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "codex/skills/orchestra/SKILL.md").read_text()
        self.role_matrices = {
            modelconfig: tomllib.loads(
                (ROOT / f"codex/config/roles.{modelconfig}.toml").read_text()
            )["tiers"]
            for modelconfig in ("native", "external")
        }
        self.dual_modes = tomllib.loads(
            _sync.compose_dual_matrix(
                (ROOT / "codex/config/roles.native.toml").read_text(),
                (ROOT / "codex/config/roles.external.toml").read_text(),
            )
        )["modes"]
        self.profiles = {
            path.stem: tomllib.loads(path.read_text())
            for path in (ROOT / "codex/agents").glob("*.toml")
        }
        self.references = ROOT / "codex/skills/orchestra/references"

    def role_skill(self, name: str) -> str:
        return (ROOT / f"codex/skills/{ROLE_SKILLS[name]}/SKILL.md").read_text()

    def test_exact_four_profiles_are_self_serve_stubs(self) -> None:
        self.assertEqual(set(self.profiles), PROFILE_NAMES)
        self.assertEqual(
            {profile["name"] for profile in self.profiles.values()}, PROFILE_NAMES
        )
        for name, profile in self.profiles.items():
            self.assertEqual(
                set(profile), {"name", "description", "developer_instructions"}
            )
            self.assertTrue(profile["description"].strip())
            stub = profile["developer_instructions"]
            self.assertIn(
                f".agents/skills/{ROLE_SKILLS[name]}/SKILL.md", stub, name
            )
            self.assertNotIn("gpt-5.", stub.lower())
            role = self.role_skill(name)
            for heading in ("## Input", "## Output", "## Stop conditions"):
                self.assertIn(heading, role, name)
            self.assertIn("shared_conduct.md", role, name)
            self.assertNotIn("gpt-5.", role.lower())

    def test_matrices_route_every_capability_through_the_four_profiles(self) -> None:
        for modelconfig, roles in self.role_matrices.items():
            self.assertEqual(set(roles), EXPECTED_TIERS[modelconfig])
            for tier, assignments in roles.items():
                self.assertEqual(
                    {name: value["profile"] for name, value in assignments.items()},
                    CAPABILITY_PROFILES,
                    f"{modelconfig}.{tier}",
                )
                for capability, assignment in assignments.items():
                    self.assertEqual(
                        set(assignment),
                        {"profile", "model", "reasoning_effort"},
                        f"{modelconfig}.{tier}.{capability}",
                    )
                    self.assertTrue(assignment["model"].strip())
                    self.assertIn(
                        assignment["reasoning_effort"], REASONING_EFFORTS
                    )
                    self.assertNotEqual(
                        (assignment["model"], assignment["reasoning_effort"]),
                        ("gpt-5.6-sol", "xhigh"),
                    )
                    self.assertNotIn(
                        assignment["profile"], {"root", "orchestrator"}
                    )

    def test_luna_tier_is_a_single_model_cost_lane(self) -> None:
        luna = self.role_matrices["external"]["luna"]
        self.assertEqual(
            {assignment["model"] for assignment in luna.values()},
            {"gpt-5.6-luna"},
        )

    def test_dual_matrix_preserves_source_assignments_with_v1_aliases(self) -> None:
        self.assertEqual(set(self.dual_modes), {"native", "external"})
        self.assertEqual(
            self.dual_modes["native"],
            {"tiers": self.role_matrices["native"]},
        )
        aliases = {
            "gpt-5.6-sol": "orchestra-v1/gpt-5.6-sol",
            "gpt-5.6-terra": "orchestra-v1/gpt-5.6-terra",
            "gpt-5.6-luna": "orchestra-v1/gpt-5.6-luna",
        }
        expected_external = {
            tier: {
                capability: {
                    **assignment,
                    "model": aliases.get(
                        assignment["model"],
                        assignment["model"],
                    ),
                }
                for capability, assignment in assignments.items()
            }
            for tier, assignments in self.role_matrices["external"].items()
        }
        self.assertEqual(
            self.dual_modes["external"],
            {"tiers": expected_external},
        )

    def test_playbook_inventory_is_closed_and_consumed(self) -> None:
        expected = {f"{name}.md" for name in PLAYBOOK_NAMES} | {
            "architecture_guidance.md",
            "shared_conduct.md",
            "host_codex.md",
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
        """No long verbatim passage may be duplicated across policy homes.

        WORKFLOW.md is the canonical home; the root skill, runtime overlay,
        and AGENTS.md reference it. Short shared phrases (activation gate,
        identifiers) are fine; a shared 25-word run means a rule was restated.
        """

        def ngrams(text: str, n: int = 25) -> set[str]:
            words = " ".join(text.lower().split()).split()
            return {
                " ".join(words[i : i + n]) for i in range(len(words) - n + 1)
            }

        sources = {
            "docs/WORKFLOW.md": (ROOT / "docs/WORKFLOW.md").read_text(),
            "codex/skills/orchestra/SKILL.md": self.skill,
            "codex/runtime/AGENTS.orchestra.md": (
                ROOT / "codex/runtime/AGENTS.orchestra.md"
            ).read_text(),
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
