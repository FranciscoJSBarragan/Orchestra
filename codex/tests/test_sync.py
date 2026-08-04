"""Isolated tests for direct Orchestra synchronization."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
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

    def run_sync(
        self,
        action: str,
        *,
        dry_run: bool = False,
        modelconfig: str | None = "external",
    ) -> dict[str, object]:
        return sync.synchronize(
            ROOT,
            self.home,
            self.codex_home,
            action,
            dry_run=dry_run,
            modelconfig=modelconfig,
            worktree_root=self.worktree_root,
        )

    def manifest(self) -> dict[str, object]:
        return json.loads((self.codex_home / "orchestra/install-manifest.json").read_text())

    def source_fixture(self) -> Path:
        fixture = Path(self.temporary.name) / "source"
        for directory in ("skills", "agents"):
            shutil.copytree(ROOT / "codex" / directory, fixture / "codex" / directory)
        (fixture / "codex/config").mkdir(parents=True)
        for modelconfig in ("native", "external"):
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
        return fixture

    def convert_current_install_to_legacy_profile_manifest(self) -> None:
        """Model an owned pre-namespace install without retired source files."""
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
        payload = self.manifest()
        current_paths = {f"agents/{name}.toml" for name in sync.AGENTS}
        entries = [
            entry
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
        self.assertEqual(status["modelconfig"], "external")
        self.assertEqual(status["sandbox_root"], str(self.orchestra_root))
        self.assertTrue(status["restart_required"])
        self.assertFalse(self.home.exists())
        self.assertFalse(self.codex_home.exists())

        applied = self.run_sync("apply")
        self.assertEqual(applied["status"], "ok")
        self.assertEqual(applied["modelconfig"], "external")
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        self.assertTrue(
            self.home.joinpath(
                ".agents/skills/orchestra-project-start/SKILL.md"
            ).is_file()
        )
        for name in sync.AGENTS:
            self.assertTrue(self.codex_home.joinpath(f"agents/{name}.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("orchestra/roles.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("orchestra/scripts/pr.py").is_file())
        self.assertTrue(
            self.codex_home.joinpath("orchestra/scripts/coordination.py").is_file()
        )
        self.assertTrue(
            self.codex_home.joinpath("orchestra/scripts/session_model.py").is_file()
        )
        self.assertEqual(
            self.codex_home.joinpath("orchestra/worktree-root").read_text(),
            f"{self.worktree_root}\n",
        )
        config = self.codex_home.joinpath("config.toml").read_text()
        self.assertIn('approval_policy = "on-request"', config)
        self.assertIn('approvals_reviewer = "auto_review"', config)
        self.assertIn('default_permissions = ":workspace"', config)
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
        self.assertEqual(self.manifest()["modelconfig"], "external")
        self.assertEqual(
            self.codex_home.joinpath("orchestra/roles.toml").read_bytes(),
            ROOT.joinpath("codex/config/roles.external.toml").read_bytes(),
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
        self.assertEqual(
            self.codex_home.joinpath(
                "agents/orchestra_reviewer.toml"
            ).stat().st_mode
            & 0o777,
            0o644,
        )
        self.assertEqual(
            self.codex_home.joinpath("orchestra/install-manifest.json").stat().st_mode
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
        self.assertFalse(self.codex_home.joinpath("orchestra/install-manifest.json").exists())
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
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
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
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
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
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
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
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
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
            self.codex_home.joinpath("orchestra/install-manifest.json").exists()
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
            self.codex_home.joinpath("orchestra/install-manifest.json").is_file()
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
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
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
            modelconfig="external",
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

    def test_fresh_install_requires_explicit_modelconfig(self) -> None:
        status = self.run_sync("status", modelconfig=None)
        self.assertEqual(status["status"], "partial")
        self.assertIn("--modelconfig dual", status["detail"])
        self.assertIn("--modelconfig native", status["detail"])

        for dry_run in (False, True):
            result = self.run_sync(
                "apply", dry_run=dry_run, modelconfig=None
            )
            self.assertEqual(result["status"], "blocked")
            self.assertIn("--modelconfig external", result["detail"])
        self.assertFalse(self.home.exists())
        self.assertFalse(self.codex_home.exists())

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

    def test_native_install_persists_and_switches_atomically_to_external(self) -> None:
        installed = self.run_sync("apply", modelconfig="native")
        self.assertEqual(installed["status"], "ok")
        self.assertEqual(installed["modelconfig"], "native")
        roles = self.codex_home / "orchestra/roles.toml"
        native = ROOT / "codex/config/roles.native.toml"
        external = ROOT / "codex/config/roles.external.toml"
        self.assertEqual(roles.read_bytes(), native.read_bytes())
        self.assertEqual(self.manifest()["modelconfig"], "native")

        reused = self.run_sync("status", modelconfig=None)
        self.assertEqual(reused["status"], "ok")
        self.assertEqual(reused["modelconfig"], "native")

        preview = self.run_sync(
            "apply", dry_run=True, modelconfig="external"
        )
        self.assertEqual(preview["status"], "partial")
        self.assertEqual(preview["modelconfig"], "external")
        self.assertEqual(
            [
                change
                for change in preview["changes"]
                if change["path"] == "orchestra/roles.toml"
            ],
            [
                {
                    "operation": "update",
                    "path": "orchestra/roles.toml",
                    "root": "codex_home",
                }
            ],
        )
        self.assertEqual(roles.read_bytes(), native.read_bytes())
        self.assertEqual(self.manifest()["modelconfig"], "native")

        switched = self.run_sync("apply", modelconfig="external")
        self.assertEqual(switched["status"], "ok")
        self.assertEqual(switched["modelconfig"], "external")
        self.assertEqual(roles.read_bytes(), external.read_bytes())
        self.assertEqual(self.manifest()["modelconfig"], "external")
        self.assertEqual(
            self.codex_home.joinpath(
                "orchestra/backups/codex_home/orchestra/roles.toml"
            ).read_bytes(),
            native.read_bytes(),
        )
        self.assertEqual(
            self.run_sync("status", modelconfig=None)["status"], "ok"
        )

    def test_dual_install_persists_combined_matrix(self) -> None:
        installed = self.run_sync("apply", modelconfig="dual")
        self.assertEqual(installed["status"], "ok")
        self.assertEqual(installed["modelconfig"], "dual")
        self.assertEqual(self.manifest()["modelconfig"], "dual")
        expected_dual = sync.compose_dual_matrix(
            ROOT.joinpath("codex/config/roles.native.toml").read_text(
                encoding="utf-8"
            ),
            ROOT.joinpath("codex/config/roles.external.toml").read_text(
                encoding="utf-8"
            ),
        ).encode("utf-8")
        self.assertEqual(
            self.codex_home.joinpath("orchestra/roles.toml").read_bytes(),
            expected_dual,
        )
        self.assertEqual(
            self.run_sync("status", modelconfig=None)["modelconfig"],
            "dual",
        )

    def test_legacy_manifest_requires_one_explicit_selection(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest()
        manifest.pop("modelconfig")
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        status = self.run_sync("status", modelconfig=None)
        self.assertEqual(status["status"], "blocked")
        self.assertIn("model configuration is not selected", status["detail"])
        self.assertEqual(
            self.run_sync("apply", modelconfig=None)["status"], "blocked"
        )

        migrated = self.run_sync("apply", modelconfig="external")
        self.assertEqual(migrated["status"], "ok")
        self.assertEqual(migrated["changes"], [])
        self.assertEqual(self.manifest()["modelconfig"], "external")

    def test_legacy_manifest_remains_uninstallable_without_selection(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest()
        manifest.pop("modelconfig")
        (self.codex_home / "orchestra/install-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        removed = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(removed["status"], "ok")
        self.assertFalse(
            self.codex_home.joinpath("orchestra/install-manifest.json").exists()
        )

    def test_invalid_modelconfig_and_manifest_selection_block(self) -> None:
        invalid = self.run_sync("status", modelconfig="unsupported")
        self.assertEqual(invalid["status"], "blocked")
        self.assertIn("unknown model configuration", invalid["detail"])

        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.manifest()
        manifest["modelconfig"] = "unsupported"
        (self.codex_home / "orchestra/install-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        status = self.run_sync("status")
        self.assertEqual(status["status"], "blocked")
        self.assertIn("invalid install manifest modelconfig", status["detail"])

    def test_failed_switch_restores_roles_and_persisted_selection(self) -> None:
        self.assertEqual(
            self.run_sync("apply", modelconfig="native")["status"], "ok"
        )
        roles = self.codex_home / "orchestra/roles.toml"
        roles_before = roles.read_bytes()
        manifest_before = (
            self.codex_home / "orchestra/install-manifest.json"
        ).read_bytes()

        with mock.patch.object(
            sync, "_write_manifest", side_effect=OSError("injected switch failure")
        ):
            switched = self.run_sync("apply", modelconfig="external")
        self.assertEqual(switched["status"], "blocked")
        self.assertEqual(roles.read_bytes(), roles_before)
        self.assertEqual(
            (self.codex_home / "orchestra/install-manifest.json").read_bytes(),
            manifest_before,
        )
        self.assertEqual(
            self.run_sync("status", modelconfig=None)["modelconfig"], "native"
        )

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
        manifest = self.codex_home / "orchestra/install-manifest.json"
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
        (self.codex_home / "agents").symlink_to(external, target_is_directory=True)
        self.assertEqual(self.run_sync("apply")["status"], "blocked")
        self.assertEqual(list(external.iterdir()), [])

    def test_subprocess_contract_uses_only_explicit_temporary_destinations(self) -> None:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env["CODEX_HOME"] = str(self.codex_home)
        env.pop("ORCHESTRA_WORKTREE_ROOT", None)
        commands = (
            ("status",),
            ("status", "--modelconfig", "external"),
            ("apply", "--dry-run", "--modelconfig", "external"),
            ("apply", "--modelconfig", "external"),
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
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env.pop("CODEX_HOME", None)
        env.pop("ORCHESTRA_WORKTREE_ROOT", None)
        applied = subprocess.run(
            [
                sys.executable,
                str(SYNC_PATH),
                "apply",
                "--modelconfig",
                "external",
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
        self.assertIn(
            "${CODEX_HOME:-$HOME/.codex}",
            self.home.joinpath(".agents/skills/orchestra/SKILL.md").read_text(),
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
        env = os.environ.copy()
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
                "external",
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
        self.assertFalse(self.codex_home.joinpath("orchestra/install-manifest.json").exists())

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
                modelconfig="external",
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
            modelconfig="external",
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
                modelconfig="external",
            )["status"],
            "ok",
        )
        backup = self.codex_home / "orchestra/backups/home/.agents/skills/orchestra/SKILL.md"
        self.assertEqual(backup.read_bytes(), previous)
        self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
        self.assertFalse(self.home.joinpath(".agents/skills/orchestra/notes.txt").exists())
        self.assertFalse(
            self.codex_home.joinpath(
                "orchestra/backups/home/.agents/skills/orchestra/notes.txt"
            ).exists()
        )
        self.assertEqual(
            sync.synchronize(
                source,
                self.home,
                self.codex_home,
                "status",
                modelconfig="external",
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
            modelconfig="external",
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
            modelconfig="external",
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
                modelconfig="external",
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
                modelconfig="external",
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
        self.assertFalse(self.codex_home.joinpath("orchestra/install-manifest.json").exists())
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
        self.assertFalse(self.codex_home.joinpath("orchestra/install-manifest.json").exists())

    def test_persistent_uninstall_manifest_failure_restores_destination(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest = self.codex_home / "orchestra/install-manifest.json"
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
                modelconfig="external",
            )["status"],
            "ok",
        )
        destination = self.home / ".agents/skills/orchestra/notes.txt"
        manifest = self.codex_home / "orchestra/install-manifest.json"
        destination_before = destination.read_bytes()
        manifest_before = manifest.read_bytes()
        backup = self.codex_home / "orchestra/backups/home/.agents/skills/orchestra/notes.txt"
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
                modelconfig="external",
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
                modelconfig="external",
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
                modelconfig="external",
            )["status"],
            "ok",
        )
        destination = self.home / ".agents/skills/orchestra/notes.txt"
        backup = self.codex_home / "orchestra/backups/home/.agents/skills/orchestra/notes.txt"
        manifest = self.codex_home / "orchestra/install-manifest.json"
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
                modelconfig="external",
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
        manifest = self.codex_home / "orchestra/install-manifest.json"
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


if __name__ == "__main__":
    unittest.main()
