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
        self.assertNotEqual(self.home.resolve(), Path.home().resolve())
        self.assertNotEqual(self.codex_home.resolve(), (Path.home() / ".codex").resolve())

    def run_sync(self, action: str, *, dry_run: bool = False) -> dict[str, object]:
        return sync.synchronize(ROOT, self.home, self.codex_home, action, dry_run=dry_run)

    def manifest(self) -> dict[str, object]:
        return json.loads((self.codex_home / "orchestra/install-manifest.json").read_text())

    def source_fixture(self) -> Path:
        fixture = Path(self.temporary.name) / "source"
        for directory in ("skills", "agents"):
            shutil.copytree(ROOT / "codex" / directory, fixture / "codex" / directory)
        (fixture / "codex/config").mkdir(parents=True)
        shutil.copy2(ROOT / "codex/config/roles.toml", fixture / "codex/config/roles.toml")
        (fixture / "codex/scripts").mkdir(parents=True)
        for helper in sync.HELPERS:
            shutil.copy2(ROOT / "codex/scripts" / helper, fixture / "codex/scripts" / helper)
        (fixture / "codex/runtime").mkdir(parents=True)
        shutil.copy2(
            ROOT / "codex/runtime/AGENTS.orchestra.md",
            fixture / "codex/runtime/AGENTS.orchestra.md",
        )
        return fixture

    def convert_current_install_to_twelve_profile_manifest(self) -> None:
        """Model a pre-composition install without depending on retired sources."""
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest_path = self.codex_home / "orchestra/install-manifest.json"
        payload = self.manifest()
        entries = [
            entry
            for entry in payload["entries"]
            if entry["path"] not in {"agents/analyst.toml", "agents/verifier.toml"}
        ]
        for name in ("analyst", "verifier"):
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
            json.dumps({"entries": sorted(entries, key=lambda entry: (entry["root"], entry["path"]))}, indent=2, sort_keys=True)
            + "\n"
        )

    def test_clean_install_status_and_uninstall(self) -> None:
        status = self.run_sync("status")
        self.assertEqual(status["status"], "partial")
        self.assertFalse(self.home.exists())
        self.assertFalse(self.codex_home.exists())

        applied = self.run_sync("apply")
        self.assertEqual(applied["status"], "ok")
        self.assertTrue(self.home.joinpath(".agents/skills/orchestra/SKILL.md").is_file())
        self.assertTrue(self.codex_home.joinpath("agents/reviewer.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("agents/analyst.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("agents/verifier.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("orchestra/roles.toml").is_file())
        self.assertTrue(self.codex_home.joinpath("orchestra/scripts/pr.py").is_file())
        installed_guidance = self.codex_home.joinpath("AGENTS.md").read_text()
        self.assertIn("Native Codex Plan Mode and Orchestra are mutually exclusive", installed_guidance)
        self.assertIn("direct change, fix, implementation", installed_guidance)
        self.assertIn("asks to create, prepare, or write the implementation plan", installed_guidance)
        self.assertEqual(self.run_sync("status")["status"], "ok")
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
        second = self.run_sync("apply")
        self.assertEqual(second["status"], "ok")
        self.assertEqual(second["changes"], [])
        self.assertEqual(
            self.home.joinpath(".agents/skills/orchestra/SKILL.md").stat().st_mode & 0o777,
            0o644,
        )
        self.assertEqual(
            self.codex_home.joinpath("agents/reviewer.toml").stat().st_mode & 0o777,
            0o644,
        )
        self.assertEqual(
            self.codex_home.joinpath("orchestra/install-manifest.json").stat().st_mode
            & 0o777,
            0o600,
        )

        removed = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(removed["status"], "ok")
        self.assertFalse(self.home.joinpath(".agents/skills/orchestra").exists())
        self.assertFalse(self.codex_home.joinpath("install-manifest.json").exists())
        self.assertFalse(self.codex_home.joinpath("orchestra/install-manifest.json").exists())
        self.assertFalse(self.codex_home.joinpath("agents/analyst.toml").exists())
        self.assertFalse(self.codex_home.joinpath("agents/verifier.toml").exists())

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
        drifted = self.codex_home / "agents/reviewer.toml"
        drifted.write_text("user edit\n")
        self.assertEqual(self.run_sync("status")["status"], "blocked")
        self.assertEqual(self.run_sync("apply")["status"], "blocked")

        result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "partial")
        self.assertEqual(drifted.read_text(), "user edit\n")
        remaining = self.manifest()["entries"]
        self.assertEqual([entry["path"] for entry in remaining], ["agents/reviewer.toml"])

    def test_uninstall_retains_missing_entry_and_removes_all_safe_entries(self) -> None:
        self.assertEqual(self.run_sync("apply")["status"], "ok")
        manifest_before = self.manifest()["entries"]
        retained = next(
            entry
            for entry in manifest_before
            if entry["path"] == "agents/analyst.toml"
        )
        missing = self.codex_home / retained["path"]
        missing.unlink()

        result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "partial")
        self.assertIn("agents/analyst.toml", result["detail"])
        self.assertEqual(self.manifest()["entries"], [retained])
        self.assertFalse(self.codex_home.joinpath("agents/reviewer.toml").exists())
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
        self.assertFalse(self.codex_home.joinpath("agents/reviewer.toml").exists())

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
        commands = (
            ("status",),
            ("apply", "--dry-run"),
            ("apply",),
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
        self.assertEqual(statuses, ["partial", "partial", "ok", "ok"])

    def test_subprocess_defaults_codex_home_and_installed_helper_resolves(self) -> None:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env.pop("CODEX_HOME", None)
        applied = subprocess.run(
            [sys.executable, str(SYNC_PATH), "apply"],
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
            sync.synchronize(source, self.home, self.codex_home, "apply")["status"],
            "ok",
        )
        installed_skill = self.home / ".agents/skills/orchestra/SKILL.md"
        previous = installed_skill.read_bytes()
        skill_source = source / "codex/skills/orchestra/SKILL.md"
        skill_source.write_bytes(previous + b"\nUpgrade fixture.\n")
        extra_source.unlink()

        preview = sync.synchronize(source, self.home, self.codex_home, "apply", dry_run=True)
        self.assertEqual(preview["status"], "partial")
        self.assertEqual(
            {(change["operation"], change["path"]) for change in preview["changes"]},
            {("update", ".agents/skills/orchestra/SKILL.md"), ("delete", ".agents/skills/orchestra/notes.txt")},
        )
        self.assertEqual(
            sync.synchronize(source, self.home, self.codex_home, "apply")["status"],
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
        self.assertEqual(sync.synchronize(source, self.home, self.codex_home, "status")["status"], "ok")

    def test_twelve_to_four_upgrade_removes_only_stale_owned_profiles(self) -> None:
        self.convert_current_install_to_twelve_profile_manifest()
        installed_agents = {
            entry["path"]
            for entry in self.manifest()["entries"]
            if entry["path"].startswith("agents/")
        }
        self.assertEqual(len(installed_agents), 12)
        self.assertEqual(
            installed_agents,
            {
                "agents/implementation_worker.toml",
                "agents/reviewer.toml",
                *(f"agents/{name}.toml" for name in sync.LEGACY_AGENTS),
            },
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
                ("create", "agents/analyst.toml"),
                ("create", "agents/verifier.toml"),
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
        self.convert_current_install_to_twelve_profile_manifest()
        drifted = self.codex_home / "agents/browser_acceptance_tester.toml"
        drifted.write_text("user edit\n")
        result = self.run_sync("apply")
        self.assertEqual(result["status"], "blocked")
        self.assertIn("owned destination drift", result["detail"])
        self.assertFalse(self.codex_home.joinpath("agents/analyst.toml").exists())
        self.assertFalse(self.codex_home.joinpath("agents/verifier.toml").exists())
        for name in sync.LEGACY_AGENTS:
            self.assertTrue(self.codex_home.joinpath(f"agents/{name}.toml").exists())

    def test_source_symlinks_and_malformed_marker_sources_block(self) -> None:
        source = self.source_fixture()
        target = Path(self.temporary.name) / "outside-source"
        target.write_text("outside")
        (source / "codex/skills/orchestra/link.txt").symlink_to(target)
        result = sync.synchronize(source, self.home, self.codex_home, "apply")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(self.home.exists())
        (source / "codex/skills/orchestra/link.txt").unlink()

        runtime = source / "codex/runtime/AGENTS.orchestra.md"
        runtime.write_bytes(sync.START + b"\n" + sync.START + b"\n" + sync.END + b"\n")
        result = sync.synchronize(source, self.home, self.codex_home, "apply")
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
            sync.synchronize(source, self.home, self.codex_home, "apply")["status"],
            "ok",
        )
        agents.write_bytes(agents.read_bytes() + b"Later outside edit.\n")
        runtime = source / "codex/runtime/AGENTS.orchestra.md"
        runtime.write_bytes(runtime.read_bytes().replace(sync.END, b"New routing line.\n" + sync.END))

        self.assertEqual(
            sync.synchronize(source, self.home, self.codex_home, "apply")["status"],
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
        backup = self.codex_home / "orchestra/backups/codex_home/agents/reviewer.toml"
        backup.parent.mkdir(parents=True)
        backup.write_text("unmanaged backup")
        result = sync.uninstall(self.home, self.codex_home)
        self.assertEqual(result["status"], "partial")
        self.assertTrue(self.codex_home.joinpath("agents/reviewer.toml").exists())
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
        self.assertFalse(self.codex_home.joinpath("agents/analyst.toml").exists())
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
            sync.synchronize(source, self.home, self.codex_home, "apply")["status"],
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
            result = sync.synchronize(source, self.home, self.codex_home, "apply")
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(destination.read_bytes(), destination_before)
        self.assertEqual(manifest.read_bytes(), manifest_before)
        self.assertFalse(backup.exists())

    def test_apply_stale_manifest_failure_restores_prior_backup_and_destination(self) -> None:
        source = self.source_fixture()
        extra_source = source / "codex/skills/orchestra/notes.txt"
        extra_source.write_text("version one\n")
        self.assertEqual(
            sync.synchronize(source, self.home, self.codex_home, "apply")["status"],
            "ok",
        )
        extra_source.write_text("version two\n")
        self.assertEqual(
            sync.synchronize(source, self.home, self.codex_home, "apply")["status"],
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
            result = sync.synchronize(source, self.home, self.codex_home, "apply")
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
