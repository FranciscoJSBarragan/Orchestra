"""Static and isolated contracts for composable planned Orchestra work."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
_SYNC_SPEC = importlib.util.spec_from_file_location(
    "orchestra_sync_planned", ROOT / "codex/scripts/sync.py"
)
assert _SYNC_SPEC is not None and _SYNC_SPEC.loader is not None
_sync = importlib.util.module_from_spec(_SYNC_SPEC)
_SYNC_SPEC.loader.exec_module(_sync)
PROFILE_NAMES = {"orchestra_analyst", "orchestra_implementation_worker", "orchestra_reviewer", "orchestra_verifier"}
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


class PlannedFlowContractTests(unittest.TestCase):
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
        self.shared_conduct = (self.references / "shared_conduct.md").read_text()

    def role_skill(self, name: str) -> str:
        return (
            ROOT / f"codex/skills/{ROLE_SKILLS[name]}/SKILL.md"
        ).read_text()

    def instructions(self, name: str) -> str:
        return "\n".join(
            (
                self.role_skill(name),
                self.shared_conduct,
                self.profiles[name]["developer_instructions"],
            )
        )

    def output_instructions(self, name: str) -> str:
        instructions = self.instructions(name)
        return instructions.split("## Output", 1)[1].split("## Stop conditions", 1)[0]

    def input_instructions(self, name: str) -> str:
        instructions = self.instructions(name)
        return instructions.split("## Input", 1)[1].split("## Output", 1)[0]

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
            self.assertIn("stop and return `blocked` with the exact path", stub, name)
            self.assertNotIn("gpt-5.", stub.lower())
            role = self.role_skill(name)
            for heading in ("## Input", "## Output", "## Stop conditions"):
                self.assertIn(heading, role, name)
            self.assertIn("shared_conduct.md", role, name)
            self.assertNotIn("gpt-5.", role.lower())

    def test_capability_inventory_and_profile_mapping_are_exact(self) -> None:
        standard = {
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
        expected_tiers = {
            "native": {"standard", "critical"},
            "external": {"luna", "standard", "critical"},
        }
        for modelconfig, roles in self.role_matrices.items():
            self.assertEqual(set(roles), expected_tiers[modelconfig])
            for tier in expected_tiers[modelconfig]:
                self.assertEqual(
                    {name: value["profile"] for name, value in roles[tier].items()},
                    standard,
                )
            for assignments in roles.values():
                for assignment in assignments.values():
                    self.assertEqual(
                        set(assignment), {"profile", "model", "reasoning_effort"}
                    )
                    self.assertNotEqual(
                        (assignment["model"], assignment["reasoning_effort"]),
                        ("gpt-5.6-sol", "xhigh"),
                    )
                    self.assertNotIn(
                        assignment["profile"], {"root", "orchestrator"}
                    )
        self.assertEqual(
            self.role_matrices["native"]["critical"],
            self.role_matrices["external"]["critical"],
        )
        luna = self.role_matrices["external"]["luna"]
        self.assertEqual(
            {assignment["model"] for assignment in luna.values()},
            {"gpt-5.6-luna"},
        )
        self.assertEqual(
            {
                capability: assignment["reasoning_effort"]
                for capability, assignment in luna.items()
            },
            {
                "repository_context": "xhigh",
                "web_research": "xhigh",
                "technical_planning": "max",
                "architecture_analysis": "max",
                "difficult_debugging": "max",
                "general_implementation": "max",
                "frontend_implementation": "max",
                "independent_review": "max",
                "browser_acceptance": "xhigh",
                "runtime_verification": "xhigh",
            },
        )

    def test_dual_matrix_preserves_legacy_assignments_with_v1_native_aliases(
        self,
    ) -> None:
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
        for assignment in self.dual_modes["external"]["tiers"]["critical"].values():
            self.assertEqual(assignment["model"], "orchestra-v1/gpt-5.6-sol")
        for assignment in self.dual_modes["external"]["tiers"]["luna"].values():
            self.assertEqual(assignment["model"], "orchestra-v1/gpt-5.6-luna")

    def test_seven_playbooks_and_shared_architecture_reference_are_composed(self) -> None:
        expected = {f"{name}.md" for name in PLAYBOOK_NAMES} | {
            "architecture_guidance.md",
            "shared_conduct.md",
        }
        self.assertEqual({path.name for path in self.references.iterdir()}, expected)
        for name in PLAYBOOK_NAMES:
            self.assertIn(f"references/{name}.md", self.skill)
        self.assertGreaterEqual(
            self.skill.count("references/architecture_guidance.md"), 3
        )
        for absent in (
            "general_implementation.md",
            "independent_review.md",
            "architecture_analysis.md",
        ):
            self.assertNotIn(absent, self.skill)

    def test_visible_primary_skill_identity_is_orchestra(self) -> None:
        metadata = (
            ROOT / "codex/skills/orchestra/agents/openai.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn('display_name: "Orchestra"', metadata)
        self.assertNotIn("Orchestra Change Routing", metadata)
        self.assertIn("# Orchestra", self.skill)
        self.assertNotIn("# Route an Orchestra change", self.skill)

    def test_profile_responsibilities_are_bounded(self) -> None:
        analyst = self.instructions("orchestra_analyst")
        self.assertIn("Perform exactly one named analysis capability", analyst)
        self.assertIn("Remain read-only with respect to repository source", analyst)
        worker = self.instructions("orchestra_implementation_worker")
        self.assertIn("approved paths and accepted fixes", worker)
        self.assertIn("same implementation owner", self.skill)
        reviewer = self.instructions("orchestra_reviewer")
        for target in ("plan", "architecture", "code revision", "PR feedback"):
            self.assertIn(target, reviewer)
        self.assertIn("Remain read-only and report-only", reviewer)
        verifier = self.instructions("orchestra_verifier")
        self.assertIn("runtime, test, log, or visible-browser checks", verifier)
        self.assertIn("Remain read-only with respect to repository source", verifier)
        for name in PROFILE_NAMES:
            instructions = self.instructions(name)
            self.assertRegex(
                instructions, r"Do not choose[^.\n]*model[^.\n]*reasoning effort", name
            )
            for boundary in ("route work", "spawn agents", "orchestrate"):
                self.assertIn(boundary, instructions, name)

    def test_profile_returns_are_outcome_first_and_lossless_for_material_evidence(
        self,
    ) -> None:
        material_terms = (
            "security",
            "privacy",
            "authentication",
            "payment",
            "destructive or irreversible",
            "blocker or authority",
            "failure or exact error",
            "reviewer finding",
            "ambiguity or conflicting evidence",
            "verification",
            "locator",
            "remaining risk",
        )
        existing_output_fields = {
            "orchestra_analyst": ("evidence", "planned", "diagnosed", "blocked", "produced artifact identifiers", "candidate bundle", "blockers", "material risks", "decisions requested"),
            "orchestra_implementation_worker": ("implemented", "blocked", "implementation-report", "changed paths", "tests changed", "verification commands", "cleanup status", "retained-resources declaration", "remaining risks"),
            "orchestra_reviewer": ("accepted", "findings", "blocked", "review target", "stable identifier", "verification or authority gaps", "rejected pr feedback"),
            "orchestra_verifier": ("passed", "failed", "blocked", "verification-report", "commands or interaction steps", "observed output or behavior", "evidence references", "environment details", "cleanup status", "retained-resources declaration"),
        }
        conduct = " ".join(self.shared_conduct.lower().split())
        for omission in (
            "packet replay",
            "praise",
            "unchanged context",
            "duplicate evidence",
        ):
            self.assertIn(omission, conduct)
        for term in material_terms:
            self.assertIn(term, conduct)
        self.assertIn("redact secrets", conduct)
        self.assertIn("safe category or locator", conduct)
        for name in PROFILE_NAMES:
            output = self.output_instructions(name).lower().strip()
            first_sentence = output.split(".", 1)[0]
            self.assertTrue(output.startswith("return the outcome or status"), name)
            self.assertIn(" first, then ", first_sentence, name)
            for field in existing_output_fields[name]:
                self.assertIn(field, output, name)
            for identity in (
                "committed revision",
                "when uncommitted changes",
                "dirty worktree",
                "diff state",
            ):
                self.assertIn(identity, output, name)
            self.assertNotIn("otherwise name", output, name)

    def test_material_context_discoveries_use_existing_reports_and_root_disposition(
        self,
    ) -> None:
        conduct = " ".join(self.shared_conduct.lower().split())
        for contract in (
            "conditional `context discoveries` section",
            "report-local stable identifier",
            "observed fact, supported inference, or unresolved uncertainty",
            "evidence and locator",
            "inspected revision",
            "material impact",
            "mandatory `affected judgment`",
            "named current-task consumer",
            "<artifact-identifier>#ctx-001",
            "complete inline report with its report-local `ctx-001`",
            "keep that report and local id together",
            "omit incidental stale information",
            "omit the section when nothing qualifies",
            "do not repeat unchanged context",
            "root alone assigns its disposition",
        ):
            self.assertIn(contract, conduct)

        for name in PROFILE_NAMES:
            output = " ".join(self.output_instructions(name).lower().split())
            for contract in (
                "context-discovery references",
                "composite identifiers for published reports",
                "local identifiers beside the complete inline fallback",
            ):
                self.assertIn(contract, output, name)

        worker = " ".join(
            self.instructions("orchestra_implementation_worker").lower().split()
        )
        for boundary in (
            "context discovery never expands edit authority",
            "canonical repository documentation",
            "root packet supplies an explicit `persist` disposition",
            "validating `context-delta` confirms a `descriptive` claim",
            "`context maintenance paths`",
            "without glob authority",
        ):
            self.assertIn(boundary, worker)

        reviewer = " ".join(
            self.instructions("orchestra_reviewer").lower().split()
        )
        self.assertIn("remain read-only and report-only", reviewer)
        self.assertIn("never becomes a silent documentation edit", reviewer)

        repository_context = " ".join(
            (self.references / "repository_context.md").read_text().lower().split()
        )
        for contract in (
            "after plan approval",
            "only at a stable handoff",
            "composite context-discovery identifier",
            "inspect the claim independently",
            "targeted `context-delta`",
        ):
            self.assertIn(contract, repository_context)

        root_sources = {
            "workflow": (ROOT / "docs/WORKFLOW.md").read_text(),
            "root skill": self.skill,
            "runtime": (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
        }
        for name, source in root_sources.items():
            normalized = " ".join(source.lower().split())
            for disposition in (
                "`route`",
                "`validate`",
                "`replan`",
                "`persist`",
                "`defer`",
                "`discard`",
            ):
                self.assertIn(disposition, normalized, name)
            self.assertIn("stable handoff", normalized, name)
            self.assertIn("only `repository_context`", normalized, name)
            self.assertIn("before phase teardown", normalized, name)
            self.assertIn("inline", normalized, name)

        durable_sources = {
            "vision": (ROOT / "VISION.md").read_text(),
            "workflow": (ROOT / "docs/WORKFLOW.md").read_text(),
            "architecture": (ROOT / "docs/ARCHITECTURE.md").read_text(),
            "source agents": (ROOT / "AGENTS.md").read_text(),
            "root skill": self.skill,
            "runtime": (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
        }
        for name, source in durable_sources.items():
            normalized = " ".join(source.lower().split())
            self.assertIn("material context", normalized, name)
            self.assertIn("versioned", normalized, name)

        combined = "\n".join(durable_sources.values()) + "\n" + self.shared_conduct
        self.assertNotIn("<NN>-context-discovery", combined)
        self.assertNotIn("context-discovery-report", combined)

    def test_phase_review_context_is_traced_and_corrected_without_self_review(
        self,
    ) -> None:
        planning = " ".join(
            (self.references / "technical_planning.md")
            .read_text()
            .lower()
            .split()
        )
        for contract in (
            "`review context` section",
            "`repository-context` and `context-delta` artifact identifiers",
            "canonical source paths consulted",
            "architecture, runtime, exposure, persistence, user-visible surface",
            "`context maintenance paths`",
            "exact repository-relative paths",
            "never use glob metacharacters",
            "validated `descriptive` discovery",
            "explicit root `persist` disposition",
        ):
            self.assertIn(contract, planning)

        repository_context = " ".join(
            (self.references / "repository_context.md")
            .read_text()
            .lower()
            .split()
        )
        for contract in (
            "evidence classification",
            "context classification",
            "`descriptive`",
            "`normative`",
            "`uncertain`",
            "classify the claim, not an entire mixed-purpose file",
            "never treat current code as proof that a normative source is stale",
            "claim result (`confirmed`, `disproved`, or `unresolved`)",
            "revalidation dispatch",
            "current dirty revision",
        ):
            self.assertIn(contract, repository_context)

        reviewer = " ".join(
            self.instructions("orchestra_reviewer").lower().split()
        )
        for contract in (
            "approved user intent and acceptance",
            "overview's `review context`",
            "current source and diff",
            "verification evidence",
            "every exact `repository-context` or `context-delta`",
            "complete inline fallback and stable label",
            "every `implementation-review` contains `context basis`",
            "missing, stale, or conflicting project context",
            "never fill the context gap with assumptions",
            "remain read-only and report-only",
        ):
            self.assertIn(contract, reviewer)

        worker = " ".join(
            self.instructions("orchestra_implementation_worker").lower().split()
        )
        for contract in (
            "exact discovery identifier",
            "root `persist` disposition",
            "validating `context-delta`",
            "exact phase-listed maintenance path",
            "versioned human-readable context documentation",
            "executable configuration, databases, generated data, and operational data",
            "targeted `repository_context` revalidation",
            "do not claim that editing the documentation proves",
            "never independently accept or review your own work",
        ):
            self.assertIn(contract, worker)

        routing_sources = {
            "vision": (ROOT / "VISION.md").read_text(),
            "workflow": (ROOT / "docs/WORKFLOW.md").read_text(),
            "architecture": (ROOT / "docs/ARCHITECTURE.md").read_text(),
            "source agents": (ROOT / "AGENTS.md").read_text(),
            "root skill": self.skill,
            "runtime": (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
        }
        for name, source in routing_sources.items():
            normalized = " ".join(source.lower().split())
            for contract in (
                "review context",
                "context maintenance paths",
                "context basis",
                "same implementation owner",
                "revalidation",
                "delta review",
                "normative",
            ):
                self.assertIn(contract, normalized, name)

        root_contract = " ".join(self.skill.lower().split())
        self.assertIn("blocks phase commit", root_contract)
        self.assertIn("no `plan.md` manifest or workflow-state field", root_contract)
        self.assertNotIn("<NN>-review-context", "\n".join(routing_sources.values()))
        self.assertNotIn("<NN>-context-basis", "\n".join(routing_sources.values()))

    def test_phase_review_context_requires_demonstrable_relevance(self) -> None:
        planning = " ".join(
            (self.references / "technical_planning.md")
            .read_text()
            .lower()
            .split()
        )
        for contract in (
            "`review use`",
            "exact acceptance, risk, invariant, exclusion, or phase dependency",
            "omit anything without a current-task use",
            "do not copy cited evidence bodies",
            "use `none` unless",
            "named current-phase or identified later-phase consumer",
        ):
            self.assertIn(contract, planning)

        shared = " ".join(self.shared_conduct.lower().split())
        for contract in (
            "mandatory `affected judgment`",
            "named current-task consumer",
            "omit incidental stale information",
            "when nothing qualifies",
        ):
            self.assertIn(contract, shared)

        reviewer = " ".join(
            self.instructions("orchestra_reviewer").lower().split()
        )
        for contract in (
            "named `review use`",
            "routed-but-unopened evidence",
            "exact `affected judgment`",
            "omit incidental stale information",
            "never list evidence merely because the packet routed it",
            "an incidental discrepancy never blocks",
            "state that judgment in the blocker",
        ):
            self.assertIn(contract, reviewer)

        repository_context = " ".join(
            (self.references / "repository_context.md")
            .read_text()
            .lower()
            .split()
        )
        for contract in (
            "mandatory `affected judgment`",
            "named current-task consumer",
            "at least one possible result could change acceptance",
            "return `blocked` without scanning",
            "effect on the named judgment and consumer",
            "post-edit revalidation is mandatory",
            "bypasses the earlier decision-change admission gate",
        ):
            self.assertIn(contract, repository_context)

        workflow = " ".join(
            (ROOT / "docs/WORKFLOW.md").read_text().lower().split()
        )
        runtime = " ".join(
            (ROOT / "codex/runtime/AGENTS.orchestra.md")
            .read_text()
            .lower()
            .split()
        )
        root_contract = " ".join(self.skill.lower().split())
        for name, source in (
            ("workflow", workflow),
            ("root skill", root_contract),
            ("runtime", runtime),
        ):
            for contract in (
                "review use",
                "affected judgment",
                "named current-task consumer",
                "discard without validation",
                "only new or replaced evidence",
                "incidental",
            ):
                self.assertIn(contract, source, name)

        self.assertIn(
            "post-edit proof bypasses the earlier relevance pruning",
            root_contract,
        )
        self.assertLess(len(self.skill.splitlines()), 500)

        combined = "\n".join((workflow, root_contract, runtime, reviewer, shared))
        for forbidden in (
            "context token budget",
            "context size limit",
            "context counter",
            "<nn>-review-use",
            "context-relevance-report",
        ):
            self.assertNotIn(forbidden, combined)

    def test_worker_minimality_requires_focused_comprehension_and_supported_cause(
        self,
    ) -> None:
        worker = self.instructions("orchestra_implementation_worker").lower()
        responsibility = worker.split("## input", 1)[0]
        worker_input = self.input_instructions("orchestra_implementation_worker").lower()
        for requirement in (
            "before editing",
            "affected flow",
            "relevant callers",
            "allowed paths constrain edits",
            "focused safe read-only inspection",
            "standard-library",
            "native-platform",
            "already-installed dependency primitives",
            "do not follow a rigid preference order",
            "supported root cause at the causal boundary that explains the affected behavior",
            "do not substitute a symptom-only patch",
            "remaining limitation only when current evidence supports it",
            "concrete revisit trigger",
        ):
            self.assertIn(requirement, worker)
        self.assertIn("necessary edit, public behavior change, or scope expansion", worker)
        shared_scope = "before editing for either implementation capability"
        general_branch = "for `general_implementation`, these base instructions"
        frontend_branch = "for `frontend_implementation`, also follow"
        self.assertIn(shared_scope, responsibility)
        self.assertIn(general_branch, responsibility)
        self.assertIn(frontend_branch, responsibility)
        for shared_rule in (
            shared_scope,
            "reuse repository",
            "supported root cause",
            "remaining limitation",
        ):
            self.assertLess(
                responsibility.index(shared_rule),
                responsibility.index(general_branch),
            )
            self.assertLess(
                responsibility.index(shared_rule),
                responsibility.index(frontend_branch),
            )
        self.assertNotIn("focused read-only inspection scope", worker_input)
        for packet_field in (
            "explicit edit authority",
            "worktree",
            "approved plan-manifest path",
            "exact `plan-overview` identifier",
            "exact current `plan-phase` identifier",
            "stop conditions",
            "revision identity",
            "accepted finding identifiers",
            "only newly changed context",
        ):
            self.assertIn(packet_field, worker_input)
        self.assertIn(
            "read objective, allowed paths, acceptance, verification",
            worker_input,
        )
        self.assertIn("do not require the root to replay them", worker_input)

    def test_approved_outcome_is_preserved_while_mechanisms_remain_hypotheses(
        self,
    ) -> None:
        root_sources = {
            "vision": (ROOT / "VISION.md").read_text(),
            "workflow": (ROOT / "docs/WORKFLOW.md").read_text(),
            "architecture": (ROOT / "docs/ARCHITECTURE.md").read_text(),
            "source agents": (ROOT / "AGENTS.md").read_text(),
            "root skill": self.skill,
            "runtime agents": (
                ROOT / "codex/runtime/AGENTS.orchestra.md"
            ).read_text(),
        }
        for name, source in root_sources.items():
            normalized = " ".join(source.lower().split())
            self.assertIn(
                "approved objective, constraints, acceptance, and authority",
                normalized,
                name,
            )
            self.assertIn(
                "proposed mechanism or causal explanation",
                normalized,
                name,
            )
            self.assertIn("hypothesis", normalized, name)

        conduct = " ".join(self.shared_conduct.lower().split())
        for distinction in ("observed facts", "supported inference", "uncertainty"):
            self.assertIn(distinction, conduct)
        self.assertIn("report conflicts", conduct)
        self.assertIn("silently replacing the approved result", conduct)

    def test_user_visualization_is_conditional_root_only_and_non_blocking(
        self,
    ) -> None:
        root_sources = {
            "workflow": (ROOT / "docs/WORKFLOW.md").read_text(),
            "root skill": self.skill,
            "runtime agents": (
                ROOT / "codex/runtime/AGENTS.orchestra.md"
            ).read_text(),
        }
        for name, source in root_sources.items():
            normalized = " ".join(source.lower().split())
            self.assertIn(
                "complex sequence, hierarchy, comparison, or mapping",
                normalized,
                name,
            )
            self.assertIn("simple explanations", normalized, name)
            self.assertIn("never blocks", normalized, name)
            self.assertIn("delegated agents", normalized, name)
            for distinction in (
                "verified facts",
                "supported inference",
                "uncertainty",
            ):
                self.assertIn(distinction, normalized, name)

        conduct = " ".join(self.shared_conduct.lower().split())
        self.assertIn("do not address the user", conduct)
        self.assertIn("invoke user-facing visualization capabilities", conduct)
        self.assertIn("root owns user explanation and synthesis", conduct)

    def test_planning_and_implementation_require_tests_with_behavioral_signal(
        self,
    ) -> None:
        planning = " ".join(
            (self.references / "technical_planning.md")
            .read_text()
            .lower()
            .split()
        )
        worker = " ".join(
            self.instructions("orchestra_implementation_worker").lower().split()
        )
        for source in (planning, worker):
            for requirement in (
                "observable acceptance journey",
                "named regression risk",
                "duplicated coverage",
                "count-driven tests",
                "implementation details",
                "approved contract",
            ):
                self.assertIn(requirement, source)

        worker_output = " ".join(
            self.output_instructions("orchestra_implementation_worker")
            .lower()
            .split()
        )
        self.assertIn(
            "behavior or regression risk each test demonstrates",
            worker_output,
        )

    def test_reviewer_complexity_is_material_not_metric_scoring(self) -> None:
        reviewer = self.instructions("orchestra_reviewer").lower()
        for requirement in (
            "unsupported consumer, requirement, or reproducible risk",
            "recommend deletion, an existing primitive, or a smaller direct implementation",
            "line count, file count, abstraction count, or unfamiliarity alone",
            "stable identifier",
            "severity, causal rationale, evidence and locator, and correction rationale",
        ):
            self.assertIn(requirement, reviewer)

    def test_dispatch_packet_pins_phase_acceptance_and_scope_stop_conditions(self) -> None:
        reviewer_input = self.input_instructions("orchestra_reviewer").lower()
        self.assertIn(
            "read objective, scope, acceptance, prior evidence, and plan details "
            "directly from those artifacts",
            reviewer_input,
        )
        reviewer_stop = self.instructions("orchestra_reviewer").split("## Stop conditions", 1)[1].lower()
        self.assertIn(
            "stop and return `blocked` when acceptance criteria cannot be "
            "resolved from the exact target artifacts",
            reviewer_stop,
        )
        worker_stop = self.instructions("orchestra_implementation_worker").split(
            "## Stop conditions", 1
        )[1].lower()
        self.assertIn(
            "stop when the change materially expands the approved phase "
            "objective, acceptance criteria, exclusions, or explicit authority, even inside "
            "allowed paths",
            worker_stop,
        )

    def test_retired_environment_identifiers_and_bridge_marker_stay_absent(self) -> None:
        sources = [
            self.skill,
            (ROOT / "VISION.md").read_text(),
            (ROOT / "docs/WORKFLOW.md").read_text(),
            (ROOT / "docs/ARCHITECTURE.md").read_text(),
            (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
            (ROOT / "codex/scripts/integrate_local.py").read_text(),
            (ROOT / "codex/scripts/pr.py").read_text(),
        ]
        combined = "\n".join(sources)
        for removed in (
            "current" + "_branch",
            "codex" + "_worktree",
            "execution" + "_mode",
            "CODEX_EXECUTION" + "_WORKSPACE",
        ):
            self.assertNotIn(removed, combined)

    def test_compact_context_requests_lossless_returns_without_hard_caps(self) -> None:
        self.assertIn("Request outcome-first, lossless structured returns", self.skill)
        self.assertIn(
            "never impose a token, line, file, finding, test, or explanation cap",
            self.skill,
        )
        architecture = " ".join(
            (ROOT / "docs/ARCHITECTURE.md").read_text().lower().split()
        )
        for invariant in (
            "outcome-first output status",
            "dirty worktree or diff state",
            "focused read-only inspection",
            "supported root cause at the causal boundary",
            "reproducible risk",
        ):
            self.assertIn(invariant, architecture)
        self.assertIn(
            "exact target artifact identifiers and their roles",
            " ".join(self.skill.split()),
        )

    def test_coordination_artifacts_are_shared_but_never_authoritative(self) -> None:
        normalized_skill = " ".join(self.skill.split())
        workflow = " ".join((ROOT / "docs/WORKFLOW.md").read_text().split())
        runtime = " ".join(
            (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text().split()
        )
        shared_conduct = " ".join(
            (self.references / "shared_conduct.md").read_text().split()
        )
        architecture = " ".join((ROOT / "docs/ARCHITECTURE.md").read_text().split())
        for contract in (
            "coordination.py",
            "task create",
            "task_state.py",
            "<task-worktree>/.orchestra/artifacts",
            "the file name is the artifact identifier",
            "material start, final, or blocker",
            "there are no heartbeats",
            "complete report inline",
            "never blocks a tier change",
            "only the root writes the plan",
        ):
            self.assertIn(contract.lower(), normalized_skill.lower())
        for contract in (
            "$HOME/.orchestra/state.sqlite3",
            "no transition graph",
            "never runs mutating Git commands",
            "no database locator exists",
            "already at `0600` are left unchanged",
        ):
            self.assertIn(contract.lower(), workflow.lower())
        for contract_source in (normalized_skill, workflow, runtime, shared_conduct):
            self.assertIn("first attempt", contract_source.lower())
            self.assertIn("known-protected", contract_source.lower())
            self.assertIn("narrow guardian escalation", contract_source.lower())
        for contract_source in (normalized_skill, workflow, shared_conduct):
            self.assertIn("without", contract_source.lower())
            self.assertIn("protected-write escalation", contract_source.lower())
        self.assertIn("correctly authorized attempt", normalized_skill.lower())
        self.assertIn("correctly authorized attempt", workflow.lower())
        self.assertIn("correctly authorized attempt", runtime.lower())
        self.assertIn("correctly authorized attempt", shared_conduct.lower())
        for contract in (
            "tasks and material agent activities",
            "telemetry loss, not workflow failure",
            "no authority, event history, heartbeat requirement",
        ):
            self.assertIn(contract.lower(), architecture.lower())
        for name in PROFILE_NAMES:
            instructions = self.instructions(name)
            self.assertIn("coordination.py", instructions, name)
            self.assertIn("complete", instructions.lower(), name)
            self.assertIn("inline", instructions.lower(), name)
        context = (self.references / "repository_context.md").read_text()
        planning = " ".join(
            (self.references / "technical_planning.md").read_text().split()
        )
        self.assertIn("<NN>-repository-context.md", context)
        self.assertIn("<NN>-plan-overview.md", planning)
        self.assertIn("<NN>-plan-phase-p<number>.md", planning)
        self.assertIn("complete replacement", planning)

    def test_coordination_localizes_only_user_visible_snapshot_text(self) -> None:
        sources = {
            "workflow": (ROOT / "docs/WORKFLOW.md").read_text(),
            "root skill": self.skill,
            "runtime": (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
            "shared conduct": self.shared_conduct,
        }
        for name, source in sources.items():
            normalized = " ".join(source.lower().split())
            for field in ("`summary`", "`blocker`", "`next_action`"):
                self.assertIn(field, normalized, name)
            self.assertIn("activity `summary`", normalized, name)
            self.assertIn("user-facing language", normalized, name)
            self.assertIn("language of the user's conversation", normalized, name)
            self.assertIn("machine-facing", normalized, name)
            self.assertIn("labels in english", normalized, name)
            self.assertIn("literal errors, commands, paths, and identifiers", normalized, name)
            self.assertIn("semantic artifacts", normalized, name)
            self.assertIn("technical logs", normalized, name)

        root_contract = " ".join(self.skill.lower().split())
        self.assertIn("keep `plan.md`", root_contract)
        self.assertIn("do not add or infer a persisted locale", root_contract)

    def test_document_handoffs_use_exact_bundle_members_without_root_replay(self) -> None:
        normalized = " ".join(self.skill.split())
        for contract in (
            "exact target artifact identifiers and their roles",
            "Do not replay objective, scope, acceptance, verification",
            "one complete `plan-overview` artifact",
            "one complete `plan-phase` artifact per phase",
            "never by timestamp or list order",
            "approved overview verbatim",
            "does not duplicate detailed phase documents",
            "exact overview identifier",
            "exact current phase identifier",
            "only prior outputs explicitly required by that phase",
            "do not restate the findings",
            "do not create a commit artifact",
        ):
            self.assertIn(contract.lower(), normalized.lower())

    def test_plan_review_is_conditional_and_root_adjudicates_convergence(self) -> None:
        normalized = " ".join(self.skill.split())
        for contract in (
            "After the complete formal bundle exists",
            "trivial single-phase `luna` or `standard` plan may skip review",
            "non-trivial multi-phase or cross-component plan receives one review",
            "critical plan receives a focused review",
            "same planner",
            "stable finding identifiers",
            "after a second material review",
            "before a third correction",
            "marginal, contradictory, or out-of-scope findings",
            "not a persisted counter or mechanical limit",
        ):
            self.assertIn(contract.lower(), normalized.lower())

    def test_new_formal_task_selects_checkout_and_creates_branch_before_discovery(
        self,
    ) -> None:
        isolation = self.skill.index("## Select the task checkout and create its branch")
        repository_dispatch = self.skill.index(
            "dispatch `repository_context` to an `orchestra_analyst`"
        )
        self.assertLess(isolation, repository_dispatch)
        normalized = " ".join(self.skill.split())
        for invariant in (
            "`${CODEX_HOME:-$HOME/.codex}/orchestra/checkout-mode`",
            "`managed` or `hybrid`",
            "`${CODEX_HOME:-$HOME/.codex}/orchestra/worktree-root`",
            "`$HOME/.orchestra/worktrees`",
            "`git worktree add`",
            "captured full base revision",
            "`git switch -c <branch> <captured-head>`",
            "Never implement on the starting branch or directly on `main`",
            "Dirty, detached, conflicted",
            "adopt_worktree.py",
            "same live preapproval task",
            "checkout mode/path, starting identity, task branch",
            "remove only proven-clean resources",
            "completion without an artificial commit",
        ):
            self.assertIn(invariant, normalized)

    def test_worktree_creation_uses_direct_git_in_all_routing_sources(self) -> None:
        sources = (
            self.skill,
            (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
            (ROOT / "docs/WORKFLOW.md").read_text(),
        )
        for source in sources:
            normalized = " ".join(source.split()).lower()
            for contract in (
                "git worktree add",
                "full base revision",
                "git error",
                "capability dispatch",
            ):
                self.assertIn(contract.lower(), normalized)
            self.assertNotIn("create_worktree.py", normalized)
        root_contract = " ".join((ROOT / "AGENTS.md").read_text().split()).lower()
        self.assertIn("managed mode", root_contract)
        self.assertIn("hybrid mode", root_contract)
        self.assertIn("never implement on the starting branch or `main`", root_contract)

    def test_agent_waiting_is_long_non_interruptive_and_timeout_is_not_failure(
        self,
    ) -> None:
        normalized = " ".join(self.skill.split())
        for contract in (
            "`wait_agent` in non-interruptive ten-minute windows",
            "`timeout_ms: 600000`",
            "returns as soon as an agent reaches a final state",
            "`timed_out` means only that the agent is still working",
            "wait again without `send_input`",
            "`interrupt: true`",
            "After 30 accumulated minutes",
            "elapsed time alone is not a failure",
        ):
            self.assertIn(contract, normalized)

    def test_implementation_handoff_bounds_root_observation_and_findings(
        self,
    ) -> None:
        normalized = " ".join(self.skill.split())
        active_owner = normalized.index(
            "While the implementation owner is active and has not returned "
            "an outcome or blocker"
        )
        handoff = normalized.index("At each implementation-owner handoff")
        verification = normalized.index("Dispatch `runtime_verification`")
        self.assertLess(active_owner, handoff)
        self.assertLess(handoff, verification)
        for contract in (
            "without reading the evolving diff",
            "running speculative canaries against it",
            "root-owned setup that does not inspect or exercise the evolving "
            "implementation",
            "at most one bounded check of exact Git identity, status, "
            "allowed-path scope, `git diff --check`, and the declared evidence "
            "inventory",
            "complete and confirm that investigation against the exact current "
            "source and diff",
            "one consolidated finding packet with evidence, impact, and "
            "acceptance",
            "never send provisional or superseding directions",
        ):
            self.assertIn(contract, normalized)

    def test_required_verification_finishes_before_independent_review(
        self,
    ) -> None:
        normalized = " ".join(self.skill.split())
        freeze = normalized.index(
            "Once a stable revision packet is under verification"
        )
        gate = normalized.index(
            "Dispatch `independent_review` only after every required verifier"
        )
        review = normalized.index(
            "Then dispatch one `independent_review` agent"
        )
        self.assertLess(freeze, gate)
        self.assertLess(gate, review)
        for contract in (
            "stop speculative root source review",
            "a confirmed finding invalidates the packet",
            "its blocker is explicitly accepted",
        ):
            self.assertIn(contract, normalized)

    def test_phase_observation_boundary_is_consistent_across_sources(self) -> None:
        for path in (
            "VISION.md",
            "docs/WORKFLOW.md",
            "docs/ARCHITECTURE.md",
            "codex/runtime/AGENTS.orchestra.md",
        ):
            normalized = " ".join((ROOT / path).read_text().split())
            self.assertIn("evolving implementation", normalized, path)
            self.assertIn("consolidated", normalized, path)
            self.assertIn("stable revision", normalized, path)
            self.assertRegex(normalized, r"required (verification|verifier)", path)
            self.assertRegex(normalized, r"independent[ _]review", path)

    def test_initial_context_precedes_final_specification_and_plan(self) -> None:
        normalized = " ".join(self.skill.split())
        brief = normalized.index("minimum brief with objective")
        worktree = normalized.index("## Select the task checkout and create its branch")
        context = normalized.index(
            "dispatch `repository_context` to an `orchestra_analyst`"
        )
        final_specification = normalized.index(
            "present and confirm the complete specification"
        )
        plan = normalized.index(
            "Final specification confirmation is the checkpoint to draft the plan"
        )
        self.assertLess(brief, worktree)
        self.assertLess(worktree, context)
        self.assertLess(context, final_specification)
        self.assertLess(final_specification, plan)
        for contract in (
            "If `$orchestra` is invoked without an objective",
            "before creating resources",
            "explicitly limits the request to brainstorming",
            "remain read-only",
            "Recommend any justified tier change",
            "do not require a second literal request to make a plan",
            "Specification confirmation authorizes plan drafting, not implementation",
        ):
            self.assertIn(contract, normalized)

    def test_repository_context_repeats_only_as_delta_and_cleans_safe_abandonment(
        self,
    ) -> None:
        normalized = " ".join(self.skill.split())
        for contract in (
            "newly material factual question",
            "request only the targeted context delta",
            "close each one-shot analyst and its descendants",
            "On preapproval abandonment",
            "never discard unique work",
            "remove only proven-clean resources",
            "no approved `plan.md` is persisted before approval",
            "clearly labeled private artifact",
        ):
            self.assertIn(contract, normalized)

    def test_repository_context_model_fallback_is_narrow_and_transient(
        self,
    ) -> None:
        external_context = self.role_matrices["external"]["standard"][
            "repository_context"
        ]
        self.assertEqual(
            external_context,
            {
                "profile": "orchestra_analyst",
                "model": "opencode/deepseek-v4-flash",
                "reasoning_effort": "max",
            },
        )
        normalized = " ".join(self.skill.split())
        assigned_first = normalized.index("Always attempt the installed assignment first")
        fallback = normalized.index("Luna and reasoning `high`")
        self.assertLess(assigned_first, fallback)
        for contract in (
            "Only when a `repository_context` spawn is rejected before execution",
            "internal subagent runtime does not support the assigned model",
            "dual `external` mode",
            "dual `native` mode blocks instead of crossing protocol versions",
            "Record the substitution only in root memory",
            "Do not create a visible Codex task",
            "persist fallback state",
            "edit the source or installed matrix",
            "use this fallback for another capability",
            "If any other capability's assigned model is unsupported, return `blocked`",
        ):
            self.assertIn(contract, normalized)

    def test_git_worktree_contract_isolated_collision_and_safe_cancel(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / "repo"
            worktree_root = root / "home" / ".orchestra" / "worktrees"
            repository_root = worktree_root / base.name
            unrelated = repository_root / "example"
            task = repository_root / "example-2"
            subprocess.run(
                ["git", "init", "-b", "main", str(base)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(base), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(base), "config", "user.name", "Test"], check=True
            )
            seed = base / "seed.txt"
            seed.write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(base), "add", "seed.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(base), "commit", "-m", "seed"],
                check=True,
                capture_output=True,
                text=True,
            )
            base_sha = subprocess.run(
                ["git", "-C", str(base), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            repository_root.mkdir(parents=True)
            canary = repository_root / ".orchestra-write-canary"
            canary.write_text("write-check\n", encoding="utf-8")
            canary.unlink()
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(base),
                    "worktree",
                    "add",
                    "-b",
                    "orchestra/example",
                    str(unrelated),
                    base_sha,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            seed.write_text("uncommitted user work\n", encoding="utf-8")
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(base),
                    "worktree",
                    "add",
                    "-b",
                    "orchestra/example-2",
                    str(task),
                    base_sha,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            task_head = subprocess.run(
                ["git", "-C", str(task), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            task_status = subprocess.run(
                ["git", "-C", str(task), "status", "--porcelain"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(task_head, base_sha)
            self.assertEqual(task_status, "")
            self.assertEqual(seed.read_text(encoding="utf-8"), "uncommitted user work\n")
            self.assertEqual(task.parent, worktree_root / "repo")
            self.assertTrue(unrelated.exists())

            subprocess.run(
                ["git", "-C", str(base), "worktree", "remove", str(task)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(base), "branch", "-d", "orchestra/example-2"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertFalse(task.exists())
            self.assertTrue(unrelated.exists())
            branch = subprocess.run(
                [
                    "git",
                    "-C",
                    str(base),
                    "branch",
                    "--list",
                    "orchestra/example-2",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(branch.stdout, "")

    def test_hybrid_clean_main_branches_in_place_before_work(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            subprocess.run(
                ["git", "init", "-b", "main", str(repo)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "config", "user.name", "Test"], check=True
            )
            (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "seed.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "commit", "-m", "seed"],
                check=True,
                capture_output=True,
                text=True,
            )
            start = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "HEAD"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()

            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "switch",
                    "-c",
                    "orchestra/hybrid",
                    start,
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            branch = subprocess.run(
                ["git", "-C", str(repo), "branch", "--show-current"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            main = subprocess.run(
                ["git", "-C", str(repo), "rev-parse", "main"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            status = subprocess.run(
                ["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertEqual(branch, "orchestra/hybrid")
            self.assertEqual(main, start)
            self.assertEqual(status, "")

    def test_local_plan_path_is_per_worktree_and_root_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary) / "repo"
            linked = Path(temporary) / "linked"
            subprocess.run(
                ["git", "init", "-b", "main", str(base)],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(base), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(base), "config", "user.name", "Test"], check=True
            )
            (base / "seed.txt").write_text("seed\n")
            subprocess.run(["git", "-C", str(base), "add", "seed.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(base), "commit", "-m", "seed"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(base), "worktree", "add", "-b", "task", str(linked)],
                check=True,
                capture_output=True,
                text=True,
            )

            def plan_path(worktree: Path) -> Path:
                return worktree.resolve() / ".orchestra" / "plan.md"

            base_plan = plan_path(base).resolve()
            linked_plan = plan_path(linked).resolve()
            self.assertNotEqual(base_plan, linked_plan)
            self.assertEqual(base_plan.parent.name, ".orchestra")
            self.assertEqual(linked_plan.parent.name, ".orchestra")

        self.assertIn("<task-worktree>/.orchestra/plan.md", self.skill)
        self.assertIn("task_state.py", self.skill)
        for status in ("`active`", "`blocked`", "`completed`"):
            self.assertIn(status, self.skill)
        self.assertNotIn("`draft`", self.skill)
        self.assertIn("Only the root writes the plan", self.skill)
        self.assertIn("Git is authoritative", self.skill)
        for field in (
            "task and Git identity",
            "approved overview verbatim",
            "exact phase manifest",
            "artifact identifier, private path, revision",
            "authorized preexisting changes",
        ):
            self.assertIn(field, self.skill)

    def test_browser_routing_prefers_chrome_and_honors_explicit_selection(
        self,
    ) -> None:
        browser = (self.references / "browser_acceptance.md").read_text()
        frontend = (self.references / "frontend_implementation.md").read_text()
        for contract in (
            "Require `browser_route: auto | in_app | chrome`",
            "explicitly select the dedicated Chrome connector first",
            "fall back to Codex's in-app Browser only",
            "remains fixed without fallback",
            "functional failure, application timeout, or selector problem never triggers fallback",
            "repeat the complete scenario",
            "Do not substitute Computer Use or standalone browser automation",
            "create a fresh task-dedicated tab",
            "Never claim or reuse a user's existing tab",
            "close the dedicated task tab before every handoff, whether successful, failed, or blocked",
            "Never retain the task tab or another owned resource across a browser-acceptance handoff",
            "never close the Chrome application or a shared window",
            "Preserve all unrelated tabs",
        ):
            self.assertIn(contract, browser)
        normalized_frontend = " ".join(frontend.split())
        for contract in (
            "`browser_route: auto | in_app | chrome`",
            "dedicated Chrome connector first",
            "Codex's in-app Browser only",
            "never triggers fallback",
            "repeat the complete visual scenario",
            "create a fresh implementation-owned task tab",
            "never claim or reuse a user tab",
            "before every handoff, whether successful, failed, or blocked",
            "Retain no task tab or supporting process across the handoff",
            "return `retained_resources: none`",
            "separate from independent acceptance",
        ):
            self.assertIn(contract, normalized_frontend)
        for retired in (
            "Computer Use with Chrome",
            "Chrome browser plugin",
            "in-app Browser first",
        ):
            self.assertNotIn(retired, browser)
            self.assertNotIn(retired, frontend)
        for profile in (
            "orchestra_implementation_worker",
            "orchestra_verifier",
        ):
            role_input = " ".join(self.input_instructions(profile).split())
            self.assertIn("`auto` carries its defined technical fallback", role_input)
            self.assertIn("a user-selected route is strict", role_input)
        self.assertIn("Never claim acceptance of your own work", frontend)
        self.assertIn("browser acceptance is an independent verifier dispatch", self.skill)

    def test_phase_agents_are_reused_then_closed_before_commit(self) -> None:
        routing = " ".join(self.skill.split())
        for contract in (
            "Keep this implementation agent open",
            "Create at most one verifier per used capability",
            "reuse it for affected reruns",
            "Keep it open for meaningful delta review",
            "same reviewer",
            "call `close_agent`",
            "so descendants close as well",
            "Under V2, where no true close operation is exposed",
            "require every phase agent to be `completed`",
            "Never scan for or kill unrelated processes",
        ):
            self.assertIn(contract, routing)
        self.assertLess(
            routing.index("call `close_agent`"),
            routing.index("Have the root commit the accepted phase"),
        )
        self.assertIn(
            "close that agent and its descendants before continuing", routing
        )
        self.assertIn(
            "Close planner and plan reviewer after the bundle is accepted", routing
        )

        commit_skill = (
            ROOT / "codex/skills/orchestra-phase-commit/SKILL.md"
        ).read_text()
        for excluded in ("close_agent", "browser_route", "kill unrelated"):
            self.assertNotIn(excluded, commit_skill)

    def test_test_permissions_respect_active_choice_and_guardian_default(
        self,
    ) -> None:
        runtime = (self.references / "runtime_verification.md").read_text()
        worker = self.instructions("orchestra_implementation_worker")
        sources = (
            runtime,
            worker,
            self.skill,
            (ROOT / "docs/WORKFLOW.md").read_text(),
            (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
        )
        for reference_doc in ("AGENTS.md", "VISION.md", "docs/ARCHITECTURE.md"):
            reference = " ".join((ROOT / reference_doc).read_text().split())
            self.assertIn("Guardian", reference, reference_doc)
            self.assertIn(
                "active permission choice for the task, host, or launcher",
                reference,
                reference_doc,
            )
            self.assertNotIn("danger-full-access", reference, reference_doc)
        for text in sources:
            normalized = " ".join(text.split())
            self.assertIn(
                "synchronizes Guardian (`:workspace`, `on-request`, and Auto-review) "
                "as the default",
                normalized,
            )
            self.assertIn(
                "active permission choice for the task, host, or launcher",
                normalized,
            )
            self.assertIn(
                "never changes it or blocks execution solely because it differs",
                normalized,
            )
            self.assertIn("When Guardian is active", normalized)
            self.assertIn("Auto-review", normalized)
            self.assertIn("protected boundary", normalized)
            self.assertIn(
                "one narrow escalation for automatic review",
                normalized,
            )
            self.assertIn("manual approvals", normalized)
            self.assertIn("Full Access", normalized)
            self.assertIn("Never retry a denial", normalized)
            self.assertIn("CLI-usage failures", normalized)
            self.assertNotIn("danger-full-access", normalized)

    def test_phase_resource_ownership_is_transient_and_bounded(self) -> None:
        verifier = self.instructions("orchestra_verifier")
        worker = self.instructions("orchestra_implementation_worker")
        analyst = self.instructions("orchestra_analyst")
        reviewer = self.instructions("orchestra_reviewer")
        conduct = " ".join(self.shared_conduct.split())
        for contract in (
            "Track every task-owned resource you create",
            "local servers, managed or detached processes",
            "exec or PTY terminal sessions",
            "in-app Browser tabs",
            "Chrome connector tabs",
            "Browser tabs are stricter than other resources",
            "never claim or reuse a user tab or a prior run's tab",
            "Browser tabs are never eligible for phase retention",
            "never means closing the browser application",
            "always attempt cleanup before a final, failed, or blocked handoff",
            "Never rely on agent completion or an agent-close operation",
            "Never scan globally for processes",
            "close unrelated tabs, windows, authenticated sessions, terminals, or user state",
            "Analysts and reviewers retain no resources across a handoff",
            "Implementers and verifiers also clean by default",
            "packet explicitly authorizes that exact resource category",
            "`cleanup: pass | partial | blocked`",
            "`retained_resources: none`",
            "type, exact handle, owner, and authorized reason",
            "Do not persist cleanup fields or resource handles in semantic artifacts",
            "Do not create a resource registry, hook, wrapper, or persisted cleanup state",
        ):
            self.assertIn(contract, conduct)

        for name in PROFILE_NAMES:
            profile = self.instructions(name)
            self.assertIn("shared_conduct.md", profile, name)
            self.assertIn("owned-resource cleanup", profile, name)

        for profile in (analyst, worker, reviewer, verifier):
            self.assertNotIn("When the root requests phase teardown", profile)
            self.assertNotIn("phase-teardown request", profile)

        for profile in (verifier, worker):
            normalized = " ".join(profile.split())
            self.assertIn(
                "Availability preserves agent context, not tool resources",
                normalized,
            )
            self.assertIn("recreate", normalized)
            self.assertIn("outside the reusable report", normalized)

        playbooks = (
            self.references / "frontend_implementation.md",
            self.references / "browser_acceptance.md",
            self.references / "runtime_verification.md",
        )
        for path in playbooks:
            playbook = " ".join(path.read_text().split())
            self.assertIn("before every handoff", playbook, path.name)
            self.assertNotIn("phase-teardown request", playbook, path.name)
        runtime_playbook = " ".join(
            (self.references / "runtime_verification.md").read_text().split()
        )
        self.assertIn("packet explicitly authorizes", runtime_playbook)
        browser_playbook = " ".join(
            (self.references / "browser_acceptance.md").read_text().split()
        )
        self.assertIn(
            "Never retain the task tab or another owned resource across a browser-acceptance handoff",
            browser_playbook,
        )
        self.assertIn("open a fresh one for every rerun", browser_playbook)
        self.assertIn("return `retained_resources: none`", browser_playbook)

        self.assertIn(
            "Repository-context, web-research, architecture-analysis, and "
            "difficult-debugging analysts are one-shot agents",
            analyst,
        )
        self.assertIn(
            "technical-planning analyst remains available only through a "
            "dispatched plan-review",
            analyst,
        )
        normalized_skill = " ".join(self.skill.split())
        for contract in (
            "Keep agent and resource handles only in root memory",
            "material start/final/blocker activities",
            "never packets, resource handles",
            "Do not contact an agent that reported `cleanup: pass` with "
            "`retained_resources: none`",
            "one parallel cleanup-only follow-up",
            "only to owners that reported authorized retained resources, "
            "`partial`, or `blocked`",
            "root-owned resource or an exact safely addressable handle",
            "Consume `cleanup` and `retained_resources` with every stable handoff",
            "A `cleanup: pass` result with no retained resources causes no follow-up",
            "A `blocked` cleanup prevents downstream dispatch",
            "one cleanup-only follow-up to the same owner",
            "block the phase instead of retry-looping",
        ):
            self.assertIn(contract, normalized_skill)
        self.assertIn(
            "an unclosed source-read-only task tab is partial cleanup",
            self.skill.lower(),
        )

        protocol_sources = (
            self.skill,
            (ROOT / "docs/WORKFLOW.md").read_text(),
            (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text(),
        )
        for source in protocol_sources:
            normalized = " ".join(source.lower().split())
            self.assertIn("under v1", normalized)
            self.assertIn("close_agent", normalized)
            self.assertIn("under v2", normalized)
            self.assertIn("no true close operation", normalized)
            self.assertIn("completed", normalized)
            self.assertIn("no active descendant", normalized)

    def test_commit_and_pr_observation_remain_root_owned(self) -> None:
        commit_skill = (
            ROOT / "codex/skills/orchestra-phase-commit/SKILL.md"
        ).read_text()
        review_skill = (ROOT / "codex/skills/orchestra-pr-review/SKILL.md").read_text()
        self.assertIn("commit_phase.py", commit_skill)
        self.assertIn("without a committer profile or capability", commit_skill)
        self.assertIn("root directly run", review_skill)
        self.assertIn("pr.py", review_skill)
        self.assertIn("observe", review_skill)
        self.assertIn("tiers.<tier>.independent_review", review_skill)
        self.assertIn(
            "exact approved overview and relevant phase identifiers",
            review_skill,
        )
        self.assertIn("accepted identifiers without restating findings", review_skill)
        self.assertIn("same implementation owner", review_skill)
        for retired in ("phase_committer", "pr_polling_specialist", "pr_triage_specialist"):
            self.assertNotIn(retired, commit_skill + review_skill + self.skill)

    def test_commit_path_rejects_parallel_git_and_state_machinery(self) -> None:
        helper = (ROOT / "codex/scripts/commit_phase.py").read_text()
        commit_skill = (
            ROOT / "codex/skills/orchestra-phase-commit/SKILL.md"
        ).read_text()
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
        self.assertIn("alternate index", commit_skill)
        self.assertIn("Do not resolve an assignment", commit_skill)

    def test_extra_review_and_debugging_are_proportional(self) -> None:
        routing = self.skill.lower()
        for field in (
            "measurable risk",
            "supporting evidence",
            "affected area",
            "independently detectable defect class",
        ):
            self.assertIn(field, routing)
        self.assertIn("complexity alone is insufficient", routing)
        self.assertIn("records the reason in review evidence", self.skill)
        debugging = (self.references / "difficult_debugging.md").read_text()
        self.assertIn("escalation trigger fired", debugging)
        self.assertIn("the same causal failure repeated", debugging)
        self.assertIn("correction cycles demonstrably failed to converge", debugging)
        self.assertNotIn(
            "two fix-review rounds with distinct legitimate findings",
            debugging,
        )
        self.assertIn("same implementation owner", debugging)
        self.assertIn("or the whole workflow", debugging)

    def test_standard_requires_approval_and_delivery_authority_stays_separate(self) -> None:
        self.assertIn("request explicit user approval", self.skill)
        self.assertIn("Stop before implementation", self.skill)
        self.assertIn(
            "write `plan.md` as the approved overview and exact phase manifest",
            self.skill,
        )
        self.assertIn("delivery authority remains separate", self.skill)
        self.assertIn("merge without separate authority", self.skill)
        self.assertIn("orchestra-delivery-policy", self.skill)

    def test_user_selects_and_can_transition_tier_without_restart(self) -> None:
        routing = " ".join(self.skill.split())
        for contract in (
            "The user may still choose `luna` or `standard` after a higher recommendation",
            "never waives separate authority gates",
            "active tier may change among those available in the selected mode",
            "Never change tier unilaterally",
            "Do not revert, restart, or create a transition commit",
            "replacement worker owns the remaining phase",
            "Preserve evidence for the unchanged revision",
        ):
            self.assertIn(contract, routing)
        for model_contract in (
            "run `python3 \"${CODEX_HOME:-$HOME/.codex}/orchestra/scripts/session_model.py\"` once",
            "immutable lookup mode for the task",
            "current session helper returns the same mode",
            "Changing `native` and `external` requires a new task",
        ):
            self.assertIn(model_contract, routing)
        pr_review = (
            ROOT / "codex/skills/orchestra-pr-review/SKILL.md"
        ).read_text()
        for review_contract in (
            "run the installed `session_model.py`",
            "require its `modelconfig` to match the plan",
            "a mismatch blocks review dispatch",
        ):
            self.assertIn(review_contract, pr_review)

    def test_planning_requires_feasibility_and_execution_readiness(self) -> None:
        context = (self.references / "repository_context.md").read_text()
        planning = (self.references / "technical_planning.md").read_text()
        combined = " ".join((context + planning).split())
        for contract in (
            "persisted types",
            "schema versions",
            "transactions",
            "downstream consumers",
            "fixtures",
            "canonical verification commands",
            "test-data provenance",
            "generated or cache paths",
            "feasibility-determining fact",
        ):
            self.assertIn(contract, combined)

    def test_review_browser_and_confirmation_canaries_are_explicit(self) -> None:
        reviewer = self.instructions("orchestra_reviewer")
        browser = (self.references / "browser_acceptance.md").read_text()
        routing = " ".join(self.skill.split())
        normalized_browser = " ".join(browser.split())
        self.assertIn("complete the entire bounded target", reviewer)
        self.assertIn("all known material findings together", reviewer)
        self.assertIn("canary for a previously failing tool", normalized_browser)
        self.assertIn(
            "Do not veto or substitute a user-selected route",
            normalized_browser,
        )
        self.assertIn("Do not ask for the same confirmation twice", routing)
        self.assertIn(
            "Distinct legitimate findings alone are not an escalation trigger",
            routing,
        )

    def test_blocking_user_questions_use_selector_or_single_text_fallback(
        self,
    ) -> None:
        source_agents = " ".join((ROOT / "AGENTS.md").read_text().split())
        self.assertIn("`request_user_input`", source_agents)
        runtime_agents = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        workflow = (ROOT / "docs/WORKFLOW.md").read_text()
        for guidance in (runtime_agents, workflow):
            normalized = " ".join(guidance.split())
            self.assertIn("`request_user_input`", normalized)
            self.assertIn("without `autoResolutionMs`", normalized)
            self.assertIn("when the tool is available", normalized)
            self.assertIn(
                "not available or does not return a usable selection",
                normalized,
            )
            self.assertIn("one concise plain-text question", normalized)
            self.assertRegex(normalized, r"(Do not retry|without retrying) the selector")
            self.assertIn("explicitly informational, non-blocking", normalized)
            self.assertIn(
                "does not change command, test, or `wait_agent` timeouts",
                normalized.lower(),
            )


if __name__ == "__main__":
    unittest.main()
