"""Structural contracts for the orchestra-lite companion and its local trial fixtures.

These tests pin machine-consumed shapes (kickoff fields, result keys and types,
inventory registration, non-routing from the full workflow) and prove that the
trial fixtures build and their gh shim behaves. They do not prove agent
behavior; the fixture README describes the coordinator-run agent trials.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "codex/scripts"))
sys.path.insert(0, str(ROOT / "codex/tests/fixtures/orchestra-lite"))
import make_fixture  # noqa: E402
import sync  # noqa: E402
import validate_suite  # noqa: E402

SKILL_DIR = ROOT / "codex/skills/orchestra-lite"
STATES = {"DONE", "DONE_PR_PENDING", "BLOCKED"}


class LiteSkillContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.example = json.loads((SKILL_DIR / "result-example.json").read_text(encoding="utf-8"))

    def test_skill_is_registered_once_in_every_inventory(self) -> None:
        self.assertEqual(sync.SKILLS.count("orchestra-lite"), 1)
        self.assertEqual(validate_suite.SKILL_NAMES.count("orchestra-lite"), 1)
        for relative in ("SKILL.md", "agents/openai.yaml", "kickoff-template.md", "result-example.json"):
            self.assertIn(f"codex/skills/orchestra-lite/{relative}", validate_suite.REQUIRED_PATHS)

    def test_kickoff_activation_metadata_allows_discovery_without_a_slash(self) -> None:
        frontmatter = self.skill.split("---", 2)[1]
        self.assertRegex(frontmatter, r"(?m)^name: orchestra-lite$")
        self.assertIn("ORCHESTRA_LITE_SPEC", frontmatter)
        metadata = (SKILL_DIR / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(metadata, r"(?m)^\s+allow_implicit_invocation: true$")
        self.assertIn("$orchestra-lite", metadata)

    def test_result_example_types_match_the_coordinator_contract(self) -> None:
        self.assertEqual(set(self.example), set(validate_suite.LITE_RESULT_KEYS))
        self.assertIn(self.example["Estado"], STATES)
        self.assertIsInstance(self.example["PR"], (str, type(None)))
        self.assertEqual(set(self.example["Rama"]), {"Nombre", "SHA"})
        self.assertRegex(self.example["Rama"]["SHA"], r"^[0-9a-f]{40}$")
        self.assertIsInstance(self.example["Publicada"], bool)
        for key in ("Commits", "Checks", "Decisiones tomadas", "Riesgos / no hecho", "Pendiente para merge"):
            self.assertIsInstance(self.example[key], list, key)
        for item in self.example["Checks"]:
            self.assertEqual(set(item), set(validate_suite.LITE_CHECK_KEYS))
            self.assertIsInstance(item["Código de salida"], (int, type(None)))
        self.assertIsInstance(self.example["CI"], str)
        self.assertIsInstance(self.example["Bloqueo"], (str, type(None)))

    def test_kickoff_template_lists_every_fixed_field_once(self) -> None:
        template = (SKILL_DIR / "kickoff-template.md").read_text(encoding="utf-8")
        block = template.split("```text\n", 1)[1].split("```", 1)[0]
        names = [line.split(":", 1)[0] for line in block.splitlines() if line and not line.startswith("-")]
        self.assertEqual(names[0], validate_suite.LITE_KICKOFF_MARKER)
        expected = [
            "Repo", "Base", "Slug", "Rama", "PR", "Tier", "Recursos", "Autorización", "Objetivo",
            "Aceptación", "Exclusiones", "Decisiones", "Checks", "Revisión", "Actualizar STATUS", "Reporte",
        ]
        self.assertCountEqual(names[1:], expected)
        for field in validate_suite.LITE_MANDATORY_FIELDS:
            self.assertIn(field, expected)

    def test_lite_is_instruction_only_and_outside_the_full_workflow_routes(self) -> None:
        self.assertFalse((SKILL_DIR / "scripts").exists())
        for resource in SKILL_DIR.rglob("*"):
            if resource.is_file():
                self.assertIn(resource.suffix, {".md", ".yaml", ".json"}, str(resource))
        for relative in ("codex/skills/orchestra/SKILL.md", "codex/runtime/AGENTS.orchestra.md"):
            self.assertNotIn("orchestra-lite", (ROOT / relative).read_text(encoding="utf-8"), relative)
        for matrix in (
            "codex/config/roles.native.toml",
            "hosts/cursor/config/roles.cursor.toml",
            "hosts/grok/config/roles.grok.toml",
            "hosts/devin/config/roles.devin.toml",
        ):
            tiers = tomllib.loads((ROOT / matrix).read_text(encoding="utf-8"))["tiers"]
            for tier, assignments in tiers.items():
                self.assertNotIn("orchestra_lite", assignments, f"{matrix}:{tier}")
        self.assertNotIn("orchestra-lite", (ROOT / "hosts/cursor/plugin/commands/orchestra.md").read_text())


class LiteFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()

    def build(self, scenario: str) -> dict[str, object]:
        return make_fixture.build(scenario, self.root / scenario)

    def git(self, cwd: Path, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()

    def gh(self, fixture: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(fixture / "bin/gh"), *args], cwd=cwd or fixture / "repo",
            capture_output=True, text=True, check=False,
        )

    def test_every_scenario_builds_a_clean_repo_bare_remote_and_kickoff(self) -> None:
        for scenario in make_fixture.SCENARIOS:
            with self.subTest(scenario=scenario):
                summary = self.build(scenario)
                repo, remote = Path(summary["repo"]), Path(summary["remote"])
                self.assertEqual(self.git(remote, "rev-parse", "--is-bare-repository"), "true")
                self.assertEqual(self.git(repo, "config", "remote.origin.url"), make_fixture.ORIGIN_URL)
                self.assertEqual(self.git(repo, "remote", "get-url", "origin"), str(remote))
                self.assertEqual(
                    self.git(repo, "ls-remote", "origin", "refs/heads/main").split()[0],
                    summary["base_sha"],
                )
                self.assertEqual(self.git(repo, "status", "--porcelain"), "")
                self.assertEqual(self.git(remote, "rev-parse", "refs/heads/main"), summary["base_sha"])
                check = subprocess.run(
                    make_fixture.CHECK, cwd=repo, capture_output=True, text=True, check=False,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                )
                self.assertEqual(check.returncode, 0, check.stderr)
                kickoff = Path(summary["kickoff"]).read_text(encoding="utf-8").splitlines()
                self.assertEqual(kickoff[0], validate_suite.LITE_KICKOFF_MARKER)
                self.assertIn(f"Repo: {make_fixture.REPO_NAME}", kickoff)
                fields = {line.split(":", 1)[0] for line in kickoff}
                for field in validate_suite.LITE_MANDATORY_FIELDS:
                    self.assertEqual(field in fields, not (scenario == "missing-field" and field == "PR"), field)
                self.assertTrue((Path(summary["bin"]) / "gh").is_file())
                self.assertTrue((repo / "AGENTS.md").is_file())
                self.assertEqual(
                    (repo / ".agent/review-policy.md").is_file(), scenario == "review-before-commit"
                )

    def test_delivery_authorizes_a_tracked_status_update_in_the_delivered_range(self) -> None:
        summary = self.build("delivery")
        repo = Path(summary["repo"])
        self.assertEqual(self.git(repo, "show", "main:STATUS.md"), make_fixture.STATUS_BASELINE.strip())
        kickoff = Path(summary["kickoff"]).read_text(encoding="utf-8")
        self.assertIn("Actualizar STATUS: sí STATUS.md", kickoff)

    def test_missing_gh_shadows_host_cli_with_an_unavailable_stub(self) -> None:
        summary = self.build("missing-gh")
        sentinel = self.root / "host-gh-was-used"
        host_bin = self.root / "host-bin"
        host_bin.mkdir()
        host_gh = host_bin / "gh"
        host_gh.write_text(f'#!/bin/sh\ntouch "{sentinel}"\nexit 0\n', encoding="utf-8")
        host_gh.chmod(0o755)
        result = subprocess.run(
            ["gh", "auth", "status"], cwd=summary["repo"], capture_output=True, text=True,
            env={**os.environ, "PATH": os.pathsep.join((summary["bin"], str(host_bin), os.environ["PATH"]))},
            check=False,
        )
        self.assertEqual(result.returncode, 127)
        self.assertIn("unavailable", result.stderr)
        self.assertFalse(sentinel.exists())

    def test_branch_scenarios_prepare_the_remote_state_the_worker_must_respect(self) -> None:
        supplied = self.build("supplied-branch")
        repo = Path(supplied["repo"])
        self.assertEqual(self.git(repo, "rev-parse", "--abbrev-ref", "HEAD"), make_fixture.BRANCH)
        self.assertEqual(
            self.git(Path(supplied["remote"]), "rev-parse", f"refs/heads/{make_fixture.BRANCH}"),
            supplied["base_sha"],
        )
        self.assertIn(f"Rama: {make_fixture.BRANCH}", Path(supplied["kickoff"]).read_text())
        self.assertIn("PR: plataforma", Path(supplied["kickoff"]).read_text())

        divergent = self.build("divergent-remote")
        remote_sha = self.git(Path(divergent["remote"]), "rev-parse", f"refs/heads/{make_fixture.BRANCH}")
        self.assertEqual(remote_sha, divergent["remote_branch_sha"])
        self.assertNotEqual(remote_sha, divergent["base_sha"])
        self.assertEqual(self.git(Path(divergent["repo"]), "branch", "--list", "orchestra/*"), "")
        self.assertFalse((self.root / "divergent-remote/scratch").exists())

    def test_gh_shim_records_draft_creation_and_rejects_unsimulated_commands(self) -> None:
        summary = self.build("delivery")
        fixture = self.root / "delivery"
        self.assertEqual(self.gh(fixture, "auth", "status").returncode, 0)
        created = self.gh(
            fixture, "pr", "create", "--draft", "--base", "main", "--head", make_fixture.BRANCH,
            "--title", "feat(tokens): strict parsing", "--body", "Spec\n\nCambios\n",
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        url = created.stdout.strip()
        view = self.gh(fixture, "pr", "view", make_fixture.BRANCH, "--json", "isDraft,baseRefName,headRefName,url")
        self.assertEqual(
            json.loads(view.stdout),
            {"isDraft": True, "baseRefName": "main", "headRefName": make_fixture.BRANCH, "url": url},
        )
        listed = json.loads(self.gh(fixture, "pr", "list", "--head", make_fixture.BRANCH, "--json", "number").stdout)
        self.assertEqual(listed, [{"number": 1}])
        duplicate = self.gh(
            fixture, "pr", "create", "--draft", "--base", "main", "--head", make_fixture.BRANCH,
            "--title", "again", "--body", "x",
        )
        self.assertNotEqual(duplicate.returncode, 0)
        merged = self.gh(fixture, "pr", "merge", "1")
        self.assertNotEqual(merged.returncode, 0)
        self.assertIn("unsupported", merged.stderr)
        calls = (fixture / "gh-state/calls.log").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(calls), 6)
        self.assertEqual(json.loads(calls[1])[:3], ["pr", "create", "--draft"])
        self.assertEqual(self.git(Path(summary["repo"]), "status", "--porcelain"), "")

    def test_output_directory_must_be_new(self) -> None:
        self.build("missing-field")
        with self.assertRaises(SystemExit):
            make_fixture.build("missing-field", self.root / "missing-field")
        with self.assertRaises(SystemExit):
            make_fixture.build("not-a-scenario", self.root / "other")
        self.assertFalse((self.root / "other").exists())


if __name__ == "__main__":
    unittest.main()
