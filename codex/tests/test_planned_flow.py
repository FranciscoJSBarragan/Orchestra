"""Static and isolated contracts for composable planned Orchestra work."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
PROFILE_NAMES = {"analyst", "implementation_worker", "reviewer", "verifier"}
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
        self.roles = tomllib.loads(
            (ROOT / "codex/config/roles.toml").read_text()
        )["tiers"]
        self.profiles = {
            path.stem: tomllib.loads(path.read_text())
            for path in (ROOT / "codex/agents").glob("*.toml")
        }
        self.references = ROOT / "codex/skills/orchestra/references"

    def instructions(self, name: str) -> str:
        return self.profiles[name]["developer_instructions"]

    def output_instructions(self, name: str) -> str:
        instructions = self.instructions(name)
        return instructions.split("## Output", 1)[1].split("## Stop conditions", 1)[0]

    def input_instructions(self, name: str) -> str:
        instructions = self.instructions(name)
        return instructions.split("## Input", 1)[1].split("## Output", 1)[0]

    def test_exact_four_profiles_are_behavior_only(self) -> None:
        self.assertEqual(set(self.profiles), PROFILE_NAMES)
        self.assertEqual(
            {profile["name"] for profile in self.profiles.values()}, PROFILE_NAMES
        )
        for name, profile in self.profiles.items():
            self.assertEqual(
                set(profile), {"name", "description", "developer_instructions"}
            )
            self.assertTrue(profile["description"].strip())
            for heading in ("## Input", "## Output", "## Stop conditions"):
                self.assertIn(heading, profile["developer_instructions"], name)
            self.assertNotIn("gpt-5.", profile["developer_instructions"].lower())

    def test_capability_inventory_and_profile_mapping_are_exact(self) -> None:
        light = {
            "general_implementation": "implementation_worker",
            "independent_review": "reviewer",
            "runtime_verification": "verifier",
        }
        standard = {
            "repository_context": "analyst",
            "web_research": "analyst",
            "technical_planning": "analyst",
            "architecture_analysis": "analyst",
            "difficult_debugging": "analyst",
            "general_implementation": "implementation_worker",
            "frontend_implementation": "implementation_worker",
            "independent_review": "reviewer",
            "browser_acceptance": "verifier",
            "runtime_verification": "verifier",
        }
        self.assertEqual(set(self.roles), {"light", "standard", "critical"})
        self.assertEqual(
            {name: value["profile"] for name, value in self.roles["light"].items()},
            light,
        )
        for tier in ("standard", "critical"):
            self.assertEqual(
                {name: value["profile"] for name, value in self.roles[tier].items()},
                standard,
            )
        for assignments in self.roles.values():
            for assignment in assignments.values():
                self.assertEqual(
                    set(assignment), {"profile", "model", "reasoning_effort"}
                )
                self.assertNotEqual(
                    (assignment["model"], assignment["reasoning_effort"]),
                    ("gpt-5.6-sol", "xhigh"),
                )
                self.assertNotIn(assignment["profile"], {"root", "orchestrator"})

    def test_seven_playbooks_and_shared_architecture_reference_are_composed(self) -> None:
        expected = {f"{name}.md" for name in PLAYBOOK_NAMES} | {
            "architecture_guidance.md"
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

    def test_profile_responsibilities_are_bounded(self) -> None:
        analyst = self.instructions("analyst")
        self.assertIn("Perform exactly one named analysis capability", analyst)
        self.assertIn("Remain read-only with respect to repository source", analyst)
        worker = self.instructions("implementation_worker")
        self.assertIn("approved paths and accepted fixes", worker)
        self.assertIn("same implementation owner", self.skill)
        reviewer = self.instructions("reviewer")
        for target in ("plan", "architecture", "code revision", "PR feedback"):
            self.assertIn(target, reviewer)
        self.assertIn("Remain read-only and report-only", reviewer)
        verifier = self.instructions("verifier")
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
            "analyst": ("evidence", "planned", "diagnosed", "blocked", "capability name", "observed facts", "unresolved questions", "source references"),
            "implementation_worker": ("implemented", "blocked", "capability name", "changed paths", "implementation notes", "tests changed", "verification commands", "remaining risks"),
            "reviewer": ("accepted", "findings", "blocked", "review target", "material findings", "verification or authority gaps", "rejected pr feedback"),
            "verifier": ("passed", "failed", "blocked", "capability name", "commands or interaction steps", "observed output or behavior", "evidence references", "environment details"),
        }
        for name in PROFILE_NAMES:
            output = self.output_instructions(name).lower().strip()
            first_sentence = output.split(".", 1)[0]
            self.assertTrue(output.startswith("return the outcome or status"), name)
            self.assertIn(" first, then ", first_sentence, name)
            for omission in (
                "packet replay",
                "praise",
                "unchanged context",
                "duplicate evidence",
            ):
                self.assertIn(omission, output, name)
            for term in material_terms:
                self.assertIn(term, output, name)
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
            self.assertIn("redact secrets", output, name)
            self.assertIn("safe category or locator", output, name)

    def test_worker_minimality_requires_focused_comprehension_and_supported_cause(
        self,
    ) -> None:
        worker = self.instructions("implementation_worker").lower()
        responsibility = worker.split("## input", 1)[0]
        worker_input = self.input_instructions("implementation_worker").lower()
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
            "approved objective",
            "known decisions and context delta",
            "allowed paths",
            "acceptance criteria",
            "verification",
            "exclusions",
            "stop conditions",
            "references",
            "revision identity",
        ):
            self.assertIn(packet_field, worker_input)

    def test_reviewer_complexity_is_material_not_metric_scoring(self) -> None:
        reviewer = self.instructions("reviewer").lower()
        for requirement in (
            "unsupported consumer, requirement, or reproducible risk",
            "recommend deletion, an existing primitive, or a smaller direct implementation",
            "line count, file count, abstraction count, or unfamiliarity alone",
            "severity, causal rationale, applicable locator, and correction rationale",
        ):
            self.assertIn(requirement, reviewer)

    def test_compact_context_requests_lossless_returns_without_hard_caps(self) -> None:
        self.assertIn("Request outcome-first, lossless structured returns", self.skill)
        self.assertIn(
            "never impose a token, line, file, finding, test, or explanation cap",
            self.skill,
        )
        architecture = (ROOT / "docs/ARCHITECTURE.md").read_text().lower()
        for invariant in (
            "outcome-first output status",
            "dirty worktree or diff state",
            "focused read-only inspection",
            "supported root cause at the causal boundary",
            "reproducible risk",
        ):
            self.assertIn(invariant, architecture)
        self.assertIn("relevant references and revision identity", self.skill)

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
                result = subprocess.run(
                    ["git", "-C", str(worktree), "rev-parse", "--git-path", "orchestra/plan.md"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                path = Path(result.stdout.strip())
                return path if path.is_absolute() else worktree / path

            base_plan = plan_path(base).resolve()
            linked_plan = plan_path(linked).resolve()
            self.assertNotEqual(base_plan, linked_plan)
            self.assertIn(".git/orchestra/plan.md", base_plan.as_posix())
            self.assertIn(".git/worktrees/linked/orchestra/plan.md", linked_plan.as_posix())

        self.assertIn("git rev-parse --git-path orchestra/plan.md", self.skill)
        for status in ("`draft`", "`active`", "`blocked`", "`completed`"):
            self.assertIn(status, self.skill)
        self.assertIn("Only the root writes the plan", self.skill)
        self.assertIn("Git is authoritative", self.skill)

    def test_browser_acceptance_is_independent_and_chrome_only(self) -> None:
        browser = (self.references / "browser_acceptance.md").read_text()
        frontend = (self.references / "frontend_implementation.md").read_text()
        for contract in (
            "Use Computer Use with Chrome as the exclusive browser-control path",
            "Never invoke, probe, or fall back to Codex's in-app Browser",
            "Open a new Chrome tab",
            "preserve all unrelated tabs",
            "Return `blocked` when Computer Use or Chrome is unavailable",
        ):
            self.assertIn(contract, browser)
        self.assertIn("use Computer Use with Chrome only", frontend)
        self.assertIn("never invoke, probe, or fall back", frontend)
        self.assertIn("Never claim acceptance of your own work", frontend)
        self.assertIn("browser acceptance is an independent verifier dispatch", self.skill)

    def test_commit_and_pr_observation_are_direct_root_helper_operations(self) -> None:
        commit_skill = (
            ROOT / "codex/skills/orchestra-phase-commit/SKILL.md"
        ).read_text()
        review_skill = (ROOT / "codex/skills/orchestra-pr-review/SKILL.md").read_text()
        self.assertIn("root directly run", commit_skill)
        self.assertIn("commit_phase.py", commit_skill)
        self.assertIn("without a committer profile or capability", commit_skill)
        self.assertIn("root directly run", review_skill)
        self.assertIn("pr.py", review_skill)
        self.assertIn("observe", review_skill)
        self.assertIn("tiers.<tier>.independent_review", review_skill)
        self.assertIn("same implementation owner", review_skill)
        for retired in ("phase_committer", "pr_polling_specialist", "pr_triage_specialist"):
            self.assertNotIn(retired, commit_skill + review_skill + self.skill)

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
        debugging = (self.references / "difficult_debugging.md").read_text()
        self.assertIn("same local failure has demonstrably repeated", debugging)
        self.assertIn("blind retries have stopped", debugging)
        self.assertIn("same implementation owner", debugging)
        self.assertIn("or the whole workflow", debugging)

    def test_standard_requires_approval_and_delivery_authority_stays_separate(self) -> None:
        self.assertIn("request explicit user approval", self.skill)
        self.assertIn("Stop before implementation", self.skill)
        self.assertIn("draft` directly to `active", self.skill)
        self.assertIn("delivery authority remains separate", self.skill)
        self.assertIn("merge without separate authority", self.skill)
        self.assertIn("orchestra-delivery-policy", self.skill)

    def test_graphify_detection_is_root_owned_read_only_and_branch_complete(self) -> None:
        self.assertIn("the advisory Graphify lifecycle", self.skill)
        self.assertIn("root owns its lifecycle directly", self.skill)
        self.assertIn("Before standard or critical planning", self.skill)
        self.assertIn("`git ls-files graphify-out` contains exactly", self.skill)
        self.assertIn(
            "A missing command or incorrect tracked/ignored artifact boundary adds "
            "exactly one explicit approval-gated bootstrap phase",
            self.skill,
        )
        self.assertIn("`graphify hook status` exactly once", self.skill)
        self.assertIn("both required hooks installed", self.skill)
        self.assertIn("either required hook absent", self.skill)
        self.assertIn("one explicit approval-gated bootstrap phase", self.skill)
        self.assertIn("failed or uninterpretable status command", self.skill)
        self.assertIn("returns `partial`, uses source, and adds no bootstrap", self.skill)
        self.assertIn("no package install", self.skill)
        self.assertIn("treat the repository as a linked worktree", self.skill)
        self.assertIn("do not run `graphify hook status`", self.skill)
        self.assertIn("preserve existing common hooks", self.skill)
        self.assertIn("add bootstrap solely for hooks", self.skill)
        self.assertIn("whose hook step is skipped", self.skill)
        self.assertIn("continue read-only to the relevant Git delta", self.skill)
        self.assertIn("tracked graph fresh at HEAD", self.skill)
        self.assertIn("tell `repository_context` that it is usable", self.skill)
        self.assertIn(
            "When the command is missing, add the one bootstrap and use source "
            "because query cannot run",
            self.skill,
        )

    def test_graphify_hook_safety_and_freshness_precede_query(self) -> None:
        git_dir = self.skill.index("`git rev-parse --git-dir`")
        common_dir = self.skill.index("`git rev-parse --git-common-dir`")
        hook_status = self.skill.index("execute `graphify hook status` exactly once")
        core_hooks = self.skill.index("`git config --path --get core.hooksPath`")
        git_hooks = self.skill.index("`git rev-parse --git-path hooks`")
        delta = self.skill.index("inspect the relevant Git delta")
        query = self.skill.index("`graphify query` smoke check")
        self.assertLess(git_dir, hook_status)
        self.assertLess(common_dir, hook_status)
        self.assertLess(core_hooks, delta)
        self.assertLess(git_hooks, delta)
        self.assertLess(delta, query)
        self.assertIn("inside the tracked worktree", self.skill)
        self.assertIn("would modify a tracked hook", self.skill)
        self.assertIn("neither a wrapper nor an alternate hook mechanism", self.skill)
        self.assertIn("do not call hook status a second time", self.skill)
        self.assertIn("without bootstrap", self.skill)

    def test_graphify_bootstrap_order_and_final_update_are_bounded(self) -> None:
        ordered = (
            "`uv tool install --upgrade graphifyy`",
            "one complete initial `graphify .` build",
            "Enforce the exact three-output versioning",
            "Review, verify, and commit the initial snapshot",
            "Only after that commit succeeds",
            "run native `graphify hook install`",
            "For either branch, inspect Git delta and pending evidence",
        )
        positions = [self.skill.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("Never run `graphify codex install`", self.skill)
        self.assertIn("`graphify . --update` at most once", self.skill)
        self.assertIn("one separate graph-only commit", self.skill)
        self.assertIn("`nothing_to_commit`", self.skill)
        self.assertIn("does not prevent functional plan completion", self.skill)
        self.assertIn("including for linked worktrees", self.skill)

    def test_repository_context_uses_graph_only_from_root_packet(self) -> None:
        context = (self.references / "repository_context.md").read_text()
        self.assertIn(
            "only when the root packet explicitly says the current detection pass found "
            "the graph usable",
            context,
        )
        self.assertIn("verify every relevant claim against current source", context)
        self.assertIn("file existence alone never authorizes graph use", context)

    def test_runtime_consumes_graphify_without_expanding_public_inventory(self) -> None:
        runtime = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        self.assertIn("The root solely owns Graphify", runtime)
        self.assertIn(
            "A missing command or incorrect exact tracked/ignored boundary adds the one "
            "approval-gated bootstrap",
            runtime,
        )
        self.assertIn(
            "Before hook status, canonicalize `git rev-parse --git-dir` and "
            "`git rev-parse --git-common-dir`",
            runtime,
        )
        self.assertIn(
            "Only for a non-linked worktree with the command available, interpret "
            "exactly one "
            "`graphify hook status` result",
            runtime,
        )
        self.assertIn(
            "If they differ, record hook automation as `partial`", runtime
        )
        self.assertIn("preserve common hooks", runtime)
        self.assertIn(
            "do not run status, install, reinstall, or uninstall hooks", runtime
        )
        self.assertIn("bootstrap solely for hooks", runtime)
        self.assertIn("with its hook step skipped", runtime)
        self.assertIn("continues read-only through relevant Git delta", runtime)
        self.assertIn("tracked graph is fresh at HEAD", runtime)
        self.assertIn("tell `repository_context` it is usable", runtime)
        self.assertIn(
            "When the command is missing, add bootstrap and use source because "
            "query cannot run",
            runtime,
        )
        self.assertIn("valid installed hooks continue", runtime)
        self.assertIn("valid absence adds that bootstrap only when", runtime)
        self.assertIn("failure or uninterpretable output is `partial`", runtime)
        self.assertIn("tell `repository_context` it is usable", runtime)
        self.assertIn("Graphify never establishes correctness or policy", runtime)
        for forbidden in (
            "graphify.toml",
            "graphify.py",
            "graphify lifecycle profile",
            "graphify lifecycle capability",
        ):
            self.assertNotIn(forbidden, self.skill + runtime)

    def test_linked_worktree_hook_guard_is_consistent_across_consumers(self) -> None:
        consumers = {
            relative: (ROOT / relative).read_text()
            for relative in (
                "README.md",
                "AGENTS.md",
                "docs/WORKFLOW.md",
                "docs/ARCHITECTURE.md",
                "codex/skills/orchestra/SKILL.md",
                "codex/runtime/AGENTS.orchestra.md",
            )
        }
        for relative, text in consumers.items():
            self.assertIn("`git rev-parse --git-dir`", text, relative)
            self.assertIn("`git rev-parse --git-common-dir`", text, relative)
            self.assertIn("linked worktree", text, relative)
            self.assertIn("`partial`", text, relative)
            normalized = " ".join(text.lower().split())
            self.assertIn("git delta", normalized, relative)
            self.assertIn("pending", normalized, relative)
            self.assertIn("query", normalized, relative)
            self.assertIn("fresh", normalized, relative)
            self.assertIn("usable", normalized, relative)
        workflow = consumers["docs/WORKFLOW.md"]
        self.assertIn("do not call hook status", workflow)
        self.assertIn("do not call hook status, install, reinstall, or uninstall", workflow)
        self.assertIn(
            "this does not invalidate the graph",
            " ".join(workflow.lower().split()),
        )
        architecture = consumers["docs/ARCHITECTURE.md"]
        self.assertIn("skips status, installation,", architecture)
        self.assertIn("reinstallation, uninstall, wrappers, alternate hooks", architecture)
        self.assertIn("the manual final", architecture)
        self.assertIn("update remains the closure path", architecture)


if __name__ == "__main__":
    unittest.main()
