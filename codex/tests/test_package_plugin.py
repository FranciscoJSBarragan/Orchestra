"""Acceptance for relocatable plugins built without touching host configuration."""
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "codex/scripts"))
from package_plugin import HELPERS, SKILLS, TARGETS, build_plugin


class PluginPackagingTests(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()

    def build(self, target: str = "portable") -> Path:
        return build_plugin(ROOT, self.root / target / "orchestra", target)

    def run_helper(self, plugin: Path, helper: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(plugin / "scripts" / helper), *args],
            cwd=self.root,
            env={**os.environ, "HOME": str(self.root / "home"),
                 "CODEX_HOME": str(self.root / "home/.codex"),
                 "ORCHESTRA_HOME": str(self.root / "state"),
                 "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, text=True, check=False,
        )

    def test_targets_share_canonical_runtime_without_global_configuration(self) -> None:
        for target in TARGETS:
            with self.subTest(target=target):
                plugin = self.build(target)
                self.assertEqual(sorted(p.name for p in (plugin / "skills").iterdir()), sorted(SKILLS))
                self.assertFalse((plugin / "skills/orchestra-lite").exists())
                for helper in HELPERS:
                    self.assertEqual((plugin / "scripts" / helper).read_bytes(), (ROOT / "codex/scripts" / helper).read_bytes())
                self.assertEqual((plugin / "WORKFLOW.md").read_bytes(), (ROOT / "docs/WORKFLOW.md").read_bytes())
                self.assertEqual((plugin / "flow.toml").read_bytes(), (ROOT / "codex/config/flow.toml").read_bytes())
                skill_root = ROOT / "codex/skills"
                resources = (*skill_root.rglob("*.md"), *skill_root.glob("*/agents/openai.yaml"))
                for source in resources:
                    self.assertEqual((plugin / "skills" / source.relative_to(ROOT / "codex/skills")).read_bytes(), source.read_bytes())
                for absent in ("hosts", "profiles", "agents", "scripts/sync.py", "scripts/delegate.py"):
                    self.assertFalse((plugin / absent).exists(), absent)
                self.assertFalse((plugin / ".mcp.json").exists())
                self.assertFalse((plugin / "mcp.json").exists())
                self.assertFalse((plugin / "config.toml").exists())
        self.assertFalse((self.root / "home").exists())
        self.assertFalse((self.root / "state").exists())

    def test_host_manifests_select_one_format_and_shared_metadata(self) -> None:
        metadata = json.loads((ROOT / "packaging/orchestra/.codex-plugin/plugin.json").read_text())
        manifests = {"portable": "plugin.json", "cursor": ".cursor-plugin/plugin.json", "grok": ".claude-plugin/plugin.json", "claude": ".claude-plugin/plugin.json"}
        for target in TARGETS:
            plugin = self.build(target)
            manifest = json.loads((plugin / manifests[target]).read_text())
            for key in ("name", "version", "description", "license"):
                self.assertEqual(manifest[key], metadata[key])
            self.assertEqual(json.loads((plugin / ".codex-plugin/plugin.json").read_text()), metadata)
            for name in set(manifests.values()):
                self.assertEqual((plugin / name).exists(), name == manifests[target])
            self.assertEqual((plugin / "hooks/hooks.json").exists(), target == "claude")
            self.assertFalse((plugin / "hooks.json").exists())

    def test_relative_skill_links_stay_inside_the_bundle_and_resolve(self) -> None:
        for target in TARGETS:
            plugin = self.build(target)
            for page in [plugin / "WORKFLOW.md", *(plugin / "skills").rglob("*.md")]:
                for link in re.findall(r"\]\(([^)]+)\)", page.read_text()):
                    if link.startswith(("https://", "http://", "#")):
                        continue
                    destination = (page.parent / link.split("#")[0]).resolve()
                    self.assertTrue(destination.is_relative_to(plugin), (page, link))
                    self.assertTrue(destination.is_file(), (page, link))

    def test_relocated_helpers_read_the_project_and_leave_the_bundle_unchanged(self) -> None:
        original = self.build()
        plugin = self.root / "relocated with spaces/orchestra"
        plugin.parent.mkdir()
        shutil.move(original, plugin)
        project = self.root / "project"
        project.mkdir()
        shutil.copy2(ROOT / "orchestra.toml", project / "orchestra.toml")
        before = {p.relative_to(plugin): p.read_bytes() for p in plugin.rglob("*") if p.is_file()}
        result = self.run_helper(plugin, "policy.py", "--repo", str(project), "show")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "hybrid")
        self.assertFalse((self.root / "home/.orchestra").exists())
        after = {p.relative_to(plugin): p.read_bytes() for p in plugin.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse((self.root / "home/.codex").exists())


    def test_packaged_preparation_uses_exact_source_without_global_installation(self) -> None:
        plugin = self.build()
        repository = self.root / "source fixture"
        for relative in (
            "docs/WORKFLOW.md", "codex/skills/orchestra/SKILL.md",
            "codex/skills/orchestra/runtime.md", "codex/config/flow.toml",
        ):
            target = repository / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        for arguments in (
            ("init", "--quiet"), ("add", "."),
            ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "source fixture"),
        ):
            subprocess.run(["git", "-C", str(repository), *arguments], capture_output=True, check=True)
        revision = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        destination = self.root / "prepared source"
        result = self.run_helper(
            plugin, "prepare_source.py", "--revision", revision,
            "--repository", str(repository), "--destination", str(destination),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["revision"], revision)
        self.assertEqual(Path(payload["workflow"]), destination / "docs/WORKFLOW.md")
        self.assertTrue((Path(payload["skills_root"]) / "orchestra/SKILL.md").is_file())
        self.assertFalse((self.root / "home").exists())
        self.assertFalse((self.root / "state").exists())

    def test_claude_target_ships_only_the_package_read_hook(self) -> None:
        plugin = self.build("claude")
        hooks = json.loads((plugin / "hooks/hooks.json").read_text())
        command = hooks["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", command)
        self.assertTrue((plugin / "hooks/read_package.py").is_file())

    def test_existing_destination_is_never_overwritten(self) -> None:
        plugin = self.build()
        sentinel = plugin / "user.txt"
        sentinel.write_text("preserve")
        with self.assertRaisesRegex(ValueError, "already exists"):
            build_plugin(ROOT, plugin, "portable")
        self.assertEqual(sentinel.read_text(), "preserve")

    def test_invalid_target_and_incomplete_sources_leave_no_package(self) -> None:
        output = self.root / "orchestra"
        with self.assertRaisesRegex(ValueError, "unsupported"):
            build_plugin(ROOT, output, "unknown")
        self.assertFalse(output.exists())
        source = self.root / "source"
        shutil.copytree(ROOT / "packaging", source / "packaging")
        with self.assertRaisesRegex(ValueError, "missing skill"):
            build_plugin(source, output, "portable")
        self.assertFalse(output.exists())


class PackageReadHookTests(unittest.TestCase):
    def decide(self, root: Path, target: object) -> str:
        result = subprocess.run(
            [sys.executable, str(ROOT / "packaging/claude/hooks/read_package.py")],
            input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": target}}),
            env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(root)},
            capture_output=True, text=True, check=True,
        )
        return json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] if result.stdout else "none"

    def test_only_package_paths_are_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve()
            package = base / "orchestra"
            (package / "skills").mkdir(parents=True)
            (package / "skills/escape").symlink_to(base)
            self.assertEqual(self.decide(package, str(package / "skills/role/SKILL.md")), "allow")
            for target in (str(base / "secret.txt"), str(package / "../secret.txt"),
                           str(package / "skills/escape/secret.txt"), "skills/role/SKILL.md", None):
                with self.subTest(target=target):
                    self.assertEqual(self.decide(package, target), "none")


if __name__ == "__main__":
    unittest.main()
