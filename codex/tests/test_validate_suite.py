"""Behavioral tests for the Orchestra conformance engine."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[2]


class ValidateSuiteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name) / "fixture"
        shutil.copytree(
            SOURCE_ROOT,
            self.root,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "dist"),
        )

    def run_validator(
        self,
        mode: str = "--quick",
        *,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(self.root / "codex/scripts/validate_suite.py"),
                mode,
            ],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_quick_succeeds_for_conforming_fixture(self) -> None:
        result = self.run_validator("--quick")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("quick conformance passed", result.stdout)

    def test_modular_entry_requires_its_runtime_and_reusable_recipe_route(self) -> None:
        skill = self.root / "codex/skills/orchestra-engineering/SKILL.md"
        skill.write_text(skill.read_text().replace(
            "(../orchestra-project-verification/SKILL.md)", "(../orchestra-role-verifier/SKILL.md)"
        ))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("modular-routing: orchestra-engineering must link ../orchestra-project-verification/SKILL.md", result.stdout)

    def test_parent_requires_root_transport_resource(self) -> None:
        skill = self.root / "codex/skills/orchestra-coordinate/SKILL.md"
        skill.write_text(skill.read_text().replace("(host-transports.md)", "(packet-example.md)"))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("modular-routing: orchestra-coordinate must link host-transports.md", result.stdout)

    def test_parent_cannot_be_made_implicitly_selected(self) -> None:
        metadata = self.root / "codex/skills/orchestra-coordinate/agents/openai.yaml"
        metadata.write_text(metadata.read_text().replace("false", "true"))
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("orchestra-coordinate must remain explicit-only", result.stdout)

    def test_repository_conventions_contract_requires_agent_hard_gate(self) -> None:
        conventions = self.root / ".agent/backend-testing.md"
        conventions.write_text(
            conventions.read_text(encoding="utf-8").replace(
                "python3 codex/scripts/validate_suite.py --full",
                "python3 -m pytest",
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            ".agent/backend-testing.md must name python3 "
            "codex/scripts/validate_suite.py --full",
            result.stdout,
        )

    def test_untracked_required_path_is_actionable(self) -> None:
        subprocess.run(
            ["git", "init"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "add", "-A"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "rm", "--cached", ".agent/backend-testing.md"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "required-path: untracked .agent/backend-testing.md",
            result.stdout,
        )

    def test_git_tracking_command_failure_is_actionable(self) -> None:
        (self.root / ".git").write_text(
            "gitdir: missing-git-directory\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "required-path: unable to verify tracked paths via git ls-files "
            "(exit ",
            result.stdout,
        )

    def test_missing_git_executable_is_actionable(self) -> None:
        (self.root / ".git").mkdir()
        env = os.environ.copy()
        env["PATH"] = ""
        result = self.run_validator(env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "required-path: unable to verify tracked paths via git ls-files "
            "(FileNotFoundError)",
            result.stdout,
        )

    def test_full_mode_runs_the_fixture_test_suite(self) -> None:
        test_file = self.root / "codex/tests/test_validate_suite.py"
        test_file.write_text(
            """from pathlib import Path
import unittest


class FullModeFixtureTest(unittest.TestCase):
    def test_full_mode_ran_this_test(self):
        Path(__file__).with_name("full-mode-ran").write_text("yes", encoding="utf-8")
