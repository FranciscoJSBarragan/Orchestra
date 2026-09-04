"""Static contracts for explicit Orchestra activation."""

import importlib.util
from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
_SYNC_SPEC = importlib.util.spec_from_file_location(
    "orchestra_sync_routing", ROOT / "codex/scripts/sync.py"
)
assert _SYNC_SPEC is not None and _SYNC_SPEC.loader is not None
_sync = importlib.util.module_from_spec(_SYNC_SPEC)
_SYNC_SPEC.loader.exec_module(_sync)
CANONICAL = (
    ROOT / "README.md",
    ROOT / "VISION.md",
    ROOT / "AGENTS.md",
    ROOT / "docs/WORKFLOW.md",
    ROOT / "docs/ARCHITECTURE.md",
    ROOT / "codex/skills/orchestra/SKILL.md",
    ROOT / "codex/runtime/AGENTS.orchestra.md",
)


class RoutingActivationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "codex/skills/orchestra/SKILL.md").read_text()
        self.task_skill = (ROOT / "codex/skills/orchestra-task/SKILL.md").read_text()
        self.task_metadata = (
            ROOT / "codex/skills/orchestra-task/agents/openai.yaml"
        ).read_text()
        self.workflow = (ROOT / "docs/WORKFLOW.md").read_text()
        self.agents = (ROOT / "AGENTS.md").read_text()
        self.runtime = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        self.canonical = {
            path.name: path.read_text(encoding="utf-8") for path in CANONICAL
        }

    @staticmethod
    def _flat(text: str) -> str:
        return " ".join(text.split())

    def test_activation_requires_explicit_orchestra_invocation(self) -> None:
        for text in (self.skill, self.workflow, self.agents, self.runtime):
            self.assertIn("$orchestra", text)
            self.assertIn("use or start Orchestra", self._flat(text))
        self.assertIn(
            "Ordinary requests to create a plan, descriptive mentions of Orchestra",
            self._flat(self.skill),
        )
        self.assertNotIn(
            "asks to create, prepare, or write the implementation plan",
            self.skill,
        )
        self.assertNotIn(
            "asks to create, prepare, or write the implementation plan",
            self.runtime,
        )

    def test_skill_frontmatter_activates_only_for_explicit_orchestra(self) -> None:
        lines = self.skill.splitlines()
        self.assertEqual(lines[0], "---")
        end = lines.index("---", 1)
        frontmatter = "\n".join(lines[1:end])
        self.assertIn("name: orchestra", frontmatter)
        description_line = next(
            line for line in lines[1:end] if line.startswith("description:")
        )
        description = description_line.split(":", 1)[1].strip()
        flat = self._flat(description)
        self.assertIn("explicit `$orchestra` invocation", flat)
        self.assertIn("unequivocal imperative to use or start Orchestra", flat)
        self.assertNotIn("explicit planned work in normal chat", description)
        vision = self.canonical["VISION.md"]
        readme = self.canonical["README.md"]
        self.assertIn("explicitly activated Orchestra request", self._flat(vision))
        self.assertIn("exploration, or a candidate specification", self._flat(vision))
        self.assertIn("explicitly activated Orchestra request", self._flat(readme))
        self.assertIn("confirmed specification", self._flat(readme))
        self.assertNotIn("explicitly requested implementation plan", vision)
        self.assertNotIn("explicitly planned software change", readme)

    def test_planning_only_host_mode_is_vendor_neutral(self) -> None:
        for text in (self.skill, self.workflow, self.agents, self.runtime):
            self.assertIn("planning-only host mode", text)
        for name, text in self.canonical.items():
            self.assertNotIn("Plan Mode", text, name)
            self.assertNotIn("mutually exclusive", text.lower(), name)

    def test_planning_only_mode_preserves_context_without_mutation(self) -> None:
        flat_skill = self._flat(self.skill)
        for phrase in (
            "pause before formal task setup",
            "Do not create a branch or worktree, persist a plan, dispatch implementation, commit",
            "continue from the adopted context without requiring another `$orchestra` invocation",
        ):
            self.assertIn(phrase, flat_skill)
        self.assertIn("without a second invocation", self._flat(self.workflow))
        self.assertIn("without a second invocation", self._flat(self.agents))
        for text in (self.skill, self.workflow, self.agents, self.runtime):
            self.assertIn(
                "never changes",
                self._flat(text),
            )

    def test_ordinary_requests_do_not_activate_orchestra(self) -> None:
        self.assertIn("do not activate it", self.skill.lower())
        self.assertIn("remain outside Orchestra", self.workflow)
        self.assertIn("remain outside Orchestra", self.runtime)
        self.assertIn("descriptive mentions", self.skill)
        self.assertIn("Ordinary plan requests", self._flat(self.workflow))

    def test_prepared_task_requires_explicit_skill_and_native_chat_adoption(self) -> None:
        frontmatter = self.task_skill.split("---", 2)[1]
        normalized_skill = self._flat(self.task_skill)
        self.assertIn("explicit `$orchestra-task` invocation", frontmatter)
        self.assertIn("Do not use for ordinary mentions", frontmatter)
        self.assertIn("allow_implicit_invocation: false", self.task_metadata)
        self.assertIn("confirmed specification", normalized_skill)
        self.assertIn("equivalent to Orchestra `repository_context`", normalized_skill)
        self.assertIn("grants no implementation authority", normalized_skill)
        self.assertIn("CODEX_THREAD_ID", normalized_skill)
        self.assertIn("GROK_SESSION_ID", normalized_skill)
        self.assertIn("never supply, invent, copy, or override it", normalized_skill)
        self.assertIn("never creates a host chat", normalized_skill)
        for path in (ROOT / "VISION.md", ROOT / "docs/WORKFLOW.md"):
            normalized = self._flat(path.read_text())
            self.assertTrue(
                "does not activate Orchestra" in normalized
                or "remains inert" in normalized
            )
            self.assertTrue(
                "authorize implementation" in normalized
                or "implementation authority" in normalized
            )

    def test_explicit_specification_gate_fields_remain(self) -> None:
        flat_skill = self._flat(self.skill)
        for field in (
            "Objective",
            "User-visible behavior",
            "Constraints",
            "Acceptance",
            "Exclusions",
            "Decisions",
            "Open questions",
        ):
            self.assertIn(field, flat_skill)
        self.assertIn("Ask only genuine gaps", self.skill)
        self.assertIn("candidate plan", self.skill)

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
        flat_skill = self._flat(self.skill)
        self.assertIn("Codex external mode additionally offers `luna`", flat_skill)
        self.assertIn("`standard` remains the default", flat_skill)
        self.assertIn("explicitly prioritizes cost", flat_skill)
        self.assertNotIn("Tier: light", self.skill)

    def test_dual_mode_is_detected_before_tier_and_immutable_per_task(self) -> None:
        flat_skill = self._flat(self.skill)
        self.assertLess(
            flat_skill.index("Resolve the installed model configuration"),
            flat_skill.index("Recommend and transition tiers"),
        )
        for contract in (
            "session_model.py",
            "require an `ok` result",
            "immutable lookup mode for the task",
            "Changing `native` and `external` requires a new task",
        ):
            self.assertIn(contract, flat_skill)

    def test_plan_is_first_persisted_as_active(self) -> None:
        for text in (self.skill, self.workflow, self.runtime):
            self.assertIn("plan.md", text)
            self.assertIn("`active`", text)
            self.assertNotIn("`draft`", text)
        self.assertIn("no approved `plan.md` is persisted before approval", self.skill)
        self.assertIn("one complete `plan-overview`", self.skill)
        self.assertIn("one complete `plan-phase`", self.skill)
        self.assertIn("approved overview verbatim", self.skill)
        self.assertIn("exact phase manifest", self.skill)
        self.assertNotIn(".orchestra/", (ROOT / ".gitignore").read_text())

    def test_durable_knowledge_checkpoint_targets_only_agent_store(self) -> None:
        self.assertIn("## Durable knowledge checkpoint", self.workflow)
        section = self.workflow.split("## Durable knowledge checkpoint", 1)[1]
        section = section.split("\n## ", 1)[0]
        self.assertIn("`.agent/`", section)
        self.assertIn("`completed`", section)
        self.assertIn("Durable knowledge checkpoint", self.skill)
        for banned in ("memory store", "optmem", "omem"):
            self.assertNotIn(banned, section.lower())

    def test_greenfield_skill_is_implicit_without_activating_orchestra(self) -> None:
        skill_dir = ROOT / "codex/skills/orchestra-project-start"
        skill = (skill_dir / "SKILL.md").read_text()
        metadata = (skill_dir / "agents/openai.yaml").read_text()
        frontmatter = skill.split("---", 2)[1]
        normalized_skill = self._flat(skill)
        for trigger in (
            "create a new project",
            "empty directory",
            "choosing a stack",
            "initial project scaffolding",
        ):
            self.assertIn(trigger, frontmatter)
        self.assertIn("allow_implicit_invocation: true", metadata)
        self.assertIn("Do not activate `$orchestra` automatically", normalized_skill)
        self.assertIn("explicitly accepts", normalized_skill)


if __name__ == "__main__":
    unittest.main()
