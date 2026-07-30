"""Static and isolated contracts for composable planned Orchestra work."""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
PROFILE_NAMES = {"orchestra_analyst", "orchestra_implementation_worker", "orchestra_reviewer", "orchestra_verifier"}
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
        for roles in self.role_matrices.values():
            self.assertEqual(set(roles), {"standard", "critical"})
            for tier in ("standard", "critical"):
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
            "orchestra_implementation_worker": ("implemented", "blocked", "implementation-report", "changed paths", "tests changed", "verification commands", "owned temporary resources", "remaining risks"),
            "orchestra_reviewer": ("accepted", "findings", "blocked", "review target", "stable identifier", "verification or authority gaps", "rejected pr feedback"),
            "orchestra_verifier": ("passed", "failed", "blocked", "verification-report", "commands or interaction steps", "observed output or behavior", "evidence references", "environment details", "owned temporary resources"),
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
        architecture = " ".join((ROOT / "docs/ARCHITECTURE.md").read_text().split())
        for contract in (
            "coordination.py",
            "task create",
            "artifact put",
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
            "worktree cleanup may make its artifact locators unavailable",
        ):
            self.assertIn(contract.lower(), workflow.lower())
        for contract in (
            "tasks, material agent activities, and artifact locators",
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
        self.assertIn("--kind repository-context", context)
        self.assertIn("--kind plan-overview", planning)
        self.assertIn("--kind plan-phase --phase <number>", planning)
        self.assertIn("complete replacement", planning)

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
            "trivial single-phase standard plan may skip review",
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

    def test_new_formal_task_creates_portable_worktree_before_discovery(
        self,
    ) -> None:
        isolation = self.skill.index("## Create the isolated task worktree")
        repository_dispatch = self.skill.index(
            "dispatch `repository_context` to an `orchestra_analyst`"
        )
        self.assertLess(isolation, repository_dispatch)
        normalized = " ".join(self.skill.split())
        for invariant in (
            "`${CODEX_HOME:-$HOME/.codex}/orchestra/worktree-root`",
            "`$HOME/.orchestra/worktrees`",
            "`<worktree-root>/<repository>/<task-slug>[-N]` checkout path",
            "write and remove one temporary canary",
            "Create the selected checkout with `git worktree add`",
            "Do not use an elevated edit path",
            "Never implement in, switch, or reuse the source checkout",
            "Adopted committed work starts at its source HEAD",
            "adopt_worktree.py",
            "same live preapproval task",
            "checkout path, branch, base, and HEAD",
            "remove only proven-clean resources",
            "completion without an artificial commit",
        ):
            self.assertIn(invariant, normalized)

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
        worktree = normalized.index("## Create the isolated task worktree")
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
                "model": "cursor/composer-2.5-fast",
                "reasoning_effort": "high",
            },
        )
        normalized = " ".join(self.skill.split())
        assigned_first = normalized.index("Always attempt the installed assignment first")
        fallback = normalized.index("Luna and reasoning `high`")
        self.assertLess(assigned_first, fallback)
        for contract in (
            "Only when a `repository_context` spawn is rejected before execution",
            "internal subagent runtime does not support the assigned model",
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

    def test_browser_routing_prefers_in_app_and_honors_explicit_selection(
        self,
    ) -> None:
        browser = (self.references / "browser_acceptance.md").read_text()
        frontend = (self.references / "frontend_implementation.md").read_text()
        for contract in (
            "Require `browser_route: auto | in_app | chrome`",
            "explicitly select Codex's in-app Browser first",
            "fall back to Computer Use with Chrome only",
            "remains fixed unless that instruction also authorizes fallback",
            "functional failure, application timeout, or selector problem never triggers fallback",
            "repeat the complete scenario",
            "Do not substitute the Chrome browser plugin",
            "preserve all unrelated tabs",
        ):
            self.assertIn(contract, browser)
        normalized_frontend = " ".join(frontend.split())
        for contract in (
            "`browser_route: auto | in_app | chrome`",
            "Codex's in-app Browser first",
            "Computer Use with Chrome",
            "never triggers fallback",
            "repeat the complete visual scenario",
            "separate from independent acceptance",
        ):
            self.assertIn(contract, normalized_frontend)
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
            "so their descendants close as well",
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

    def test_failed_tests_use_selective_exact_elevation(self) -> None:
        runtime = (self.references / "runtime_verification.md").read_text()
        worker = self.instructions("orchestra_implementation_worker")
        for text in (runtime, worker, self.skill):
            normalized = " ".join(text.split())
            self.assertIn("Classify a failure from", normalized)
            self.assertIn("sandbox", normalized)
            self.assertIn("sockets", normalized)
            self.assertIn("CLI-usage failures", normalized)
            self.assertIn("one exact elevated retry", normalized)
        self.assertNotIn("any failed test", self.skill)

    def test_phase_resource_ownership_is_transient_and_bounded(self) -> None:
        verifier = self.instructions("orchestra_verifier")
        worker = self.instructions("orchestra_implementation_worker")
        analyst = self.instructions("orchestra_analyst")
        for profile in (verifier, worker):
            for contract in (
                "Retain only explicitly permitted temporary processes",
                "phase teardown",
                "owned resources",
            ):
                self.assertIn(contract, profile)
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
        ):
            self.assertIn(contract, normalized_skill)
        self.assertIn(
            "an unclosed source-read-only task tab is partial cleanup",
            self.skill.lower(),
        )

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
            "The user may choose `standard` after a `critical` recommendation",
            "never waives separate authority gates",
            "active tier may change in either direction",
            "Never change tier unilaterally",
            "Do not revert, restart, or create a transition commit",
            "replacement worker owns the remaining phase",
            "Preserve evidence for the unchanged revision",
        ):
            self.assertIn(contract, routing)

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

    def test_blocking_user_questions_never_auto_resolve(self) -> None:
        source_agents = (ROOT / "AGENTS.md").read_text()
        runtime_agents = (ROOT / "codex/runtime/AGENTS.orchestra.md").read_text()
        for guidance in (source_agents, runtime_agents):
            normalized = " ".join(guidance.split())
            self.assertIn(
                "required to continue, call `request_user_input` without "
                "`autoResolutionMs`",
                normalized,
            )
            self.assertIn("explicitly informational, non-blocking", normalized)
            self.assertIn(
                "does not change command, test, or `wait_agent` timeouts",
                normalized,
            )


if __name__ == "__main__":
    unittest.main()