""",
            encoding="utf-8",
        )
        result = self.run_validator("--full")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("full conformance passed", result.stdout)
        self.assertEqual(
            (self.root / "codex/tests/full-mode-ran").read_text(encoding="utf-8"),
            "yes",
        )

    def test_versioned_hook_executes_quick_validation(self) -> None:
        hook = self.root / ".githooks/pre-commit"
        result = subprocess.run(
            [str(hook)],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
            env={**os.environ, "PATH": os.environ.get("PATH", "")},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("quick conformance passed", result.stdout)

    def test_missing_required_file_is_actionable(self) -> None:
        (self.root / "VISION.md").unlink()
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required-path: missing VISION.md", result.stdout)

    def test_completed_migration_evidence_is_rejected(self) -> None:
        migration = self.root / "docs/MIGRATION.md"
        migration.write_text("completed evidence\n", encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("remove docs/MIGRATION.md", result.stdout)

    def test_prohibited_distribution_path_is_rejected(self) -> None:
        plugin_path = self.root / "codex/.codex-plugin/plugin.json"
        plugin_path.parent.mkdir(parents=True)
        plugin_path.write_text("{}\n", encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("generated manifest belongs in a package, not codex/.codex-plugin", result.stdout)

    def test_generic_configuration_and_plugin_named_paths_are_allowed(self) -> None:
        (self.root / "pyproject.toml").write_text(
            "[tool.example]\nvalue = true\n", encoding="utf-8"
        )
        (self.root / "setup.cfg").write_text("[example]\n", encoding="utf-8")
        notes = self.root / "tools/plugins/marketplace-notes.md"
        notes.parent.mkdir(parents=True)
        notes.write_text("ordinary project notes\n", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_roadmap_must_preserve_precedence_boundary(self) -> None:
        roadmap = self.root / "docs/ROADMAP.md"
        roadmap.write_text("# Orchestra Roadmap\n", encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("docs/ROADMAP.md is missing required boundary", result.stdout)

    def test_historical_product_narrative_is_rejected(self) -> None:
        readme = self.root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\nThis replaces the legacy product.\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("historical product replacement narrative", result.stdout)

    def test_functional_vocabulary_and_reflow_are_allowed(self) -> None:
        agents = self.root / "AGENTS.md"
        agents.write_text(
            agents.read_text(encoding="utf-8").replace(
                "- no auth, security, privacy, payment, migration, production, deployment, or",
                "- no auth, security, privacy, payment,\n  migration, production, deployment, or",
            ),
            encoding="utf-8",
        )
        readme = self.root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + "\nMigration risk and the replacement component are reviewed before "
            "the next phase.\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ordinary_status_and_task_wording_is_allowed(self) -> None:
        readme = self.root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + "\nMigration status is an input to the current status view. The next "
            "task defines the next step.\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hook_cannot_add_independent_policy(self) -> None:
        hook = self.root / ".githooks/pre-commit"
        hook.write_text(
            hook.read_text(encoding="utf-8") + "git status\n", encoding="utf-8"
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("hook-contract", result.stdout)

    def test_invalid_role_toml_is_actionable(self) -> None:
        roles = self.root / "codex/config/roles.native.toml"
        roles.write_text("[tiers.standard\n", encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "role-contract: codex/config/roles.native.toml is invalid",
            result.stdout,
        )

    def test_model_assignment_in_profile_is_rejected(self) -> None:
        profile = self.root / "codex/agents/orchestra_reviewer.toml"
        profile.write_text(
            profile.read_text(encoding="utf-8") + '\nmodel = "gpt-5.6-terra"\n',
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "profile-contract: orchestra_reviewer must contain only",
            result.stdout,
        )

    def test_invalid_role_model_is_rejected(self) -> None:
        roles = self.root / "codex/config/roles.native.toml"
        roles.write_text(
            roles.read_text(encoding="utf-8").replace(
                'model = "gpt-5.6-sol"', 'model = "unsupported"', 1
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has invalid model", result.stdout)


    def test_duplicate_profile_name_is_rejected(self) -> None:
        analyst = self.root / "codex/agents/orchestra_analyst.toml"
        analyst.write_text(
            analyst.read_text(encoding="utf-8").replace(
                'name = "orchestra_analyst"',
                'name = "orchestra_reviewer"',
                1,
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("profile names must be unique", result.stdout)

    def test_sync_legacy_inventory_diagnostic_tracks_contract_count(self) -> None:
        sync_script = self.root / "codex/scripts/sync.py"
        sync_script.write_text(
            sync_script.read_text(encoding="utf-8").replace(
                '    "web_researcher",\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "stale-profile cleanup must be limited to the 14 retired agent names",
            result.stdout,
        )

    def test_unconsumed_matrix_role_is_rejected(self) -> None:
        skill = self.root / "codex/skills/orchestra/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8").replace(
                "`difficult_debugging`", "diagnostic specialist"
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "difficult_debugging is not consumed", result.stdout
        )

    def test_speculative_pr_role_is_rejected(self) -> None:
        roles = self.root / "codex/config/roles.native.toml"
        roles.write_text(
            roles.read_text(encoding="utf-8")
            + '\n[tiers.standard.pr_poll]\nprofile = "orchestra_reviewer"\n'
            + 'model = "gpt-5.6-terra"\n'
            + 'reasoning_effort = "xhigh"\n',
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected native.standard capability set", result.stdout)

    def test_assignment_without_profile_is_rejected(self) -> None:
        roles = self.root / "codex/config/roles.native.toml"
        roles.write_text(
            roles.read_text(encoding="utf-8").replace(
                'profile = "orchestra_implementation_worker"\n', "", 1
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("needs profile, model, and reasoning_effort", result.stdout)

    def test_wrong_profile_mapping_and_sol_xhigh_are_rejected(self) -> None:
        roles = self.root / "codex/config/roles.native.toml"
        roles.write_text(
            roles.read_text(encoding="utf-8")
            .replace(
                'profile = "orchestra_analyst"',
                'profile = "orchestra_reviewer"',
                1,
            )
            .replace(
                'model = "gpt-5.6-sol"\nreasoning_effort = "high"',
                'model = "gpt-5.6-sol"\nreasoning_effort = "xhigh"',
                1,
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approved assignment matrix", result.stdout)
        self.assertIn("must not use Sol xhigh", result.stdout)

    def test_extra_internal_playbook_is_rejected(self) -> None:
        extra = self.root / "codex/skills/orchestra/references/extra.md"
        extra.write_text("# Extra\n", encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exactly seven playbooks", result.stdout)

    def test_broken_skill_link_is_actionable(self) -> None:
        skill = self.root / "codex/skills/orchestra/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8") + "\n[missing](missing.md)\n",
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skill-contract: orchestra has broken link missing.md", result.stdout)

    def test_shared_guidance_reaches_roles_and_recipe_consumers(self) -> None:
        consumers = (
            "orchestra/SKILL.md",
            "orchestra-role-analyst/SKILL.md",
            "orchestra-role-implementer/SKILL.md",
            "orchestra-role-reviewer/SKILL.md",
            "orchestra-role-verifier/SKILL.md",
            "orchestra-repo-onboard/SKILL.md",
            "orchestra-project-start/SKILL.md",
            "orchestra/references/repository_context.md",
            "orchestra/references/technical_planning.md",
            "orchestra/references/runtime_verification.md",
            "orchestra/references/browser_acceptance.md",
        )
        for relative in consumers:
            with self.subTest(consumer=relative):
                page = self.root / "codex/skills" / relative
                original = page.read_text(encoding="utf-8")
                # Leave the path as plain text: a mention is not a routed reference.
                unrouted = re.sub(
                    r"\[[^]]+\]\(([^)]*architecture_guidance\.md)\)",
                    r"\1",
                    original,
                )
                self.assertNotEqual(original, unrouted)
                try:
                    page.write_text(unrouted, encoding="utf-8")
                    result = self.run_validator()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        f"codex/skills/{relative} must link to shared engineering guidance",
                        result.stdout,
                    )
                finally:
                    page.write_text(original, encoding="utf-8")

    def test_shared_guidance_routing_does_not_pin_link_wording(self) -> None:
        page = self.root / "codex/skills/orchestra-role-implementer/SKILL.md"
        original = page.read_text(encoding="utf-8")
        rewritten = re.sub(
            r"\[[^]]+\]\(([^)]*architecture_guidance\.md)\)",
            r"[Relevant criteria](\1)",
            original,
        )
        self.assertNotEqual(original, rewritten)
        page.write_text(rewritten, encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_runtime_requires_exact_managed_markers(self) -> None:
        runtime = self.root / "codex/runtime/AGENTS.orchestra.md"
        runtime.write_text(
            runtime.read_text(encoding="utf-8").replace(
                "<!-- orchestra:end -->", "<!-- orchestra:done -->"
            ),
            encoding="utf-8",
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runtime-contract: managed markers", result.stdout)

    def test_full_mode_rejects_invalid_python_syntax(self) -> None:
        invalid = self.root / "codex/tests/invalid_fixture.py"
        invalid.write_text("def broken(:\n", encoding="utf-8")
        quick = self.run_validator("--quick")
        full = self.run_validator("--full")
        self.assertEqual(quick.returncode, 0, quick.stdout + quick.stderr)
        self.assertNotEqual(full.returncode, 0)
        self.assertIn("python-syntax: codex/tests/invalid_fixture.py", full.stdout)

    def test_lite_result_object_key_order_is_not_part_of_the_contract(self) -> None:
        example = self.root / "codex/skills/orchestra-lite/result-example.json"
        payload = json.loads(example.read_text(encoding="utf-8"))
        payload = dict(reversed(list(payload.items())))
        payload["Rama"] = dict(reversed(list(payload["Rama"].items())))
        payload["Checks"] = [dict(reversed(list(item.items()))) for item in payload["Checks"]]
        example.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_lite_result_and_kickoff_contracts_are_actionable(self) -> None:
        skill_dir = self.root / "codex/skills/orchestra-lite"
        example = skill_dir / "result-example.json"
        original_example = example.read_text(encoding="utf-8")
        payload = json.loads(original_example)
        payload["Estado nuevo"] = payload.pop("Estado")
        example.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lite-contract: result-example.json must contain exactly", result.stdout)
        example.write_text("{not json", encoding="utf-8")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lite-contract: result-example.json is invalid JSON", result.stdout)
        example.write_text(original_example, encoding="utf-8")

        template = skill_dir / "kickoff-template.md"
        template.write_text(
            template.read_text(encoding="utf-8").replace("\nPR:\n", "\n", 1), encoding="utf-8"
        )
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("kickoff template is missing mandatory field PR", result.stdout)

    def test_missing_common_helper_fails_quick(self) -> None:
        (self.root / "codex/scripts/_common.py").unlink()
        result = self.run_validator("--quick")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("required-path: missing codex/scripts/_common.py", result.stdout)

    def test_missing_coordination_helper_fails_quick(self) -> None:
        (self.root / "codex/scripts/coordination.py").unlink()
        result = self.run_validator("--quick")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "required-path: missing codex/scripts/coordination.py",
            result.stdout,
        )

if __name__ == "__main__":
    unittest.main()
