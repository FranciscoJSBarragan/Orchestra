"""Isolated tests for direct Orchestra synchronization."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SYNC_PATH = ROOT / "codex/scripts/sync.py"
SPEC = importlib.util.spec_from_file_location("orchestra_sync", SYNC_PATH)
assert SPEC is not None and SPEC.loader is not None
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


class SyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        base = Path(self.temporary.name)
        self.home = base / "home"
        self.codex_home = base / "codex-home"
        self.orchestra_root = self.home / ".orchestra"
        self.worktree_root = self.home / ".orchestra" / "worktrees"
        self.assertNotEqual(self.home.resolve(), Path.home().resolve())
        self.assertNotEqual(self.codex_home.resolve(), (Path.home() / ".codex").resolve())
        self.original_cache_discovery = sync._discover_cache_roots
        self.cache_patcher = mock.patch.object(
            sync,
            "_discover_cache_roots",
            return_value=(
                {},
                {tool: "not installed" for tool in sync.CACHE_TOOLS},
            ),
        )
        self.cache_discovery = self.cache_patcher.start()
        self.addCleanup(self.cache_patcher.stop)
        self.version_patcher = mock.patch.object(
            sync,
            "_detect_codex_version",
            return_value=("0.146.0", (0, 146, 0)),
        )
        self.codex_version = self.version_patcher.start()
        self.addCleanup(self.version_patcher.stop)

    def subprocess_environment(self) -> dict[str, str]:
        """Supply the same version fixture across the subprocess boundary."""
        tools = Path(self.temporary.name) / "bin"
        tools.mkdir()
        codex = tools / "codex"
        codex.write_text(
            '#!/bin/sh\n'
            'if [ "$#" -eq 1 ] && [ "$1" = "--version" ]; then\n'
            '  printf "%s\\n" "codex-cli 0.146.0"\n'
            'else\n'
            '  exit 1\n'
            'fi\n'
        )
        codex.chmod(0o700)
        env = os.environ.copy()
        env["PATH"] = str(tools) + os.pathsep + env.get("PATH", os.defpath)
        return env

    def run_sync(
        self,
        action: str,
        *,
        dry_run: bool = False,
        modelconfig: str | None = None,
        checkout_mode: str | None = None,
        host: str = "codex",
    ) -> dict[str, object]:
        return sync.synchronize(
            ROOT,
            self.home,
            self.codex_home,
            action,
            dry_run=dry_run,
            modelconfig=modelconfig,
            checkout_mode=checkout_mode,
            worktree_root=self.worktree_root,
            host=host,
        )

    def manifest(self) -> dict[str, object]:
        return json.loads(self.manifest_path().read_text())

    def manifest_path(self) -> Path:
        return self.orchestra_root / "install-manifest.json"

    def legacy_manifest_path(self) -> Path:
        return self.codex_home / "orchestra/install-manifest.json"

    def source_fixture(self) -> Path:
        fixture = Path(self.temporary.name) / "source"
        for directory in ("skills", "agents", "control"):
            shutil.copytree(ROOT / "codex" / directory, fixture / "codex" / directory)
        (fixture / "codex/config").mkdir(parents=True)
        shutil.copy2(
            ROOT / "codex/config/execution-presets.toml",
            fixture / "codex/config/execution-presets.toml",
        )
        for modelconfig in ("native",):
            shutil.copy2(
                ROOT / f"codex/config/roles.{modelconfig}.toml",
                fixture / f"codex/config/roles.{modelconfig}.toml",
            )
        (fixture / "codex/scripts").mkdir(parents=True)
        for helper in sync.HELPERS:
            shutil.copy2(ROOT / "codex/scripts" / helper, fixture / "codex/scripts" / helper)
        (fixture / "codex/runtime").mkdir(parents=True)
        shutil.copy2(
            ROOT / "codex/runtime/AGENTS.orchestra.md",
            fixture / "codex/runtime/AGENTS.orchestra.md",
        )
        (fixture / "docs").mkdir(parents=True)
        shutil.copy2(ROOT / "docs/WORKFLOW.md", fixture / "docs/WORKFLOW.md")
        return fixture

    def convert_current_install_to_legacy_profile_manifest(self) -> None:
        """Model an owned pre-namespace install without retired source files."""
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest_path = self.manifest_path()
        payload = self.manifest()
        current_paths = {f"agents/{name}.toml" for name in sync.AGENTS}
        entries = [
            {
                key: value
                for key, value in entry.items()
                if key not in {"scope", "backup_root"}
            }
            for entry in payload["entries"]
            if entry["path"] not in current_paths
        ]
        for name in sync.AGENTS:
            (self.codex_home / f"agents/{name}.toml").unlink()
        for name in sync.LEGACY_AGENTS:
            content = f"retired owned profile: {name}\n".encode()
            destination = self.codex_home / f"agents/{name}.toml"
            destination.write_bytes(content)
            entries.append(
                {
                    "digest": hashlib.sha256(content).hexdigest(),
                    "path": f"agents/{name}.toml",
                    "root": "codex_home",
                    "type": "file",
                }
            )
        manifest_path.write_text(
            json.dumps(
                {
                    "entries": sorted(
                        entries, key=lambda entry: (entry["root"], entry["path"])
                    )
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )

    def test_clean_install_status_and_uninstall(self) -> None:
        status = self.run_sync("status")
        self.assertEqual(status["status"], "partial")
        self.assertEqual(status["modelconfig"], "native")
        self.assertEqual(status["checkout_mode"], "managed")
        self.assertEqual(status["sandbox_root"], str(self.orchestra_root))
        self.assertTrue(status["restart_required"])
        self.assertFalse(self.home.exists())
        self.assertFalse(self.codex_home.exists())

        applied = self.run_sync("apply")
        self.assertEqual(applied["status"], "ok")
        self.assertEqual(applied["modelconfig"], "native")
        self.assertEqual(applied["checkout_mode"], "managed")
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        self.assertTrue(
            self.home.joinpath(
                ".agents/skills/orchestra-project-start/SKILL.md"
            ).is_file()
        )
        self.assertTrue(
            self.home.joinpath(
                ".agents/skills/orchestra-repo-onboard/SKILL.md"
            ).is_file()
        )
        for relative in ("SKILL.md", "kickoff-template.md", "result-example.json"):
            self.assertTrue(
                self.home.joinpath(f".agents/skills/orchestra-lite/{relative}").is_file(),
                relative,
            )
        for name in sync.AGENTS:
            self.assertTrue(self.codex_home.joinpath(f"agents/{name}.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("orchestra/roles.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("orchestra/scripts/pr.py").is_file())
        self.assertTrue(
            self.codex_home.joinpath("orchestra/scripts/coordination.py").is_file()
        )
        self.assertTrue(
            self.codex_home.joinpath("orchestra/scripts/task_state.py").is_file()
        )
        self.assertFalse(
            self.codex_home.joinpath("orchestra/scripts/session_model.py").exists()
        )
        self.assertTrue(
            self.codex_home.joinpath("orchestra/scripts/task_mcp.py").is_file()
        )
        self.assertEqual(
            self.codex_home.joinpath("orchestra/worktree-root").read_text(),
            f"{self.worktree_root}\n",
        )
        self.assertEqual(
            self.codex_home.joinpath("orchestra/checkout-mode").read_text(),
            "managed\n",
        )
        config = self.codex_home.joinpath("config.toml").read_text()
        self.assertIn('approval_policy = "on-request"', config)
        self.assertIn('approvals_reviewer = "auto_review"', config)
        self.assertIn('default_permissions = ":workspace"', config)
        self.assertIn("mcp_servers.orchestra_tasks = {", config)
        self.assertIn('default_tools_approval_mode = "writes"', config)
        self.assertIn("orchestra/scripts/task_mcp.py", config)
        self.assertNotIn("orchestra-workspace", config)
        self.assertNotIn("[permissions.", config)
        self.assertNotIn("[sandbox_workspace_write]", config)
        self.assertNotIn("sandbox_mode", config)
        self.assertIn("# orchestra-worktree-root:start", config)
        self.assertEqual(applied["codex_version"], "0.146.0")
        self.assertEqual(applied["permission_backend"], "profile")
        self.assertEqual(applied["permission_profile"], ":workspace")
        self.assertTrue(applied["profile_configured"])
        self.assertEqual(self.manifest()["permission_backend"], "profile")
        self.assertTrue(applied["restart_required"])
        installed_guidance = self.codex_home.joinpath("AGENTS.md").read_text()
        self.assertIn("planning-only host mode", installed_guidance)
        self.assertIn("unequivocal imperative to use or start Orchestra", installed_guidance)
        self.assertIn("adopt_worktree.py", installed_guidance)
        self.assertIn("without `autoResolutionMs`", installed_guidance)
        self.assertNotIn("Plan Mode", installed_guidance)
        self.assertTrue(
            self.codex_home.joinpath("orchestra/scripts/adopt_worktree.py").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("scripts/coordination.py").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("control/orchestra_control/service.py").is_file()
        )
        self.assertEqual(
            self.orchestra_root.joinpath("checkout-mode").read_text(),
            "managed\n",
        )
        synchronized_status = self.run_sync("status")
        self.assertEqual(synchronized_status["status"], "ok")
        self.assertFalse(synchronized_status["restart_required"])
        installed_agents = {
            entry["path"]
            for entry in self.manifest()["entries"]
            if entry["root"] == "codex_home" and entry["path"].startswith("agents/")
        }
        self.assertEqual(
            installed_agents,
            {f"agents/{name}.toml" for name in sync.AGENTS},
        )
        self.assertEqual(len(installed_agents), 4)
        self.assertEqual(self.manifest()["modelconfig"], "native")
        self.assertEqual(self.manifest()["checkout_mode"], "managed")
        self.assertEqual(
            self.codex_home.joinpath("orchestra/roles.toml").read_bytes(),
            ROOT.joinpath("codex/config/roles.native.toml").read_bytes(),
        )
        self.assertFalse(
            self.codex_home.joinpath("orchestra/roles.external.toml").exists()
        )
        self.assertFalse(
            self.codex_home.joinpath("orchestra/roles.native.toml").exists()
        )
        second = self.run_sync("apply")
        self.assertEqual(second["status"], "ok")
        self.assertEqual(second["changes"], [])
        self.assertEqual(
            self.home.joinpath(".agents/skills/orchestra/SKILL.md").stat().st_mode & 0o777,
            0o644,
        )

    def test_checkout_mode_defaults_to_managed_and_switches_atomically(self) -> None:
        installed = self.run_sync("apply")
        self.assertEqual(installed["checkout_mode"], "managed")

        preview = self.run_sync("apply", dry_run=True, checkout_mode="hybrid")
        self.assertEqual(preview["status"], "partial")
        self.assertEqual(preview["checkout_mode"], "hybrid")
        self.assertIn(
            {
                "operation": "update",
                "path": "orchestra/checkout-mode",
                "root": "codex_home",
            },
            preview["changes"],
        )
        self.assertEqual(
            self.codex_home.joinpath("orchestra/checkout-mode").read_text(),
            "managed\n",
        )

        switched = self.run_sync("apply", checkout_mode="hybrid")
        self.assertEqual(switched["status"], "ok")
        self.assertEqual(switched["checkout_mode"], "hybrid")
        self.assertEqual(self.manifest()["checkout_mode"], "hybrid")
        self.assertEqual(
            self.codex_home.joinpath("orchestra/checkout-mode").read_text(),
            "hybrid\n",
        )
        self.assertEqual(
            self.run_sync("status", modelconfig=None)["checkout_mode"], "hybrid"
        )
        self.assertEqual(
            self.codex_home.joinpath(
                "agents/orchestra_reviewer.toml"
            ).stat().st_mode
            & 0o777,
            0o644,
        )
        self.assertEqual(
            self.manifest_path().stat().st_mode
            & 0o777,
            0o600,
        )

        state_database = self.orchestra_root / "state.sqlite3"
        state_database.parent.mkdir(parents=True, exist_ok=True)
        state_database.write_bytes(b"user-owned coordination state")
        removed = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(removed["status"], "ok")
        self.assertFalse(self.home.joinpath(".agents/skills/orchestra").exists())
        self.assertFalse(self.codex_home.joinpath("install-manifest.json").exists())
        self.assertFalse(self.manifest_path().exists())
        for name in sync.AGENTS:
            self.assertFalse(self.codex_home.joinpath(f"agents/{name}.toml").exists())
        self.assertFalse(self.codex_home.joinpath("config.toml").exists())
        self.assertFalse(
            self.codex_home.joinpath("orchestra/scripts/coordination.py").exists()
        )
        self.assertTrue(removed["restart_required"])
        self.assertEqual(state_database.read_bytes(), b"user-owned coordination state")

    def test_apply_retires_owned_worktree_bridge(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        retired = {
            "orchestra/scripts/create_worktree.py": b"retired helper\n",
            "rules/orchestra.rules": b"retired rule\n",
        }
        manifest_path = self.manifest_path()
        payload = self.manifest()
        for relative, content in retired.items():
            destination = self.codex_home / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            payload["entries"].append(
                {
                    "digest": hashlib.sha256(content).hexdigest(),
                    "path": relative,
                    "root": "codex_home",
                    "scope": "codex",
                    "type": "file",
                }
            )
        payload["entries"].sort(key=lambda entry: (entry["root"], entry["path"]))
        manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        status = self.run_sync("status")
        self.assertEqual(status["status"], "partial")
        self.assertTrue(status["restart_required"])
        migrated = self.run_sync("apply")
        self.assertEqual(migrated["status"], "ok")
        self.assertTrue(migrated["restart_required"])
        for relative in retired:
            self.assertFalse(self.codex_home.joinpath(relative).exists())

    def test_old_codex_blocks_status_and_apply_without_mutation(self) -> None:
        self.codex_version.return_value = ("0.145.9", (0, 145, 9))

        for action, dry_run in (
            ("status", False),
            ("apply", True),
            ("apply", False),
        ):
            with self.subTest(action=action, dry_run=dry_run):
                result = self.run_sync(action, dry_run=dry_run)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["codex_version"], "0.145.9")
                self.assertIn("Codex 0.146.0 or later", result["detail"])
                self.assertFalse(self.home.exists())
                self.assertFalse(self.codex_home.exists())
        self.cache_discovery.assert_not_called()

    def test_legacy_backend_migrates_to_guardian_and_uninstalls_exactly(
        self,
    ) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = 'model = "test-model"\n'
        config.write_text(original)

        self.assertEqual(self.run_sync("apply")["status"], "ok")
        legacy_block = (
            sync.CONFIG_START
            + b'\napproval_policy = "never"\n'
            + b'sandbox_mode = "danger-full-access"\n'
            + sync.CONFIG_END
            + b"\n"
        )
        config.write_bytes(
            original.encode()
            + legacy_block
        )
        manifest_path = self.manifest_path()
        manifest = self.manifest()
        config_entry = next(
            entry for entry in manifest["entries"] if entry["path"] == "config.toml"
        )
        config_entry["digest"] = hashlib.sha256(legacy_block).hexdigest()
        manifest["permission_backend"] = "legacy"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        upgraded = self.run_sync("apply")
        self.assertEqual(upgraded["status"], "ok")
        self.assertEqual(upgraded["permission_backend"], "profile")
        installed = config.read_text()
        self.assertIn('approval_policy = "on-request"', installed)
        self.assertIn('approvals_reviewer = "auto_review"', installed)
        self.assertIn('default_permissions = ":workspace"', installed)
        self.assertNotIn("sandbox_mode", installed)

        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(config.read_text(), original)

    def test_owned_full_access_profile_migrates_to_guardian(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            'model = "test-model"\n'
            'web_search = "indexed"\n'
        )
        config.write_text(original)
        self.assertEqual(self.run_sync("apply")["status"], "ok")

        current = config.read_bytes()
        span = sync._config_span(current)
        self.assertIsNotNone(span)
        assert span is not None
        old_block = (
            sync.CONFIG_START
            + b'\napproval_policy = "never"\n'
            + b'default_permissions = ":danger-full-access"\n'
            + sync.CONFIG_END
            + b"\n"
        )
        config.write_bytes(current[: span[0]] + old_block + current[span[1] :])
        manifest_path = self.manifest_path()
        manifest = self.manifest()
        config_entry = next(
            entry for entry in manifest["entries"] if entry["path"] == "config.toml"
        )
        config_entry["digest"] = hashlib.sha256(old_block).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        migrated = self.run_sync("apply")

        self.assertEqual(migrated["status"], "ok")
        installed = config.read_text()
        self.assertIn('approval_policy = "on-request"', installed)
        self.assertIn('approvals_reviewer = "auto_review"', installed)
        self.assertIn('default_permissions = ":workspace"', installed)
        self.assertNotIn("danger-full-access", installed)
        self.assertIn('web_search = "indexed"', installed)
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(config.read_text(), original)

    def test_historical_legacy_install_uninstalls_without_codex(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = 'model = "test-model"\n'
        config.write_text(original)
        self.assertEqual(self.run_sync("apply")["status"], "ok")

        current = config.read_bytes()
        span = sync._config_span(current)
        self.assertIsNotNone(span)
        assert span is not None
        legacy_block = (
            sync.CONFIG_START
            + b'\napproval_policy = "never"\n'
            + b'sandbox_mode = "danger-full-access"\n'
            + sync.CONFIG_END
            + b"\n"
        )
        config.write_bytes(
            current[: span[0]] + legacy_block + current[span[1] :]
        )
        manifest_path = self.manifest_path()
        manifest = self.manifest()
        config_entry = next(
            entry for entry in manifest["entries"] if entry["path"] == "config.toml"
        )
        config_entry["digest"] = hashlib.sha256(legacy_block).hexdigest()
        manifest["permission_backend"] = "legacy"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.codex_version.side_effect = sync.SyncError("Codex is unavailable")

        removed = sync.uninstall(self.home, self.codex_home)

        self.assertEqual(removed["status"], "ok")
        self.assertEqual(config.read_text(), original)
        self.assertFalse(manifest_path.exists())
        self.codex_version.assert_called_once()

    def test_guardian_takes_over_approval_fields_and_preserves_other_options(
        self,
    ) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            'model = "test-model"\n'
            'approval_policy = "never"\n'
            'approvals_reviewer = "user"\n'
            'web_search = "indexed"\n'
        )
        config.write_text(original)

        applied = self.run_sync("apply")

        self.assertEqual(applied["status"], "ok")
        installed = config.read_text()
        self.assertEqual(installed.count("approval_policy"), 1)
        self.assertEqual(installed.count("approvals_reviewer"), 1)
        self.assertIn('approval_policy = "on-request"', installed)
        self.assertIn('approvals_reviewer = "auto_review"', installed)
        self.assertNotIn('approvals_reviewer = "user"', installed)
        self.assertIn('default_permissions = ":workspace"', installed)
        self.assertIn('web_search = "indexed"', installed)
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(config.read_text(), original)

    def test_user_owned_sandbox_modes_block_without_mutation(
        self,
    ) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        for sandbox_mode in ("read-only", "workspace-write", "danger-full-access"):
            with self.subTest(sandbox_mode=sandbox_mode):
                original = (
                    'model = "test-model"\n'
                    f'sandbox_mode = "{sandbox_mode}"\n'
                )
                config.write_text(original)
                for action, dry_run in (
                    ("status", False),
                    ("apply", True),
                    ("apply", False),
                ):
                    result = self.run_sync(action, dry_run=dry_run)
                    self.assertEqual(result["status"], "blocked")
                    self.assertIn("sandbox_mode is user-owned", result["detail"])
                    self.assertEqual(config.read_text(), original)
                    self.assertFalse(
                        self.codex_home.joinpath("orchestra").exists()
                    )

    def test_clean_config_preserves_local_domain_rules(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            'model = "test-model"\n\n'
            "[features.network_proxy.domains]\n"
            '"codexbridge.local" = "allow"\n'
        )
        config.write_text(original)

        applied = self.run_sync("apply")

        self.assertEqual(applied["status"], "ok")
        installed = config.read_text()
        self.assertIn('approval_policy = "on-request"', installed)
        self.assertIn('approvals_reviewer = "auto_review"', installed)
        self.assertIn('default_permissions = ":workspace"', installed)
        self.assertIn('"codexbridge.local" = "allow"', installed)
        self.assertNotIn("[permissions.", installed)
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(config.read_text(), original)

    def test_user_permission_added_outside_owned_block_blocks_without_rewrite(
        self,
    ) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        config.write_text('model = "test-model"\n')
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        installed = config.read_bytes()
        marker = installed.index(sync.CONFIG_START)
        user_edited = (
            installed[:marker]
            + b'sandbox_mode = "read-only"\n'
            + installed[marker:]
        )
        config.write_bytes(user_edited)

        for action, dry_run in (("status", False), ("apply", True), ("apply", False)):
            result = self.run_sync(action, dry_run=dry_run)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("sandbox_mode is user-owned", result["detail"])
            self.assertEqual(config.read_bytes(), user_edited)

    def test_user_owned_permission_profile_blocks_without_mutation(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            'default_permissions = "personal"\n\n'
            "[permissions.personal]\n"
            'extends = ":workspace"\n'
        )
        config.write_text(original)

        result = self.run_sync("apply")

        self.assertEqual(result["status"], "blocked")
        self.assertIn("default_permissions is user-owned", result["detail"])
        self.assertEqual(config.read_text(), original)
        self.assertFalse(self.codex_home.joinpath("orchestra").exists())

    def test_unreadable_codex_version_blocks_before_any_mutation(self) -> None:
        self.codex_version.side_effect = sync.SyncError(
            "Codex returned an unsupported or unreadable version"
        )

        result = self.run_sync("apply")

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["codex_version"], "unknown")
        self.assertIn("unreadable version", result["detail"])
        self.assertFalse(self.home.exists())
        self.assertFalse(self.codex_home.exists())
        self.cache_discovery.assert_not_called()

    def test_uninstall_does_not_require_a_readable_codex_version(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        config = self.codex_home / "config.toml"
        self.codex_version.side_effect = sync.SyncError(
            "Codex returned an unsupported or unreadable version"
        )

        result = sync.uninstall(self.home, self.codex_home)

        self.assertEqual(result["status"], "ok")
        self.assertFalse(config.exists())
        self.assertFalse(
            self.manifest_path().exists()
        )
        self.codex_version.assert_called_once()

    def test_uninstall_preserves_unrelated_config_changes_after_apply(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = 'model = "test-model"\n'
        config.write_text(original)
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        with config.open("a") as stream:
            stream.write('\n[mcp_servers.example]\ncommand = "example-server"\n')

        removed = sync.uninstall(self.home, self.codex_home)

        self.assertEqual(removed["status"], "ok")
        restored = config.read_text()
        self.assertIn('model = "test-model"', restored)
        self.assertIn("[mcp_servers.example]", restored)
        self.assertIn('command = "example-server"', restored)
        self.assertNotIn("orchestra-workspace", restored)

    def test_codex_inserted_mcp_table_inside_marker_is_recovered(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        config = self.codex_home / "config.toml"
        installed = config.read_bytes()
        injected = (
            b"[mcp_servers.node_repl]\n"
            b'command = "node-repl"\n\n'
        )
        config.write_bytes(
            installed.replace(sync.CONFIG_END + b"\n", injected + sync.CONFIG_END + b"\n", 1)
        )

        status = self.run_sync("status")
        self.assertEqual(status["status"], "partial")
        self.assertNotIn("owned managed block drift", status.get("detail", ""))
        self.assertEqual(self.run_sync("apply")["status"], "ok")

        repaired = config.read_text()
        self.assertIn("mcp_servers.orchestra_tasks = {", repaired)
        self.assertNotIn("[mcp_servers.orchestra_tasks]", repaired)
        self.assertLess(
            repaired.index("# orchestra-worktree-root:end"),
            repaired.index("[mcp_servers.node_repl]"),
        )
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertIn("[mcp_servers.node_repl]", config.read_text())
        self.assertIn('command = "node-repl"', config.read_text())

    def test_permission_rewrite_preserves_multiline_strings_byte_for_byte(
        self,
    ) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            b'model = "test-model"\n'
            b'developer_instructions = """first line\n'
            b"\n"
            b"\n"
            b"[sandbox_workspace_write]\n"
            b"# orchestra-worktree-root:start\n"
            b"# orchestra-worktree-root:end\n"
            b'last line"""\n\n'
            b"[features]\n"
            b"example = true\n"
        )
        config.write_bytes(original)

        applied = self.run_sync("apply")

        self.assertEqual(applied["status"], "ok")
        installed = config.read_bytes()
        self.assertIn(
            b'first line\n\n\n[sandbox_workspace_write]\n'
            b"# orchestra-worktree-root:start\n"
            b"# orchestra-worktree-root:end\n"
            b'last line"""',
            installed,
        )
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(config.read_bytes(), original)

    def test_permission_rewrite_restores_config_without_final_newline(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = b'model = "test-model"'
        config.write_bytes(original)

        self.assertEqual(self.run_sync("apply")["status"], "ok")
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(config.read_bytes(), original)

    def test_status_returns_blocked_when_post_analysis_validation_fails(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        with mock.patch.object(
            sync,
            "_profile_is_configured",
            side_effect=sync.SyncError("config changed during status"),
        ):
            result = self.run_sync("status")

        self.assertEqual(result["status"], "blocked")
        self.assertIn("config changed during status", result["detail"])

    def test_apply_returns_partial_when_post_apply_validation_fails(self) -> None:
        with mock.patch.object(
            sync,
            "_profile_is_configured",
            side_effect=sync.SyncError("config changed after apply"),
        ):
            result = self.run_sync("apply")

        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["changes"])
        self.assertIn("config changed after apply", result["detail"])
        self.assertTrue(
            self.manifest_path().is_file()
        )

    def test_worktree_root_precedence_and_validation(self) -> None:
        default = sync._resolve_worktree_root(self.home, None)
        self.assertEqual(default, self.worktree_root)

        environment = self.home / "environment-root"
        explicit = self.home / "explicit-root"
        with mock.patch.dict(
            os.environ, {"ORCHESTRA_WORKTREE_ROOT": str(environment)}
        ):
            self.assertEqual(
                sync._resolve_worktree_root(self.home, None), environment
            )
            self.assertEqual(
                sync._resolve_worktree_root(self.home, explicit), explicit
            )
        with self.assertRaisesRegex(sync.SyncError, "must be absolute"):
            sync._resolve_worktree_root(self.home, "relative/worktrees")
        with self.assertRaisesRegex(sync.SyncError, "dedicated directory"):
            sync._resolve_worktree_root(self.home, self.home)

    def test_cache_root_validation_accepts_specific_home_caches(self) -> None:
        accepted = (
            self.home / "Library" / "Caches" / "pypoetry",
            self.home / "Library" / "Caches" / "pip",
            self.home / ".cache" / "uv",
            self.home / ".npm",
            self.home / ".orchestra" / "cache" / "poetry",
        )
        for candidate in accepted:
            with self.subTest(candidate=candidate):
                self.assertEqual(
                    sync._validate_cache_root(self.home, str(candidate)),
                    candidate,
                )

        rejected = (
            self.home,
            self.home / "Library" / "Caches",
            self.home / ".cache",
            self.home / ".docker" / "buildx",
            self.home / ".ssh" / "cache",
            self.home / ".codex" / "cache",
            self.home / "Library" / "Containers" / "com.docker.docker",
            self.home / "Library" / "Application Support" / "tool",
            Path(self.temporary.name) / "outside-cache",
        )
        for candidate in rejected:
            with self.subTest(candidate=candidate):
                with self.assertRaises(sync.SyncError):
                    sync._validate_cache_root(self.home, str(candidate))

        self.home.mkdir(parents=True)
        outside = Path(self.temporary.name) / "external"
        outside.mkdir()
        linked = self.home / "linked-cache"
        linked.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(sync.SyncError, "resolves outside"):
            sync._validate_cache_root(self.home, str(linked / "tool"))

    def test_cache_discovery_is_independent_and_omits_unsafe_results(self) -> None:
        outputs = {
            "poetry": str(self.home / "Library" / "Caches" / "pypoetry"),
            sys.executable: str(self.home / "Library" / "Caches" / "pip"),
            "uv": str(self.home / ".docker" / "buildx"),
        }

        def fake_which(executable: str) -> str | None:
            if executable == "npm":
                return None
            return f"/usr/bin/{executable}"

        def fake_run(command, **kwargs):
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=outputs[command[0]] + "\n",
                stderr="",
            )

        with (
            mock.patch.object(sync.shutil, "which", side_effect=fake_which),
            mock.patch.object(sync.subprocess, "run", side_effect=fake_run),
        ):
            discovered, omitted = self.original_cache_discovery(self.home)

        self.assertEqual(
            discovered,
            {
                "poetry": self.home / "Library" / "Caches" / "pypoetry",
                "pip": self.home / "Library" / "Caches" / "pip",
            },
        )
        self.assertEqual(
            omitted,
            {
                "npm": "not installed",
                "uv": "unsafe or invalid cache path",
            },
        )

    def test_pip_cache_discovery_retries_with_isolated_home(self) -> None:
        calls = 0

        def fake_run(command, **kwargs):
            nonlocal calls
            if command[0] != sys.executable:
                return subprocess.CompletedProcess(
                    command,
                    1,
                    stdout="",
                    stderr="unavailable",
                )
            calls += 1
            if calls == 1:
                return subprocess.CompletedProcess(
                    command,
                    1,
                    stdout="",
                    stderr="cache is disabled",
                )
            fallback_home = Path(kwargs["env"]["HOME"])
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=str(fallback_home / "Library" / "Caches" / "pip") + "\n",
                stderr="",
            )

        with (
            mock.patch.object(sync.shutil, "which", return_value="/usr/bin/tool"),
            mock.patch.object(sync.subprocess, "run", side_effect=fake_run),
        ):
            discovered, omitted = self.original_cache_discovery(self.home)

        self.assertEqual(
            discovered["pip"],
            self.home / "Library" / "Caches" / "pip",
        )
        self.assertNotIn("pip", omitted)
        self.assertEqual(calls, 2)

    def test_workspace_profile_reports_caches_without_adding_permission_roots(self) -> None:
        cache_roots = {
            "poetry": self.home / "Library" / "Caches" / "pypoetry",
            "pip": self.home / "Library" / "Caches" / "pip",
            "uv": self.home / ".cache" / "uv",
            "npm": self.home / ".npm",
        }
        self.cache_discovery.return_value = (cache_roots, {})

        applied = self.run_sync("apply")

        self.assertEqual(applied["status"], "ok")
        self.assertEqual(
            applied["cache_roots"],
            {tool: str(path) for tool, path in cache_roots.items()},
        )
        self.assertEqual(applied["omitted_cache_tools"], {})
        self.assertEqual(applied["unconfigured_cache_tools"], [])
        self.assertTrue(applied["restart_required"])
        config = (self.codex_home / "config.toml").read_text()
        self.assertIn('default_permissions = ":workspace"', config)
        for cache_root in cache_roots.values():
            self.assertNotIn(str(cache_root), config)
        self.assertNotIn(str(self.orchestra_root), config)
        status = self.run_sync("status")
        self.assertEqual(status["status"], "ok")
        self.assertFalse(status["restart_required"])

    def test_owned_legacy_worktree_block_migrates_to_guardian(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        config = self.codex_home / "config.toml"
        old_block = (
            sync.CONFIG_START
            + b"\n[sandbox_workspace_write]\n"
            + f'writable_roots = ["{self.worktree_root}"]\n'.encode()
            + sync.CONFIG_END
            + b"\n"
        )
        config.write_bytes(old_block)
        manifest_path = self.manifest_path()
        manifest = self.manifest()
        config_entry = next(
            entry for entry in manifest["entries"] if entry["path"] == "config.toml"
        )
        config_entry["digest"] = hashlib.sha256(old_block).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        migrated = self.run_sync("apply")

        self.assertEqual(migrated["status"], "ok")
        self.assertTrue(migrated["restart_required"])
        installed = config.read_text()
        self.assertIn('approval_policy = "on-request"', installed)
        self.assertIn('approvals_reviewer = "auto_review"', installed)
        self.assertIn('default_permissions = ":workspace"', installed)
        self.assertNotIn("writable_roots", installed)
        self.assertNotIn("orchestra-workspace", installed)
        self.assertEqual(self.run_sync("status")["status"], "ok")
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertFalse(config.exists())

    def test_user_owned_parent_root_blocks_when_detected_caches_change_scope(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            "[sandbox_workspace_write]\n"
            f'writable_roots = ["{self.orchestra_root}"]\n'
        )
        config.write_text(original)
        cache_roots = {
            "poetry": self.home / "Library" / "Caches" / "pypoetry",
            "uv": self.home / ".cache" / "uv",
        }
        self.cache_discovery.return_value = (cache_roots, {})

        applied = self.run_sync("apply")

        self.assertEqual(applied["status"], "blocked")
        self.assertEqual(applied["unconfigured_cache_tools"], [])
        self.assertIn("cannot be migrated without changing their scope", applied["detail"])
        self.assertFalse(applied["restart_required"])
        self.assertEqual(config.read_text(), original)
        self.assertFalse(self.codex_home.joinpath("orchestra").exists())

    def test_user_owned_network_access_blocks_without_mutation(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        for network_access in ("false", "true"):
            with self.subTest(network_access=network_access):
                original = (
                    'model = "test-model"\n\n'
                    "[sandbox_workspace_write]\n"
                    f"network_access = {network_access}\n\n"
                    "[features]\n"
                    "example = true\n"
                )
                config.write_text(original)

                for action, dry_run in (
                    ("status", False),
                    ("apply", True),
                    ("apply", False),
                ):
                    result = self.run_sync(action, dry_run=dry_run)
                    self.assertEqual(result["status"], "blocked")
                    self.assertIn(
                        "sandbox_workspace_write.network_access is user-owned",
                        result["detail"],
                    )
                    self.assertEqual(config.read_text(), original)
                    self.assertFalse(self.codex_home.joinpath("orchestra").exists())

    def test_user_owned_extra_writable_roots_block_without_rewrite(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            "[sandbox_workspace_write]\n"
            f'writable_roots = ["{self.worktree_root}", "/tmp/other"]\n'
        )
        config.write_text(original)

        applied = self.run_sync("apply")

        self.assertEqual(applied["status"], "blocked")
        self.assertIn("cannot be migrated without changing their scope", applied["detail"])
        self.assertEqual(config.read_text(), original)
        self.assertFalse(self.codex_home.joinpath("orchestra").exists())

    def test_conflicting_writable_roots_block_without_mutation(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = (
            "[sandbox_workspace_write]\n"
            'writable_roots = ["/tmp/user-owned"]\n'
        )
        config.write_text(original)

        result = self.run_sync("apply")

        self.assertEqual(result["status"], "blocked")
        self.assertIn(
            "cannot be migrated without changing their scope",
            result["detail"],
        )
        self.assertEqual(config.read_text(), original)
        self.assertFalse(self.codex_home.joinpath("orchestra").exists())

    def test_managed_root_switch_updates_only_worktree_root(self) -> None:
        self.codex_home.mkdir(parents=True)
        config = self.codex_home / "config.toml"
        original = 'model = "test-model"\n'
        config.write_text(original)
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        replacement = self.home / "alternate" / "worktrees"

        switched = sync.synchronize(
            ROOT,
            self.home,
            self.codex_home,
            "apply",
            modelconfig="native",
            worktree_root=replacement,
        )

        self.assertEqual(switched["status"], "ok")
        self.assertEqual(switched["worktree_root"], str(replacement))
        self.assertNotIn(str(replacement), config.read_text())
        self.assertNotIn(str(self.orchestra_root), config.read_text())
        self.assertNotIn(str(self.worktree_root), config.read_text())
        self.assertEqual(
            self.codex_home.joinpath("orchestra/worktree-root").read_text(),
            f"{replacement}\n",
        )
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(config.read_text(), original)


    def test_fresh_install_preserves_unmanaged_generic_agent_profiles(self) -> None:
        generic = self.codex_home / "agents/analyst.toml"
        generic.parent.mkdir(parents=True)
        generic.write_text("user-owned generic analyst\n")

        result = self.run_sync("apply")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(generic.read_text(), "user-owned generic analyst\n")
        self.assertTrue(
            self.codex_home.joinpath(
                "agents/orchestra_analyst.toml"
            ).is_file()
        )
        owned_paths = {
            entry["path"]
            for entry in self.manifest()["entries"]
            if entry["root"] == "codex_home"
        }
        self.assertNotIn("agents/analyst.toml", owned_paths)


    def seed_retired_install(self, mode: str) -> bytes:
        """Reproduce former manifest ownership without keeping its runtime."""
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest()
        manifest["modelconfig"] = mode
        roles = self.codex_home / "orchestra/roles.toml"
        content = b'[tiers.standard.example]\nmodel = "retired/model"\n'
        if mode == "dual":
            content = content.replace(b"[tiers.", b"[modes.external.tiers.")
        roles.write_bytes(content)
        for entry in manifest["entries"]:
            if entry["root"] == "codex_home" and entry["path"] == "orchestra/roles.toml":
                entry["digest"] = hashlib.sha256(content).hexdigest()
        for root_name, root, name, scope in (
            ("codex_home", self.codex_home, "orchestra/scripts/session_model.py", "codex"),
            ("orchestra_home", self.orchestra_root, "scripts/session_model.py", "shared"),
        ):
            helper = root / name
            helper.parent.mkdir(parents=True, exist_ok=True)
            helper.write_bytes(b"# Retired session helper\n")
            manifest["entries"].append({
                "root": root_name, "path": name, "scope": scope, "type": "file",
                "digest": hashlib.sha256(helper.read_bytes()).hexdigest(),
            })
        self.manifest_path().write_text(json.dumps(manifest))
        return content

    def test_fresh_install_defaults_to_native_without_selection(self) -> None:
        preview = self.run_sync("apply", dry_run=True)
        self.assertEqual(preview["status"], "partial")
        self.assertEqual(preview["modelconfig"], "native")
        self.assertFalse(self.home.exists())
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        self.assertEqual(self.manifest()["modelconfig"], "native")
        self.assertEqual(
            (self.codex_home / "orchestra/roles.toml").read_bytes(),
            (ROOT / "codex/config/roles.native.toml").read_bytes(),
        )

    def test_retired_selections_are_rejected_without_writes(self) -> None:
        for mode in ("external", "dual"):
            with self.subTest(mode=mode):
                result = self.run_sync("apply", modelconfig=mode)
                self.assertEqual(result["status"], "blocked")
                self.assertIn("unknown model configuration", result["detail"])
                self.assertFalse(self.home.exists())

    def test_retired_install_migrates_owned_resources_to_native(self) -> None:
        for mode in ("external", "dual"):
            with self.subTest(mode=mode):
                previous = self.seed_retired_install(mode)
                roles = self.codex_home / "orchestra/roles.toml"
                manifest_before = self.manifest_path().read_bytes()
                for action, dry_run in (("status", False), ("apply", True)):
                    result = self.run_sync(action, dry_run=dry_run)
                    self.assertEqual(result["status"], "partial")
                    self.assertEqual(result["modelconfig"], "native")
                    self.assertEqual(roles.read_bytes(), previous)
                    self.assertEqual(self.manifest_path().read_bytes(), manifest_before)
                migrated = self.run_sync("apply")
                self.assertEqual(migrated["status"], "ok", migrated)
                self.assertEqual(self.manifest()["modelconfig"], "native")
                self.assertEqual(roles.read_bytes(), (ROOT / "codex/config/roles.native.toml").read_bytes())
                self.assertFalse((self.codex_home / "orchestra/scripts/session_model.py").exists())
                self.assertFalse((self.orchestra_root / "scripts/session_model.py").exists())
                self.assertEqual(
                    (self.codex_home / "orchestra/backups/codex_home/orchestra/roles.toml").read_bytes(),
                    previous,
                )
                self.assertEqual(self.run_sync("status")["status"], "ok")
                self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")

    def test_retired_helper_drift_blocks_migration_without_mutation(self) -> None:
        self.seed_retired_install("dual")
        helper = self.orchestra_root / "scripts/session_model.py"
        helper.write_text("# User changes\n")
        before = {
            p: p.read_bytes() for p in self.temporary_path_files()
        }
        result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual(before, {p: p.read_bytes() for p in self.temporary_path_files()})

    def temporary_path_files(self) -> list[Path]:
        return [p for p in Path(self.temporary.name).rglob("*") if p.is_file()]

    def test_retired_install_can_be_uninstalled_without_migration(self) -> None:
        self.seed_retired_install("external")
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertFalse(self.manifest_path().exists())
        self.assertFalse((self.codex_home / "orchestra/scripts/session_model.py").exists())

    def test_other_host_sync_preserves_retired_codex_selection(self) -> None:
        original = self.seed_retired_install("dual")
        for host in ("cursor", "grok", "devin"):
            with self.subTest(host=host):
                result = self.run_sync("apply", host=host)
                self.assertEqual(result["status"], "ok", result)
                self.assertEqual(self.manifest()["modelconfig"], "dual")
                self.assertEqual((self.codex_home / "orchestra/roles.toml").read_bytes(), original)
                self.assertTrue((self.codex_home / "orchestra/scripts/session_model.py").exists())
        self.assertEqual(self.run_sync("apply", host="all")["status"], "ok")
        self.assertEqual(self.manifest()["modelconfig"], "native")
        self.assertEqual(self.run_sync("status", host="all")["status"], "ok")

    def test_legacy_manifest_without_selection_defaults_to_native(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest()
        manifest.pop("modelconfig")
        self.manifest_path().write_text(json.dumps(manifest))
        result = self.run_sync("apply")
        self.assertEqual(result["status"], "ok", result)
        self.assertEqual(self.manifest()["modelconfig"], "native")

    def test_failed_migration_restores_roles_and_manifest(self) -> None:
        previous = self.seed_retired_install("dual")
        manifest_before = self.manifest_path().read_bytes()
        with mock.patch.object(sync, "_write_manifest", side_effect=OSError("injected migration failure")):
            result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked", result)
        self.assertEqual((self.codex_home / "orchestra/roles.toml").read_bytes(), previous)
        self.assertEqual(self.manifest_path().read_bytes(), manifest_before)
        self.assertEqual(self.manifest()["modelconfig"], "dual")

    def test_legacy_manifest_remains_uninstallable_without_selection(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest()
        manifest.pop("modelconfig")
        (self.manifest_path()).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        removed = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(removed["status"], "ok")
        self.assertFalse(
            self.manifest_path().exists()
        )

    def test_invalid_modelconfig_and_manifest_selection_block(self) -> None:
        invalid = self.run_sync("status", modelconfig="unsupported")
        self.assertEqual(invalid["status"], "blocked")
        self.assertIn("unknown model configuration", invalid["detail"])

        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest()
        manifest["modelconfig"] = "unsupported"
        (self.manifest_path()).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        status = self.run_sync("status")
        self.assertEqual(status["status"], "blocked")
        self.assertIn("invalid install manifest modelconfig", status["detail"])

        manifest["modelconfig"] = "native"
        manifest["checkout_mode"] = "unsupported"
        (self.manifest_path()).write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        status = self.run_sync("status")
        self.assertEqual(status["status"], "blocked")
        self.assertIn("invalid install manifest checkout mode", status["detail"])


    def test_dry_run_is_a_zero_mutation_full_preview(self) -> None:
        preview = self.run_sync("apply", dry_run=True)
        self.assertEqual(preview["status"], "partial")
        self.assertGreater(len(preview["changes"]), 20)
        self.assertFalse(self.home.exists())
        self.assertFalse(self.codex_home.exists())

    def test_apply_preserves_unrelated_agents_content_and_uninstall_removes_only_block(self) -> None:
        self.codex_home.mkdir(parents=True)
        agents = self.codex_home / "AGENTS.md"
        original = b"# Personal rules\n\nKeep this text.\n"
        agents.write_bytes(original)
        agents.chmod(0o640)

        self.assertEqual(self.run_sync("apply")["status"], "ok")
        installed = agents.read_bytes()
        self.assertIn(sync.START, installed)
        self.assertTrue(installed.endswith(original))
        self.assertEqual(agents.stat().st_mode & 0o777, 0o640)
        agents.write_bytes(installed + b"\nPost-install user edit.\n")

        removed = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(removed["status"], "ok")
        self.assertEqual(agents.read_bytes(), original + b"\nPost-install user edit.\n")
        self.assertEqual(agents.stat().st_mode & 0o777, 0o640)

    def test_unmanaged_file_and_markers_block_without_mutation(self) -> None:
        collision = self.home / ".agents/skills/orchestra/SKILL.md"
        collision.parent.mkdir(parents=True)
        collision.write_bytes(ROOT.joinpath("codex/skills/orchestra/SKILL.md").read_bytes())
        before = collision.read_bytes()
        result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(collision.read_bytes(), before)
        self.assertFalse(self.codex_home.exists())

        collision.unlink()
        self.codex_home.mkdir(parents=True)
        agents = self.codex_home / "AGENTS.md"
        agents.write_bytes(sync.START + b"\nforeign\n" + sync.END + b"\n")
        result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked")
        for malformed in (
            sync.START + b"\none\n" + sync.END + b"\n" + sync.START + b"\ntwo\n" + sync.END + b"\n",
            sync.END + b"\nforeign\n" + sync.START + b"\n",
        ):
            agents.write_bytes(malformed)
            self.assertEqual(self.run_sync("apply")["status"], "blocked")

    def test_owned_drift_blocks_apply_and_is_preserved_by_uninstall(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        drifted = self.codex_home / "agents/orchestra_reviewer.toml"
        drifted.write_text("user edit\n")
        self.assertEqual(self.run_sync("status")["status"], "blocked")
        self.assertEqual(self.run_sync("apply")["status"], "blocked")

        result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(drifted.read_text(), "user edit\n")
        remaining = self.manifest()["entries"]
        self.assertEqual(
            [entry["path"] for entry in remaining],
            ["agents/orchestra_reviewer.toml"],
        )

    def test_uninstall_retains_missing_entry_and_removes_all_safe_entries(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest_before = self.manifest()["entries"]
        retained = next(
            entry
            for entry in manifest_before
            if entry["path"] == "agents/orchestra_analyst.toml"
        )
        missing = self.codex_home / retained["path"]
        missing.unlink()

        result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "partial")
        self.assertIn("agents/orchestra_analyst.toml", result["detail"])
        self.assertEqual(self.manifest()["entries"], [retained])
        self.assertFalse(
            self.codex_home.joinpath("agents/orchestra_reviewer.toml").exists()
        )
        self.assertFalse(self.home.joinpath(".agents/skills/orchestra/SKILL.md").exists())

    def test_uninstall_retains_malformed_block_and_removes_safe_files(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        retained = next(
            entry for entry in self.manifest()["entries"] if entry["path"] == "AGENTS.md"
        )
        agents = self.codex_home / "AGENTS.md"
        malformed = sync.START + b"\none\n" + sync.START + b"\ntwo\n" + sync.END + b"\n"
        agents.write_bytes(malformed)

        result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "partial")
        self.assertIn("markers must appear exactly once", result["detail"])
        self.assertEqual(agents.read_bytes(), malformed)
        self.assertEqual(self.manifest()["entries"], [retained])
        self.assertFalse(
            self.codex_home.joinpath("agents/orchestra_reviewer.toml").exists()
        )

    def test_invalid_manifest_paths_and_destination_symlinks_block(self) -> None:
        manifest = self.manifest_path()
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"entries": [{
            "digest": "0" * 64,
            "path": "../outside",
            "root": "codex_home",
            "type": "file",
        }]}))
        self.assertEqual(self.run_sync("status")["status"], "blocked")

        manifest.unlink()
        external = Path(self.temporary.name) / "external"
        external.mkdir()
        self.codex_home.mkdir(parents=True, exist_ok=True)
        (self.codex_home / "agents").symlink_to(external, target_is_directory=True)
        self.assertEqual(self.run_sync("apply")["status"], "blocked")
        self.assertEqual(list(external.iterdir()), [])

    def test_subprocess_contract_uses_only_explicit_temporary_destinations(self) -> None:
        env = self.subprocess_environment()
        env["HOME"] = str(self.home)
        env["CODEX_HOME"] = str(self.codex_home)
        env.pop("ORCHESTRA_WORKTREE_ROOT", None)
        commands = (
            ("status",),
            ("status", "--modelconfig", "native"),
            ("apply", "--dry-run", "--modelconfig", "native"),
            ("apply", "--modelconfig", "native"),
            ("status",),
            ("uninstall",),
        )
        statuses = []
        for arguments in commands:
            result = subprocess.run(
                [sys.executable, str(SYNC_PATH), *arguments],
                cwd=ROOT,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            statuses.append(json.loads(result.stdout)["status"])
        self.assertEqual(
            statuses, ["partial", "partial", "partial", "ok", "ok", "ok"]
        )

    def test_subprocess_defaults_codex_home_and_installed_helper_resolves(self) -> None:
        env = self.subprocess_environment()
        env["HOME"] = str(self.home)
        env.pop("CODEX_HOME", None)
        env.pop("ORCHESTRA_WORKTREE_ROOT", None)
        applied = subprocess.run(
            [
                sys.executable,
                str(SYNC_PATH),
                "apply",
                "--modelconfig",
                "native",
            ],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(applied.returncode, 0, applied.stderr or applied.stdout)
        default_codex_home = self.home / ".codex"
        helper = default_codex_home / "orchestra/scripts/policy.py"
        self.assertTrue(helper.is_file())
        installed_skill = self.home / ".agents/skills/orchestra"
        self.assertIn("(runtime.md)", (installed_skill / "SKILL.md").read_text())
        self.assertEqual(
            (installed_skill / "runtime.md").read_bytes(),
            (ROOT / "codex/skills/orchestra/runtime.md").read_bytes(),
        )
        resolved = subprocess.run(
            [sys.executable, str(helper), "--repo", str(ROOT), "show"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(resolved.returncode, 0, resolved.stderr or resolved.stdout)
        self.assertEqual(json.loads(resolved.stdout)["status"], "ok")
        removed = subprocess.run(
            [sys.executable, str(SYNC_PATH), "uninstall"],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(removed.returncode, 0, removed.stderr or removed.stdout)

    def test_subprocess_worktree_root_flag_overrides_environment(self) -> None:
        env = self.subprocess_environment()
        env["HOME"] = str(self.home)
        env["CODEX_HOME"] = str(self.codex_home)
        environment_root = self.home / "from-environment"
        explicit_root = self.home / "from-flag"
        env["ORCHESTRA_WORKTREE_ROOT"] = str(environment_root)

        result = subprocess.run(
            [
                sys.executable,
                str(SYNC_PATH),
                "apply",
                "--dry-run",
                "--modelconfig",
                "native",
                "--worktree-root",
                str(explicit_root),
            ],
            cwd=ROOT,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["worktree_root"], str(explicit_root))
        self.assertFalse(self.home.exists())
        self.assertFalse(self.codex_home.exists())

    def test_mid_apply_failure_records_exact_successful_ownership(self) -> None:
        original = sync._apply_operation
        calls = 0

        def fail_second(*args: object, **kwargs: object) -> object:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected write failure")
            return original(*args, **kwargs)

        with mock.patch.object(sync, "_apply_operation", side_effect=fail_second):
            result = self.run_sync("apply")
        self.assertEqual(result["status"], "partial")
        entries = self.manifest()["entries"]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        root = self.home if entry["root"] == "home" else self.codex_home
        data = root.joinpath(entry["path"]).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), entry["digest"])
        self.assertEqual(self.run_sync("status")["status"], "partial")
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertFalse(self.manifest_path().exists())

    def test_upgrade_backs_up_current_content_and_removes_stale_owned_files(self) -> None:
        source = self.source_fixture()
        extra_source = source / "codex/skills/orchestra/notes.txt"
        extra_source.write_text("owned extra\n")
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )["status"],
            "ok",
        )
        installed_skill = self.home / ".agents/skills/orchestra/SKILL.md"
        previous = installed_skill.read_bytes()
        skill_source = source / "codex/skills/orchestra/SKILL.md"
        skill_source.write_bytes(previous + b"\nUpgrade fixture.\n")
        extra_source.unlink()

        preview = sync.synchronize(
            source,
            self.home,
            self.codex_home,
            "apply",
            dry_run=True,
            modelconfig="native",
        )
        self.assertEqual(preview["status"], "partial")
        self.assertEqual(
            {(change["operation"], change["path"]) for change in preview["changes"]},
            {("update", ".agents/skills/orchestra/SKILL.md"), ("delete", ".agents/skills/orchestra/notes.txt")},
        )
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )["status"],
            "ok",
        )
        backup = self.orchestra_root / "orchestra/backups/home/.agents/skills/orchestra/SKILL.md"
        self.assertEqual(backup.read_bytes(), previous)
        self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
        self.assertFalse(self.home.joinpath(".agents/skills/orchestra/notes.txt").exists())
        self.assertFalse(
            self.orchestra_root.joinpath(
                "orchestra/backups/home/.agents/skills/orchestra/notes.txt"
            ).exists()
        )
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "status",
                modelconfig="native",
            )["status"],
            "ok",
        )

    def test_legacy_to_namespaced_upgrade_removes_only_owned_profiles(self) -> None:
        self.convert_current_install_to_legacy_profile_manifest()
        installed_agents = {
            entry["path"]
            for entry in self.manifest()["entries"]
            if entry["path"].startswith("agents/")
        }
        self.assertEqual(
            installed_agents,
            {f"agents/{name}.toml" for name in sync.LEGACY_AGENTS},
        )

        preview = self.run_sync("apply", dry_run=True)
        self.assertEqual(preview["status"], "partial")
        agent_changes = {
            (change["operation"], change["path"])
            for change in preview["changes"]
            if change["path"].startswith("agents/")
        }
        self.assertEqual(
            agent_changes,
            {
                *(("create", f"agents/{name}.toml") for name in sync.AGENTS),
                *(("delete", f"agents/{name}.toml") for name in sync.LEGACY_AGENTS),
            },
        )
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        for name in sync.AGENTS:
            self.assertTrue(self.codex_home.joinpath(f"agents/{name}.toml").is_file())
        for name in sync.LEGACY_AGENTS:
            self.assertFalse(self.codex_home.joinpath(f"agents/{name}.toml").exists())

        unowned = self.codex_home / "agents/browser_acceptance_tester.toml"
        unowned.write_text("unowned user file\n")
        self.assertEqual(self.run_sync("status")["status"], "ok")
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(unowned.read_text(), "unowned user file\n")

    def test_drifted_retired_profile_blocks_upgrade_without_partial_deletion(self) -> None:
        self.convert_current_install_to_legacy_profile_manifest()
        drifted = self.codex_home / "agents/browser_acceptance_tester.toml"
        drifted.write_text("user edit\n")
        result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("owned destination drift", result["detail"])
        for name in sync.AGENTS:
            self.assertFalse(self.codex_home.joinpath(f"agents/{name}.toml").exists())
        for name in sync.LEGACY_AGENTS:
            self.assertTrue(self.codex_home.joinpath(f"agents/{name}.toml").exists())

    def test_source_symlinks_and_malformed_marker_sources_block(self) -> None:
        source = self.source_fixture()
        target = Path(self.temporary.name) / "outside-source"
        target.write_text("outside")
        (source / "codex/skills/orchestra/link.txt").symlink_to(target)
        result = sync.synchronize(
            source,
            self.home,
            self.codex_home,
            "apply",
            modelconfig="native",
        )
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(self.home.exists())
        (source / "codex/skills/orchestra/link.txt").unlink()

        runtime = source / "codex/runtime/AGENTS.orchestra.md"
        runtime.write_bytes(sync.START + b"\n" + sync.START + b"\n" + sync.END + b"\n")
        result = sync.synchronize(
            source,
            self.home,
            self.codex_home,
            "apply",
            modelconfig="native",
        )
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(self.home.exists())

    def test_managed_block_upgrade_preserves_outside_edits(self) -> None:
        source = self.source_fixture()
        self.codex_home.mkdir(parents=True)
        agents = self.codex_home / "AGENTS.md"
        original = b"Personal rules.\n"
        agents.write_bytes(original)
        agents.chmod(0o640)
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )["status"],
            "ok",
        )
        agents.write_bytes(agents.read_bytes() + b"Later outside edit.\n")
        runtime = source / "codex/runtime/AGENTS.orchestra.md"
        runtime.write_bytes(runtime.read_bytes().replace(sync.END, b"New routing line.\n" + sync.END))

        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )["status"],
            "ok",
        )
        current = agents.read_bytes()
        self.assertIn(b"New routing line.", current)
        self.assertTrue(current.endswith(original + b"Later outside edit.\n"))
        self.assertEqual(agents.stat().st_mode & 0o777, 0o640)
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(agents.read_bytes(), original + b"Later outside edit.\n")
        self.assertEqual(agents.stat().st_mode & 0o777, 0o640)

    def test_destination_root_symlink_and_unmanaged_backup_block(self) -> None:
        external = Path(self.temporary.name) / "external-home"
        external.mkdir()
        self.home.symlink_to(external, target_is_directory=True)
        result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(list(external.iterdir()), [])
        self.home.unlink()

        self.assertEqual(self.run_sync("apply")["status"], "ok")
        backup = (
            self.codex_home
            / "orchestra/backups/codex_home/agents/orchestra_reviewer.toml"
        )
        backup.parent.mkdir(parents=True)
        backup.write_text("unmanaged backup")
        result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "partial")
        self.assertTrue(
            self.codex_home.joinpath("agents/orchestra_reviewer.toml").exists()
        )
        self.assertEqual(backup.read_text(), "unmanaged backup")

    def test_persistent_first_manifest_failure_restores_unowned_destination(self) -> None:
        with mock.patch.object(
            sync, "_write_manifest", side_effect=OSError("persistent manifest failure")
        ):
            result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(self.codex_home.joinpath("AGENTS.md").exists())
        self.assertFalse(self.manifest_path().exists())
        self.assertEqual(self.run_sync("status")["status"], "partial")

    def test_persistent_second_manifest_failure_keeps_exact_first_ownership(self) -> None:
        original = sync._write_manifest
        calls = 0

        def fail_from_second(*args: object, **kwargs: object) -> object:
            nonlocal calls
            calls += 1
            if calls >= 2:
                raise OSError("persistent manifest failure")
            return original(*args, **kwargs)

        with mock.patch.object(sync, "_write_manifest", side_effect=fail_from_second):
            result = self.run_sync("apply")
        self.assertEqual(result["status"], "partial")
        entries = self.manifest()["entries"]
        self.assertEqual([entry["path"] for entry in entries], ["AGENTS.md"])
        self.assertTrue(self.codex_home.joinpath("AGENTS.md").is_file())
        self.assertFalse(
            self.codex_home.joinpath("agents/orchestra_analyst.toml").exists()
        )
        self.assertEqual(self.run_sync("status")["status"], "partial")
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertFalse(self.manifest_path().exists())

    def test_persistent_uninstall_manifest_failure_restores_destination(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest_path()
        manifest_before = manifest.read_bytes()
        agents = self.codex_home / "AGENTS.md"
        agents_before = agents.read_bytes()
        with mock.patch.object(
            sync, "_write_manifest", side_effect=OSError("persistent manifest failure")
        ):
            result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(manifest.read_bytes(), manifest_before)
        self.assertEqual(agents.read_bytes(), agents_before)
        self.assertFalse(
            self.codex_home.joinpath("orchestra/backups/codex_home/AGENTS.md").exists()
        )
        self.assertEqual(self.run_sync("status")["status"], "ok")

    def test_apply_stale_backup_cleanup_failure_restores_exact_state(self) -> None:
        source = self.source_fixture()
        extra_source = source / "codex/skills/orchestra/notes.txt"
        extra_source.write_text("owned extra\n")
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )["status"],
            "ok",
        )
        destination = self.home / ".agents/skills/orchestra/notes.txt"
        manifest = self.manifest_path()
        destination_before = destination.read_bytes()
        manifest_before = manifest.read_bytes()
        backup = self.orchestra_root / "orchestra/backups/home/.agents/skills/orchestra/notes.txt"
        extra_source.unlink()

        original_cleanup = sync._cleanup_operation_backup

        def cleanup_then_fail(*args: object, **kwargs: object) -> None:
            original_cleanup(*args, **kwargs)
            raise OSError("injected backup cleanup failure")

        with mock.patch.object(
            sync,
            "_cleanup_operation_backup",
            side_effect=cleanup_then_fail,
        ):
            result = sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(destination.read_bytes(), destination_before)
        self.assertEqual(manifest.read_bytes(), manifest_before)
        self.assertFalse(backup.exists())

    def test_apply_stale_manifest_failure_restores_prior_backup_and_destination(self) -> None:
        source = self.source_fixture()
        extra_source = source / "codex/skills/orchestra/notes.txt"
        extra_source.write_text("version one\n")
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )["status"],
            "ok",
        )
        extra_source.write_text("version two\n")
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )["status"],
            "ok",
        )
        destination = self.home / ".agents/skills/orchestra/notes.txt"
        backup = self.orchestra_root / "orchestra/backups/home/.agents/skills/orchestra/notes.txt"
        manifest = self.manifest_path()
        destination_before = destination.read_bytes()
        backup_before = backup.read_bytes()
        manifest_before = manifest.read_bytes()
        extra_source.unlink()

        with mock.patch.object(
            sync, "_write_manifest", side_effect=OSError("persistent manifest failure")
        ):
            result = sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "apply",
                modelconfig="native",
            )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(destination.read_bytes(), destination_before)
        self.assertEqual(backup.read_bytes(), backup_before)
        self.assertEqual(manifest.read_bytes(), manifest_before)

    def test_uninstall_backup_cleanup_failure_restores_exact_state(self) -> None:
        self.codex_home.mkdir(parents=True)
        agents = self.codex_home / "AGENTS.md"
        agents.write_bytes(b"Personal rules.\n")
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        backup = self.codex_home / "orchestra/backups/codex_home/AGENTS.md"
        manifest = self.manifest_path()
        agents_before = agents.read_bytes()
        backup_before = backup.read_bytes()
        manifest_before = manifest.read_bytes()

        with mock.patch.object(
            sync,
            "_cleanup_operation_backup",
            side_effect=OSError("injected backup cleanup failure"),
        ):
            result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(agents.read_bytes(), agents_before)
        self.assertEqual(backup.read_bytes(), backup_before)
        self.assertEqual(manifest.read_bytes(), manifest_before)

    def test_missing_referenced_backup_is_partial_but_uninstall_remains_safe(self) -> None:
        self.codex_home.mkdir(parents=True)
        agents = self.codex_home / "AGENTS.md"
        original = b"Personal rules.\n"
        agents.write_bytes(original)
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        backup = self.codex_home / "orchestra/backups/codex_home/AGENTS.md"
        self.assertTrue(backup.is_file())
        backup.unlink()

        status = self.run_sync("status")
        self.assertEqual(status["status"], "partial")
        self.assertEqual(
            status["detail"],
            "referenced backup is missing: orchestra/backups/codex_home/AGENTS.md",
        )
        self.assertEqual(self.run_sync("apply")["status"], "partial")
        self.assertEqual(sync.uninstall(self.home, self.codex_home)["status"], "ok")
        self.assertEqual(agents.read_bytes(), original)

    def test_execution_preset_resolves_from_each_install_and_is_owned_on_uninstall(self) -> None:
        for host in ("codex", "cursor", "grok", "all"):
            with self.subTest(host=host):
                result = self.run_sync("apply", host=host,
                                       modelconfig="native" if host in ("codex", "all") else None)
                self.assertEqual(result["status"], "ok", result)
                locations = [self.orchestra_root]
                if host in ("codex", "all"):
                    locations.append(self.codex_home / "orchestra")
                for location in locations:
                    preset = location / "execution-presets.toml"
                    self.assertEqual(preset.read_bytes(), (ROOT / "codex/config/execution-presets.toml").read_bytes())
                    resolved = subprocess.run([
                        sys.executable, str(location / "scripts/delegate.py"),
                        "--preset", "standard-delegate", "--host", "codex" if host == "all" else host,
                        "--capability", "independent_review", "--resolve-only",
                    ], cwd=self.home, capture_output=True, text=True, check=False)
                    self.assertEqual(resolved.returncode, 0, resolved.stdout + resolved.stderr)
                    self.assertEqual(json.loads(resolved.stdout)["model"], "claude-fable-5-1-thinking-medium")
                removed = sync.uninstall(self.home, self.codex_home, host=host)
                self.assertEqual(removed["status"], "ok", removed)
                for location in locations:
                    self.assertFalse((location / "execution-presets.toml").exists())

    def test_cursor_host_installs_adapter_without_codex_config(self) -> None:
        preview = self.run_sync(
            "apply", dry_run=True, modelconfig=None, host="cursor"
        )
        self.assertEqual(preview["status"], "partial")
        self.assertIsNone(preview.get("codex_version"))
        self.assertFalse(self.codex_home.exists())
        applied = self.run_sync("apply", modelconfig=None, host="cursor")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        self.assertTrue(self.orchestra_root.joinpath("scripts/task_mcp.py").is_file())
        self.assertTrue(
            self.orchestra_root.joinpath("control/orchestra_control/cli.py").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("hosts/cursor/roles.toml").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("hosts/cursor/spawn.md").is_file()
        )
        self.assertTrue(
            self.home.joinpath(
                ".cursor/plugins/local/orchestra/.cursor-plugin/plugin.json"
            ).is_file()
        )
        mcp = json.loads(
            self.home.joinpath(".cursor/plugins/local/orchestra/mcp.json").read_text()
        )
        self.assertEqual(
            mcp["mcpServers"]["orchestra_tasks"]["args"],
            [str(self.orchestra_root / "scripts" / "task_mcp.py")],
        )
        self.assertFalse(self.codex_home.joinpath("config.toml").exists())
        self.assertFalse(self.codex_home.joinpath("orchestra/roles.toml").exists())
        roles = self.orchestra_root.joinpath("hosts/cursor/roles.toml").read_text()
        self.assertIn("[tiers.minimal.independent_review]", roles)
        self.assertIn("[tiers.standard.independent_review]", roles)
        self.assertIn("[tiers.critical.independent_review]", roles)
        self.assertFalse(self.legacy_manifest_path().exists())
        self.assertTrue((self.orchestra_root / "install-manifest.json").is_file())
        removed = sync.uninstall(self.home, self.codex_home, host="cursor")
        self.assertEqual(removed["status"], "ok", removed.get("detail"))
        self.assertFalse(
            self.home.joinpath(".cursor/plugins/local/orchestra/mcp.json").exists()
        )

    def test_manifest_v2_tracks_host_and_shared_ownership(self) -> None:
        applied = self.run_sync("apply", host="all")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        manifest = self.manifest()
        self.assertEqual(manifest["schema_version"], sync.MANIFEST_SCHEMA_VERSION)
        self.assertEqual(
            manifest["installed_hosts"], ["codex", "cursor", "devin", "grok"]
        )
        scopes = {entry["scope"] for entry in manifest["entries"]}
        self.assertEqual(scopes, {"shared", "codex", "cursor", "devin", "grok"})
        self.assertFalse(self.legacy_manifest_path().exists())
        for selected in ("codex", "cursor", "grok", "devin", "all"):
            with self.subTest(host=selected):
                status = self.run_sync(
                    "status",
                    host=selected,
                    modelconfig="native" if selected in {"codex", "all"} else None,
                )
                self.assertEqual(status["status"], "ok", status.get("detail"))

    def test_host_transitions_and_partial_uninstall_preserve_other_host(self) -> None:
        self.assertEqual(self.run_sync("apply", host="codex")["status"], "ok")
        self.assertEqual(
            self.run_sync("apply", host="cursor", modelconfig=None)["status"],
            "ok",
        )
        self.assertEqual(self.manifest()["installed_hosts"], ["codex", "cursor"])

        removed_cursor = sync.uninstall(self.home, self.codex_home, host="cursor")
        self.assertEqual(removed_cursor["status"], "ok", removed_cursor.get("detail"))
        self.assertEqual(self.manifest()["installed_hosts"], ["codex"])
        self.assertTrue(self.codex_home.joinpath("orchestra/roles.toml").is_file())
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        self.assertTrue(
            self.orchestra_root.joinpath("control/orchestra_control/db.py").is_file()
        )
        self.assertFalse(
            self.home.joinpath(".cursor/plugins/local/orchestra/mcp.json").exists()
        )

        self.assertEqual(
            self.run_sync("apply", host="cursor", modelconfig=None)["status"],
            "ok",
        )
        removed_codex = sync.uninstall(self.home, self.codex_home, host="codex")
        self.assertEqual(removed_codex["status"], "ok", removed_codex.get("detail"))
        self.assertEqual(self.manifest()["installed_hosts"], ["cursor"])
        self.assertFalse(self.codex_home.joinpath("config.toml").exists())
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        self.assertTrue(
            self.home.joinpath(".cursor/plugins/local/orchestra/mcp.json").is_file()
        )

    def test_grok_host_installs_adapter_without_codex_config(self) -> None:
        preview = self.run_sync(
            "apply", dry_run=True, modelconfig=None, host="grok"
        )
        self.assertEqual(preview["status"], "partial")
        self.assertIsNone(preview.get("codex_version"))
        self.assertFalse(self.codex_home.exists())
        applied = self.run_sync("apply", modelconfig=None, host="grok")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        self.assertTrue(self.orchestra_root.joinpath("scripts/task_mcp.py").is_file())
        self.assertTrue(
            self.orchestra_root.joinpath("control/orchestra_control/mcp.py").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("hosts/grok/roles.toml").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("hosts/grok/spawn.md").is_file()
        )
        self.assertFalse(self.codex_home.joinpath("config.toml").exists())
        self.assertFalse(self.codex_home.joinpath("orchestra/roles.toml").exists())
        self.assertFalse(
            self.home.joinpath(".cursor/plugins/local/orchestra/mcp.json").exists()
        )
        roles = self.orchestra_root.joinpath("hosts/grok/roles.toml").read_text()
        self.assertIn("[tiers.standard.independent_review]", roles)
        self.assertIn("[tiers.critical.independent_review]", roles)
        self.assertNotIn("[tiers.minimal.", roles)
        self.assertIn('model = "grok-4.6"', roles)
        self.assertFalse(self.legacy_manifest_path().exists())
        removed = sync.uninstall(self.home, self.codex_home, host="grok")
        self.assertEqual(removed["status"], "ok", removed.get("detail"))
        self.assertFalse(self.orchestra_root.joinpath("hosts/grok/roles.toml").exists())

    def test_devin_host_installs_adapter_without_codex_config(self) -> None:
        preview = self.run_sync(
            "apply", dry_run=True, modelconfig=None, host="devin"
        )
        self.assertEqual(preview["status"], "partial")
        self.assertIsNone(preview.get("codex_version"))
        self.assertFalse(self.codex_home.exists())
        self.assertFalse(self.home.exists())
        applied = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        self.assertTrue(applied["restart_required"])
        self.assertTrue(
            self.home.joinpath(".config/devin/skills/orchestra/SKILL.md").is_file()
        )
        self.assertTrue(
            self.home.joinpath(".config/devin/skills/orchestra-lite/SKILL.md").is_file()
        )
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        for name in sync.AGENTS:
            self.assertTrue(
                self.home.joinpath(f".config/devin/agents/{name}.md").is_file(), name
            )
        self.assertTrue(self.orchestra_root.joinpath("scripts/task_mcp.py").is_file())
        self.assertTrue(
            self.orchestra_root.joinpath("hosts/devin/roles.toml").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("hosts/devin/spawn.md").is_file()
        )
        self.assertTrue(
            self.orchestra_root.joinpath("hosts/devin/session_identity.py").is_file()
        )
        config = json.loads(
            self.home.joinpath(".config/devin/config.json").read_text()
        )
        session_start = config["hooks"]["SessionStart"]
        self.assertEqual(len(session_start), 1)
        self.assertEqual(session_start[0]["matcher"], "")
        hook = session_start[0]["hooks"][0]
        self.assertEqual(hook["type"], "command")
        self.assertEqual(
            hook["command"],
            f'python3 "{self.orchestra_root}/hosts/devin/session_identity.py"',
        )
        self.assertFalse(self.codex_home.joinpath("config.toml").exists())
        self.assertFalse(self.codex_home.joinpath("orchestra/roles.toml").exists())
        roles = self.orchestra_root.joinpath("hosts/devin/roles.toml").read_text()
        self.assertIn("[tiers.standard.independent_review]", roles)
        self.assertIn("[tiers.critical.independent_review]", roles)
        self.assertNotIn("[tiers.minimal.", roles)
        self.assertFalse(self.legacy_manifest_path().exists())
        self.assertTrue((self.orchestra_root / "install-manifest.json").is_file())
        devin_paths = {
            entry["path"]
            for entry in self.manifest()["entries"]
            if entry["scope"] == "devin"
        }
        self.assertIn(".config/devin/config.json", devin_paths)
        self.assertIn("hosts/devin/roles.toml", devin_paths)
        self.assertIn("hosts/devin/spawn.md", devin_paths)
        self.assertIn("hosts/devin/session_identity.py", devin_paths)
        synchronized = self.run_sync("status", modelconfig=None, host="devin")
        self.assertEqual(synchronized["status"], "ok", synchronized.get("detail"))
        self.assertFalse(synchronized["restart_required"])
        removed = sync.uninstall(self.home, self.codex_home, host="devin")
        self.assertEqual(removed["status"], "ok", removed.get("detail"))
        self.assertFalse(
            self.orchestra_root.joinpath("hosts/devin/roles.toml").exists()
        )
        self.assertFalse(
            self.home.joinpath(".config/devin/skills/orchestra").exists()
        )
        self.assertFalse(self.home.joinpath(".config/devin/config.json").exists())
        self.assertFalse(
            self.home.joinpath(".config/devin/agents/orchestra_analyst.md").exists()
        )

    def test_devin_config_merge_preserves_existing_hooks_and_keys(self) -> None:
        config_path = self.home / ".config/devin/config.json"
        config_path.parent.mkdir(parents=True)
        existing = {
            "model": "swe-2-max",
            "hooks": {
                "SessionStart": [
                    {
                        "matcher": "",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "orca session-start",
                                "timeout": 5,
                            }
                        ],
                    }
                ],
                "PreToolUse": [
                    {
                        "matcher": "exec",
                        "hooks": [{"type": "command", "command": "orca guard"}],
                    }
                ],
            },
        }
        config_path.write_text(json.dumps(existing, indent=2) + "\n")

        applied = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        merged = json.loads(config_path.read_text())
        self.assertEqual(merged["model"], "swe-2-max")
        self.assertEqual(
            merged["hooks"]["PreToolUse"], existing["hooks"]["PreToolUse"]
        )
        session_start = merged["hooks"]["SessionStart"]
        self.assertEqual(len(session_start), 2)
        self.assertEqual(
            session_start[0], existing["hooks"]["SessionStart"][0]
        )
        commands = [
            hook["command"]
            for matcher in session_start
            for hook in matcher["hooks"]
        ]
        self.assertIn(
            f'python3 "{self.orchestra_root}/hosts/devin/session_identity.py"',
            commands,
        )
        second = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(second["status"], "ok", second.get("detail"))
        self.assertEqual(second["changes"], [])

        removed = sync.uninstall(self.home, self.codex_home, host="devin")
        self.assertEqual(removed["status"], "ok", removed.get("detail"))
        remaining = json.loads(config_path.read_text())
        self.assertEqual(remaining["model"], "swe-2-max")
        self.assertEqual(
            remaining["hooks"]["SessionStart"],
            existing["hooks"]["SessionStart"],
        )
        self.assertEqual(
            remaining["hooks"]["PreToolUse"], existing["hooks"]["PreToolUse"]
        )

    def test_devin_invalid_config_json_blocks_without_mutation(self) -> None:
        config_path = self.home / ".config/devin/config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("{ not json")
        result = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("invalid Devin config.json", result["detail"])
        self.assertEqual(config_path.read_text(), "{ not json")

        config_path.write_text(json.dumps({"hooks": "not-an-object"}))
        result = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("hooks must be an object", result["detail"])
        self.assertEqual(
            config_path.read_text(), json.dumps({"hooks": "not-an-object"})
        )

        config_path.write_text(json.dumps({"hooks": {"SessionStart": "x"}}))
        result = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("SessionStart must be an array", result["detail"])

    def test_devin_unmanaged_orchestra_hook_and_drift_block(self) -> None:
        config_path = self.home / ".config/devin/config.json"
        config_path.parent.mkdir(parents=True)
        unmanaged = {
            "hooks": {
                "SessionStart": [
                    {
                        "matcher": "",
                        "hooks": [
                            {
                                "type": "command",
                                "command": 'python3 "$HOME/.orchestra/hosts/devin/session_identity.py"',
                            }
                        ],
                    }
                ]
            }
        }
        config_path.write_text(json.dumps(unmanaged))
        result = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("unmanaged Orchestra hook", result["detail"])
        self.assertIn("hosts/devin/session_identity.py", result["detail"])

        config_path.unlink()
        self.assertEqual(
            self.run_sync("apply", modelconfig=None, host="devin")["status"], "ok"
        )
        merged = json.loads(config_path.read_text())
        merged["hooks"]["SessionStart"][0]["hooks"][0]["timeout"] = 99
        config_path.write_text(json.dumps(merged))
        drifted = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(drifted["status"], "blocked")
        self.assertIn("owned Orchestra hook drift", drifted["detail"])

    def test_devin_unrelated_config_files_are_not_touched(self) -> None:
        unrelated = self.home / ".config/devin/team-settings.json"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text('{"org": "acme"}\n')
        other_agent = self.home / ".config/devin/agents/repo_context_explorer.md"
        other_agent.parent.mkdir(parents=True)
        other_agent.write_text("user agent\n")

        applied = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        self.assertEqual(unrelated.read_text(), '{"org": "acme"}\n')
        self.assertEqual(other_agent.read_text(), "user agent\n")

        removed = sync.uninstall(self.home, self.codex_home, host="devin")
        self.assertEqual(removed["status"], "ok", removed.get("detail"))
        self.assertEqual(unrelated.read_text(), '{"org": "acme"}\n')
        self.assertEqual(other_agent.read_text(), "user agent\n")

    def test_devin_uninstall_removes_managed_json_backup_so_reinstall_succeeds(
        self,
    ) -> None:
        config_path = self.home / ".config/devin/config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text(json.dumps({"model": "swe-2-max"}))
        backup = (
            self.orchestra_root
            / "orchestra/backups/home/.config/devin/config.json"
        )

        self.assertEqual(
            self.run_sync("apply", modelconfig=None, host="devin")["status"], "ok"
        )
        self.assertTrue(backup.is_file())
        removed = sync.uninstall(self.home, self.codex_home, host="devin")
        self.assertEqual(removed["status"], "ok", removed.get("detail"))
        self.assertFalse(backup.exists())

        reapplied = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(reapplied["status"], "ok", reapplied.get("detail"))
        merged = json.loads(config_path.read_text())
        self.assertEqual(len(merged["hooks"]["SessionStart"]), 1)

    def test_devin_duplicate_orchestra_hook_is_drift_and_uninstall_strips_all(self) -> None:
        config_path = self.home / ".config/devin/config.json"
        config_path.parent.mkdir(parents=True)
        user_matcher = {
            "matcher": "",
            "hooks": [{"type": "command", "command": "orca session-start"}],
        }
        config_path.write_text(
            json.dumps({"hooks": {"SessionStart": [user_matcher]}})
        )
        self.assertEqual(
            self.run_sync("apply", modelconfig=None, host="devin")["status"], "ok"
        )
        merged = json.loads(config_path.read_text())
        self.assertEqual(len(merged["hooks"]["SessionStart"]), 2)
        merged["hooks"]["SessionStart"].append(merged["hooks"]["SessionStart"][1])
        config_path.write_text(json.dumps(merged))

        status = self.run_sync("status", modelconfig=None, host="devin")
        self.assertEqual(status["status"], "blocked")
        self.assertIn("owned Orchestra hook drift", status["detail"])

        removed = sync.uninstall(self.home, self.codex_home, host="devin")
        self.assertEqual(removed["status"], "ok", removed.get("detail"))
        remaining = json.loads(config_path.read_text())
        self.assertEqual(remaining["hooks"]["SessionStart"], [user_matcher])

    def test_devin_divergent_duplicate_hook_blocks_uninstall_without_mutation(self) -> None:
        config_path = self.home / ".config/devin/config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("{}")
        self.assertEqual(
            self.run_sync("apply", modelconfig=None, host="devin")["status"], "ok"
        )
        merged = json.loads(config_path.read_text())
        divergent = json.loads(json.dumps(merged["hooks"]["SessionStart"][0]))
        divergent["hooks"][0]["timeout"] = 30
        merged["hooks"]["SessionStart"].append(divergent)
        config_path.write_text(json.dumps(merged))

        before = config_path.read_text()
        removed = sync.uninstall(self.home, self.codex_home, host="devin")
        self.assertEqual(removed["status"], "partial")
        self.assertIn("config.json", removed["detail"])
        self.assertEqual(config_path.read_text(), before)

    def test_devin_stray_source_agent_file_blocks_before_any_write(self) -> None:
        fixture = self.source_fixture()
        agents_dir = fixture / "hosts/devin/agents"
        agents_dir.mkdir(parents=True)
        for name in sync.AGENTS:
            shutil.copy2(
                ROOT / f"hosts/devin/agents/{name}.md",
                agents_dir / f"{name}.md",
            )
        (agents_dir / ".DS_Store").write_text("stray\n")
        for source, destination in (
            ("hosts/devin/config/roles.devin.toml", "hosts/devin/config/roles.devin.toml"),
            ("hosts/devin/references/spawn.md", "hosts/devin/references/spawn.md"),
            (
                "hosts/devin/plugin/scripts/session_identity.py",
                "hosts/devin/plugin/scripts/session_identity.py",
            ),
        ):
            target = fixture / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / source, target)

        result = sync.synchronize(
            fixture,
            self.home,
            self.codex_home,
            "apply",
            modelconfig=None,
            worktree_root=self.worktree_root,
            host="devin",
        )
        self.assertEqual(result["status"], "blocked")
        self.assertIn("unexpected agent source entry", result["detail"])
        self.assertFalse(self.home.exists())

    def test_devin_hook_command_uses_relocated_orchestra_home(self) -> None:
        relocated = Path(self.temporary.name) / "custom-orchestra"
        with mock.patch.dict(os.environ, {"ORCHESTRA_HOME": str(relocated)}):
            applied = self.run_sync("apply", modelconfig=None, host="devin")
            self.assertEqual(applied["status"], "ok", applied.get("detail"))
            config = json.loads(
                self.home.joinpath(".config/devin/config.json").read_text()
            )
            command = config["hooks"]["SessionStart"][0]["hooks"][0]["command"]
            self.assertEqual(
                command,
                f'python3 "{relocated}/hosts/devin/session_identity.py"',
            )
            self.assertTrue(
                relocated.joinpath("hosts/devin/session_identity.py").is_file()
            )
            self.assertFalse(
                self.orchestra_root.joinpath(
                    "hosts/devin/session_identity.py"
                ).exists()
            )
            removed = sync.uninstall(self.home, self.codex_home, host="devin")
            self.assertEqual(removed["status"], "ok", removed.get("detail"))

    def test_devin_new_config_json_is_created_owner_only(self) -> None:
        config_path = self.home / ".config/devin/config.json"
        applied = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        self.assertEqual(stat.S_IMODE(config_path.stat().st_mode), 0o600)

    def test_devin_existing_config_json_keeps_its_mode(self) -> None:
        config_path = self.home / ".config/devin/config.json"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("{}")
        config_path.chmod(0o640)
        applied = self.run_sync("apply", modelconfig=None, host="devin")
        self.assertEqual(applied["status"], "ok", applied.get("detail"))
        self.assertEqual(stat.S_IMODE(config_path.stat().st_mode), 0o640)

    def test_legacy_all_manifest_migrates_without_moving_backups(self) -> None:
        self.codex_home.mkdir(parents=True)
        self.codex_home.joinpath("AGENTS.md").write_text("Personal rules.\n")
        self.assertEqual(self.run_sync("apply", host="all")["status"], "ok")
        modern = self.manifest()
        legacy = {
            key: value
            for key, value in modern.items()
            if key not in {"schema_version", "installed_hosts"}
        }
        legacy["entries"] = [
            {
                key: value
                for key, value in entry.items()
                if key not in {"scope", "backup_root"}
            }
            for entry in modern["entries"]
        ]
        self.legacy_manifest_path().parent.mkdir(parents=True, exist_ok=True)
        self.legacy_manifest_path().write_text(
            json.dumps(legacy, indent=2, sort_keys=True) + "\n"
        )
        self.manifest_path().unlink()
        backup = self.codex_home / "orchestra/backups/codex_home/AGENTS.md"
        self.assertTrue(backup.is_file())

        status = self.run_sync("status", host="all")
        self.assertEqual(status["status"], "partial")
        self.assertIn("manifest migration pending", status["detail"])
        migrated = self.run_sync("apply", host="all")
        self.assertEqual(migrated["status"], "ok", migrated.get("detail"))
        self.assertFalse(self.legacy_manifest_path().exists())
        self.assertEqual(
            self.manifest()["installed_hosts"], ["codex", "cursor", "devin", "grok"]
        )
        owner = next(
            entry for entry in self.manifest()["entries"] if entry["path"] == "AGENTS.md"
        )
        self.assertEqual(owner["backup_root"], "codex_home")
        self.assertEqual(backup.read_text(), "Personal rules.\n")

    def test_conflicting_canonical_and_legacy_manifests_block(self) -> None:
        self.assertEqual(self.run_sync("apply", host="codex")["status"], "ok")
        legacy = self.manifest()
        legacy.pop("schema_version")
        legacy.pop("installed_hosts")
        legacy["entries"] = [
            {
                key: value
                for key, value in entry.items()
                if key not in {"scope", "backup_root"}
            }
            for entry in legacy["entries"]
        ]
        legacy["entries"][0]["digest"] = "0" * 64
        self.legacy_manifest_path().parent.mkdir(parents=True, exist_ok=True)
        self.legacy_manifest_path().write_text(
            json.dumps(legacy, indent=2, sort_keys=True) + "\n"
        )
        blocked = self.run_sync("status", host="codex")
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("conflicting install manifest destination", blocked["detail"])


if __name__ == "__main__":
    unittest.main()
