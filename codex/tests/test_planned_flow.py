"""Static contracts for standard and critical Orchestra routing."""

from __future__ import annotations

from pathlib import Path
import re
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
PROFILE_NAMES = {
    "repo_context_explorer",
    "planner",
    "plan_scope_auditor",
    "implementation_worker",
    "reviewer",
    "debugging_investigator",
    "web_researcher",
    "browser_acceptance_tester",
    "phase_committer",
    "pr_polling_specialist",
    "pr_triage_specialist",
}


class PlannedFlowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "codex/skills/orchestra/SKILL.md").read_text()
        self.profiles = {
            path.stem: tomllib.loads(path.read_text())
            for path in sorted((ROOT / "codex/agents").glob("*.toml"))
        }
        self.roles = tomllib.loads(
            (ROOT / "codex/config/roles.toml").read_text()
        )["tiers"]

    def instructions(self, name: str) -> str:
        return self.profiles[name]["developer_instructions"]

    def assert_assignments(
        self, tier: str, names: set[str], model: str, effort: str
    ) -> None:
        for name in names:
            self.assertEqual(
                self.roles[tier][name],
                {"model": model, "reasoning_effort": effort},
            )

    def test_eleven_profiles_have_unique_structural_contracts(self) -> None:
        self.assertEqual(set(self.profiles), PROFILE_NAMES)
        declared_names = {profile["name"] for profile in self.profiles.values()}
        self.assertEqual(declared_names, PROFILE_NAMES)
        for name, profile in self.profiles.items():
            self.assertEqual(
                set(profile), {"name", "description", "developer_instructions"}
            )
            self.assertNotIn("model", profile["developer_instructions"].lower())
            for heading in ("## Input", "## Output", "## Stop conditions"):
                self.assertIn(heading, profile["developer_instructions"], name)

    def test_roles_match_current_standard_and_critical_matrix(self) -> None:
        standard_roles = {
            "planner",
            "plan_scope_auditor",
            "implementation_worker",
            "reviewer",
            "debugging_investigator",
            "repo_context_explorer",
            "web_researcher",
            "browser_acceptance_tester",
            "phase_committer",
            "pr_polling_specialist",
            "pr_triage_specialist",
        }
        critical_roles = standard_roles | {"reviewer_second_pass"}
        self.assertEqual(set(self.roles), {"light", "standard", "critical"})
        self.assertEqual(set(self.roles["standard"]), standard_roles)
        self.assertEqual(set(self.roles["critical"]), critical_roles)
        self.assertNotIn("orchestrator", self.roles["standard"])
        self.assertNotIn("orchestrator", self.roles["critical"])

        self.assert_assignments(
            "standard",
            {"planner", "plan_scope_auditor"},
            "gpt-5.6-sol",
            "high",
        )
        self.assert_assignments(
            "standard",
            {
                "implementation_worker",
                "reviewer",
                "debugging_investigator",
                "pr_triage_specialist",
            },
            "gpt-5.6-luna",
            "max",
        )
        self.assert_assignments(
            "standard",
            {"pr_polling_specialist"},
            "gpt-5.6-luna",
            "high",
        )
        self.assert_assignments(
            "standard",
            {
                "repo_context_explorer",
                "web_researcher",
                "browser_acceptance_tester",
                "phase_committer",
            },
            "gpt-5.6-luna",
            "xhigh",
        )
        self.assert_assignments(
            "critical",
            {"planner", "plan_scope_auditor", "reviewer_second_pass"},
            "gpt-5.6-sol",
            "xhigh",
        )
        self.assert_assignments(
            "critical",
            {
                "implementation_worker",
                "reviewer",
                "debugging_investigator",
                "pr_triage_specialist",
            },
            "gpt-5.6-sol",
            "high",
        )
        self.assert_assignments(
            "critical",
            {
                "repo_context_explorer",
                "web_researcher",
                "phase_committer",
                "pr_polling_specialist",
            },
            "gpt-5.6-luna",
            "high",
        )
        self.assert_assignments(
            "critical",
            {"browser_acceptance_tester"},
            "gpt-5.6-luna",
            "xhigh",
        )

    def test_standard_stops_for_user_approval_and_limits_authority(self) -> None:
        self.assertIn("request explicit user approval", self.skill)
        self.assertIn(
            "Stop before any standard or critical implementation until approval",
            self.skill,
        )
        self.assertIn("successful phase commits only", self.skill)
        for action in ("merge", "delivery", "release", "deployment"):
            self.assertIn(action, self.skill)

    def test_critical_audit_and_second_review_are_proportional(self) -> None:
        auditor_description = self.profiles["plan_scope_auditor"]["description"].lower()
        self.assertIn("named measurable risk", auditor_description)
        self.assertNotIn("complex", auditor_description)
        auditor = self.instructions("plan_scope_auditor").lower()
        routing = self.skill.lower()
        for field in (
            "measurable risk",
            "supporting evidence",
            "affected area",
            "defect class",
        ):
            self.assertIn(field, auditor)
            self.assertIn(field, routing)
        self.assertIn("architectural complexity alone", auditor)
        self.assertIn("architectural complexity alone", routing)
        self.assertIn("report only material", auditor)
        self.assertIn("do not rewrite or approve the plan", auditor)
        self.assertIn("reviewer_second_pass", routing)
        self.assertIn("reuse `reviewer.toml`", routing)

    def test_root_keeps_authority_and_context_stays_ephemeral(self) -> None:
        for responsibility in (
            "problem framing",
            "tier selection",
            "user alignment",
            "routing",
            "compact synthesis",
            "blocker resolution",
            "ordinary reversible in-scope decisions",
            "final technical judgment",
        ):
            self.assertIn(responsibility, self.skill)
        self.assertIn("current session configuration", self.skill)
        self.assertIn("selected outside Orchestra", self.skill)
        self.assertNotIn("planned root assignment", self.skill)
        self.assertIn("compact packet in memory", self.skill)
        self.assertIn("only changed context deltas", self.skill)
        self.assertIn("Do not write packets, workflow state", self.skill)
        self.assertIn("never restart the whole workflow", self.skill)
        self.assertIn("same implementation owner", self.skill)

    def test_specialists_report_without_spawning_or_orchestrating(self) -> None:
        for name in PROFILE_NAMES - {"implementation_worker", "reviewer", "phase_committer"}:
            instructions = self.instructions(name)
            self.assertRegex(
                instructions.lower(), re.compile(r"do not [^.\n]*spawn agents"), name
            )
            self.assertRegex(
                instructions.lower(),
                re.compile(r"do not [^.\n]*act as the orchestrator"),
                name,
            )
        self.assertIn("Remain read-only", self.instructions("repo_context_explorer"))
        self.assertIn("Remain read-only", self.instructions("planner"))
        self.assertIn("Remain read-only", self.instructions("plan_scope_auditor"))
        self.assertIn("Remain read-only", self.instructions("debugging_investigator"))
        self.assertIn("Remain read-only", self.instructions("web_researcher"))
        self.assertIn("Remain read-only", self.instructions("browser_acceptance_tester"))

    def test_explorer_is_bounded_evidence_and_planner_never_edits(self) -> None:
        explorer = self.instructions("repo_context_explorer")
        self.assertIn("only the repository domains and questions", explorer)
        self.assertIn("Return bounded evidence", explorer)
        self.assertIn("Separate observed facts from inferences", explorer)
        planner = self.instructions("planner")
        self.assertIn("smallest executable plan", planner)
        self.assertIn("independently reviewable phases", planner)
        self.assertIn("do not edit, implement, approve", planner)

    def test_debugger_is_local_diagnostic_after_repeated_failure(self) -> None:
        debugger = self.instructions("debugging_investigator")
        self.assertIn("after the same failure repeats", debugger)
        self.assertIn("do not implement fixes", debugger.lower())
        self.assertIn("root-cause conclusion with evidence", debugger)
        self.assertIn("next local corrective action", debugger)
        self.assertIn("never restart the whole workflow", self.skill)

    def test_web_research_is_narrow_current_and_cited(self) -> None:
        researcher = self.instructions("web_researcher")
        self.assertIn("time-sensitive external questions", researcher)
        self.assertIn("primary evidence", researcher)
        self.assertIn("direct primary-source citations", researcher)
        self.assertIn("Do not fill gaps from memory", researcher)

    def test_browser_acceptance_uses_computer_use_and_chrome_only(self) -> None:
        browser = self.instructions("browser_acceptance_tester")
        for contract in (
            "Use Computer Use to operate Chrome",
            "Open a new Chrome tab",
            "preserve every unrelated tab and session",
            "Never use Codex's in-app Browser",
            "reproducible evidence",
            "do not edit files",
        ):
            self.assertIn(contract, browser)
        self.assertIn("without switching to the in-app Browser", browser)

    def test_delivery_routing_starts_only_after_reviewed_commits(self) -> None:
        self.assertIn("After all reviewed, verified phase commits", self.skill)
        self.assertIn("orchestra-delivery-policy", self.skill)
        self.assertIn("Do not choose a lane before that point", self.skill)
        self.assertIn("merge without separate authority", self.skill)
        self.assertIn("deploy, release, synchronize, or install", self.skill)

    def test_ui_and_runtime_expose_all_tier_routing(self) -> None:
        ui = (ROOT / "codex/skills/orchestra/agents/openai.yaml").read_text()
        self.assertIn("Route proportional reviewed software changes", ui)
        self.assertIn("$orchestra", ui)
        runtime = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        self.assertIn("light, standard, and critical changes", runtime)
        self.assertIn("Require explicit user approval", runtime)
        self.assertIn("not merge, delivery, deployment, or release", runtime)
        self.assertIn("orchestra-delivery-policy", runtime)


if __name__ == "__main__":
    unittest.main()
