"""Tests for the durable prepared-task Kanban."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTROL_ROOT = ROOT / "codex/control"
sys.path.insert(0, str(CONTROL_ROOT))

from orchestra_control.db import SCHEMA_VERSION  # noqa: E402
from orchestra_control.service import (  # noqa: E402
    ControlError,
    ControlService,
    host_thread_from_env,
    sequence_to_short_id,
    validate_thread_id,
)
from orchestra_control.mcp import TOOLS, cli_arguments  # noqa: E402


HELPER = ROOT / "codex/scripts/task_control.py"
MCP_HELPER = ROOT / "codex/scripts/task_mcp.py"
THREAD_ONE = "11111111-1111-4111-8111-111111111111"
THREAD_TWO = "22222222-2222-4222-8222-222222222222"


class TaskControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.state_root = self.root / "state"
        self.repository = self.root / "repository"
        self.repository.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Orchestra Test")
        self.git("config", "user.email", "orchestra@example.invalid")
        (self.repository / "seed.txt").write_text("seed\n", encoding="utf-8")
        self.git("add", "seed.txt")
        self.git("commit", "-q", "-m", "seed")
        self.revision = self.git("rev-parse", "HEAD").stdout.strip()
        self.common_dir = self.git(
            "rev-parse", "--path-format=absolute", "--git-common-dir"
        ).stdout.strip()
        self.service = ControlService(self.state_root)

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args], cwd=self.repository, capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def create_task(self, key: str = "capture-1") -> dict[str, object]:
        return self.service.create_task(
            title="Durable task",
            brief="Inspect the repository and prepare a candidate specification.",
            source_harness="test",
            repository=str(self.repository),
            idempotency_key=key,
        )

    def prepare(self, task: str) -> dict[str, object]:
        return self.service.prepare_task(
            task_ref=task,
            repository=str(self.repository),
            prepared_revision=self.revision,
            repository_common_dir=self.common_dir,
            repository_context="# Repository context\n\nObserved source.\n",
            specification="# Specification\n\nConfirmed result.\n",
            confirmed=True,
        )

    def cli(
        self,
        *args: str,
        thread: str | None = None,
        cursor_thread: str | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        environment = os.environ.copy()
        for key in (
            "CODEX_THREAD_ID",
            "CURSOR_CONVERSATION_ID",
            "CURSOR_THREAD_ID",
            "ORCHESTRA_HOST_THREAD_ID",
        ):
            environment.pop(key, None)
        if thread is not None:
            environment["CODEX_THREAD_ID"] = thread
        if cursor_thread is not None:
            environment["ORCHESTRA_HOST_THREAD_ID"] = cursor_thread
        result = subprocess.run(
            [sys.executable, str(HELPER), "--state-root", str(self.state_root), *args],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(result.stdout + result.stderr)
        return result, payload

    def test_short_id_sequence_matches_approved_format(self) -> None:
        expected = {
            1: "A1",
            99: "A99",
            100: "B1",
            2574: "Z99",
            2575: "AA1",
            2674: "AB1",
        }
        for sequence, short_id in expected.items():
            self.assertEqual(sequence_to_short_id(sequence), short_id)

    def test_capture_is_idempotent_allocates_human_id_and_is_private(self) -> None:
        first = self.create_task()
        second = self.create_task()
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(first["short_id"], "A1")
        self.assertEqual(first["preparation_status"], "draft")
        self.assertEqual(self.create_task("capture-2")["short_id"], "A2")
        self.assertEqual(stat.S_IMODE(self.state_root.stat().st_mode), 0o700)
        self.assertEqual(
            stat.S_IMODE((self.state_root / "control.sqlite3").stat().st_mode), 0o600
        )

    def test_lookup_is_case_insensitive_and_uuid_remains_identity(self) -> None:
        task = self.create_task()
        self.assertEqual(self.service.get_task("a1")["id"], task["id"])
        self.assertEqual(self.service.get_task(str(task["id"]))["short_id"], "A1")

    def test_concurrent_capture_allocates_unique_monotonic_ids(self) -> None:
        commands = [
            [
                sys.executable,
                str(HELPER),
                "--state-root",
                str(self.state_root),
                "task",
                "create",
                "--title",
                f"Task {index}",
                "--brief",
                "Prepared task",
                "--source-harness",
                "test",
                "--idempotency-key",
                f"concurrent-{index}",
            ]
            for index in range(12)
        ]
        processes = [
            subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for command in commands
        ]
        rows = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, stdout + stderr)
            rows.append(json.loads(stdout)["task"])
        self.assertEqual(len({row["short_id"] for row in rows}), 12)
        self.assertEqual(
            {row["short_id"] for row in rows},
            {f"A{index}" for index in range(1, 13)},
        )

    def test_prepare_requires_confirmation_and_writes_private_documents(self) -> None:
        task = self.create_task()
        with self.assertRaises(ControlError):
            self.service.prepare_task(
                task_ref="A1",
                repository=str(self.repository),
                prepared_revision=self.revision,
                repository_context="context",
                specification="specification",
                confirmed=False,
            )
        ready = self.prepare("A1")
        self.assertEqual(ready["preparation_status"], "ready")
        for name in ("repository_context", "specification", "marker"):
            path = Path(ready["documents"][name])
            self.assertTrue(path.is_file())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        marker = json.loads(Path(ready["documents"]["marker"]).read_text())
        self.assertEqual(marker["id"], task["id"])
        self.assertEqual(marker["short_id"], "A1")

    def test_adoption_requires_native_thread_and_reports_context_delta(self) -> None:
        self.create_task()
        self.prepare("A1")
        with self.assertRaises(ControlError) as missing:
            self.service.adopt_task(
                task_ref="A1",
                thread_id=None,
                repository=str(self.repository),
                current_revision=self.revision,
            )
        self.assertEqual(missing.exception.status, "blocked")
        adopted = self.service.adopt_task(
            task_ref="a1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        self.assertEqual(adopted["preparation_status"], "adopted")
        self.assertEqual(adopted["context_action"], "use_prepared")
        self.git("commit", "--allow-empty", "-q", "-m", "new revision")
        new_revision = self.git("rev-parse", "HEAD").stdout.strip()
        resumed = self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=new_revision,
        )
        self.assertEqual(resumed["context_action"], "repository_context_delta")

    def test_cursor_adoption_blocks_without_host_identity_and_accepts_host_id(
        self,
    ) -> None:
        self.create_task()
        self.prepare("A1")
        with self.assertRaises(ControlError) as missing:
            self.service.adopt_task(
                task_ref="A1",
                thread_id=None,
                repository=str(self.repository),
                current_revision=self.revision,
                source_harness="cursor",
            )
        self.assertEqual(missing.exception.status, "blocked")
        self.assertIn("Cursor host conversation identity", missing.exception.reason)
        adopted = self.service.adopt_task(
            task_ref="A1",
            thread_id="cursor-conversation-abc",
            repository=str(self.repository),
            current_revision=self.revision,
            source_harness="cursor",
        )
        self.assertEqual(adopted["preparation_status"], "adopted")
        self.assertEqual(adopted["adopted_thread_id"], "cursor-conversation-abc")

    def test_host_thread_from_env_reads_codex_or_cursor_identity(self) -> None:
        self.assertEqual(host_thread_from_env({}), (None, None))
        self.assertEqual(
            host_thread_from_env({"CODEX_THREAD_ID": THREAD_ONE}),
            ("codex", THREAD_ONE),
        )
        self.assertEqual(
            host_thread_from_env({"ORCHESTRA_HOST_THREAD_ID": "cursor-thread-1"}),
            ("cursor", "cursor-thread-1"),
        )
        self.assertEqual(
            host_thread_from_env({"CURSOR_CONVERSATION_ID": "undocumented"}),
            (None, None),
        )
        self.assertEqual(
            host_thread_from_env({"CURSOR_THREAD_ID": "undocumented"}),
            (None, None),
        )
        with self.assertRaises(ControlError) as missing:
            validate_thread_id(None, None)
        self.assertEqual(missing.exception.status, "blocked")
        self.assertIn("host conversation identity is missing", missing.exception.reason)

    def test_adoption_rejects_tampered_prepared_documents(self) -> None:
        self.create_task()
        ready = self.prepare("A1")
        Path(ready["documents"]["specification"]).write_text("tampered\n", encoding="utf-8")
        with self.assertRaises(ControlError) as error:
            self.service.adopt_task(
                task_ref="A1",
                thread_id=THREAD_ONE,
                repository=str(self.repository),
                current_revision=self.revision,
            )
        self.assertEqual(error.exception.status, "blocked")
        self.assertIn("digest", error.exception.reason)

    def test_adoption_rejects_repository_alias_and_symlinked_document(self) -> None:
        self.create_task()
        ready = self.prepare("A1")
        alias = self.root / "repository-alias"
        alias.symlink_to(self.repository, target_is_directory=True)
        adopted = self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(alias),
            current_revision=self.revision,
        )
        self.assertEqual(adopted["adopted_thread_id"], THREAD_ONE)
        self.assertEqual(adopted["adopted_harness"], "codex")
        self.service.transfer_task(
            task_ref="A1", thread_id=THREAD_ONE, stable_checkpoint=True
        )
        specification = Path(ready["documents"]["specification"])
        original = specification.read_text(encoding="utf-8")
        specification.unlink()
        target = self.root / "specification-target.md"
        target.write_text(original, encoding="utf-8")
        specification.symlink_to(target)
        with self.assertRaises(ControlError) as error:
            self.service.adopt_task(
                task_ref="A1",
                thread_id=THREAD_TWO,
                repository=str(self.repository),
                current_revision=self.revision,
            )
        self.assertEqual(error.exception.status, "blocked")
        self.assertIn("unsafe", error.exception.reason)

    def test_only_one_chat_adopts_and_transfer_requires_stable_checkpoint(self) -> None:
        self.create_task()
        self.prepare("A1")
        self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        with self.assertRaises(ControlError) as busy:
            self.service.adopt_task(
                task_ref="A1",
                thread_id=THREAD_TWO,
                repository=str(self.repository),
                current_revision=self.revision,
            )
        self.assertEqual(busy.exception.status, "busy")
        with self.assertRaises(ControlError):
            self.service.transfer_task(
                task_ref="A1", thread_id=THREAD_ONE, stable_checkpoint=False
            )
        transferred = self.service.transfer_task(
            task_ref="A1", thread_id=THREAD_ONE, stable_checkpoint=True
        )
        self.assertEqual(transferred["preparation_status"], "ready")
        self.assertEqual(transferred["transfer_generation"], 1)
        with self.assertRaises(ControlError):
            self.service.adopt_task(
                task_ref="A1",
                thread_id=THREAD_ONE,
                repository=str(self.repository),
                current_revision=self.revision,
            )
        resumed = self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_TWO,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        self.assertTrue(resumed["resume_existing_checkout"])
        self.assertEqual(resumed["id"], transferred["id"])
        self.assertEqual(resumed["short_id"], "A1")
        self.assertEqual(resumed["title"], transferred["title"])

    def test_reclaim_takes_over_another_host_chat(self) -> None:
        self.create_task()
        self.prepare("A1")
        with self.assertRaises(ControlError) as not_adopted:
            self.service.reclaim_task(
                task_ref="A1",
                thread_id=THREAD_TWO,
                repository=str(self.repository),
                current_revision=self.revision,
                authorized=True,
            )
        self.assertEqual(not_adopted.exception.status, "invalid")
        self.assertIn("owned by another chat", not_adopted.exception.reason)
        adopted = self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        self.assertEqual(adopted["adopted_thread_id"], THREAD_ONE)
        with self.assertRaises(ControlError) as busy:
            self.service.adopt_task(
                task_ref="A1",
                thread_id="cursor-conversation-abc",
                repository=str(self.repository),
                current_revision=self.revision,
                source_harness="cursor",
            )
        self.assertEqual(busy.exception.status, "busy")
        with self.assertRaises(ControlError) as unauthorized:
            self.service.reclaim_task(
                task_ref="A1",
                thread_id="cursor-conversation-abc",
                repository=str(self.repository),
                current_revision=self.revision,
                authorized=False,
                source_harness="cursor",
            )
        self.assertEqual(unauthorized.exception.status, "invalid")
        self.assertIn("authorization", unauthorized.exception.reason)
        with self.assertRaises(ControlError) as missing:
            self.service.reclaim_task(
                task_ref="A1",
                thread_id=None,
                repository=str(self.repository),
                current_revision=self.revision,
                authorized=True,
                source_harness="cursor",
            )
        self.assertEqual(missing.exception.status, "blocked")
        self.assertIn("Cursor host conversation identity", missing.exception.reason)
        with self.assertRaises(ControlError) as same_thread:
            self.service.reclaim_task(
                task_ref="A1",
                thread_id=THREAD_ONE,
                repository=str(self.repository),
                current_revision=self.revision,
                authorized=True,
            )
        self.assertEqual(same_thread.exception.status, "invalid")
        self.assertIn("continue instead of reclaim", same_thread.exception.reason)
        with self.assertRaises(ControlError) as foreign_transfer:
            self.service.transfer_task(
                task_ref="A1",
                thread_id="cursor-conversation-abc",
                stable_checkpoint=True,
                source_harness="cursor",
            )
        self.assertEqual(foreign_transfer.exception.status, "invalid")
        reclaimed = self.service.reclaim_task(
            task_ref="A1",
            thread_id="cursor-conversation-abc",
            repository=str(self.repository),
            current_revision=self.revision,
            authorized=True,
            source_harness="cursor",
        )
        self.assertEqual(reclaimed["preparation_status"], "adopted")
        self.assertEqual(reclaimed["adopted_thread_id"], "cursor-conversation-abc")
        self.assertEqual(reclaimed["adopted_harness"], "cursor")
        self.assertEqual(reclaimed["previous_thread_id"], THREAD_ONE)
        self.assertEqual(reclaimed["previous_harness"], "codex")
        self.assertEqual(reclaimed["transfer_generation"], 1)
        self.assertTrue(reclaimed["resume_existing_checkout"])
        with self.assertRaises(ControlError) as still_busy:
            self.service.adopt_task(
                task_ref="A1",
                thread_id=THREAD_TWO,
                repository=str(self.repository),
                current_revision=self.revision,
            )
        self.assertEqual(still_busy.exception.status, "busy")
        with self.assertRaises(ControlError) as same_new_owner:
            self.service.reclaim_task(
                task_ref="A1",
                thread_id="cursor-conversation-abc",
                repository=str(self.repository),
                current_revision=self.revision,
                authorized=True,
                source_harness="cursor",
            )
        self.assertEqual(same_new_owner.exception.status, "invalid")
        result, missing_cli = self.cli(
            "task",
            "reclaim",
            "--task",
            "A1",
            "--repository",
            str(self.repository),
            "--authorized",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(missing_cli["status"], "blocked")
        result, cli_reclaim = self.cli(
            "task",
            "reclaim",
            "--task",
            "A1",
            "--repository",
            str(self.repository),
            "--authorized",
            cursor_thread="cursor-conversation-abc",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(cli_reclaim["status"], "invalid")
        result, without_flag = self.cli(
            "task",
            "reclaim",
            "--task",
            "A1",
            "--repository",
            str(self.repository),
            cursor_thread="cursor-other",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(without_flag["status"], "invalid")
        result, cli_ok = self.cli(
            "task",
            "reclaim",
            "--task",
            "A1",
            "--repository",
            str(self.repository),
            "--authorized",
            cursor_thread="cursor-other",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(cli_ok["task"]["adopted_thread_id"], "cursor-other")
        self.assertEqual(cli_ok["task"]["previous_thread_id"], "cursor-conversation-abc")
        self.assertTrue(cli_ok["task"]["resume_existing_checkout"])

    def test_finish_and_archive_are_owner_safe(self) -> None:
        self.create_task()
        self.prepare("A1")
        self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        with self.assertRaises(ControlError):
            self.service.set_archived("A1", True)
        with self.assertRaises(ControlError):
            self.service.finish_task(task_ref="A1", thread_id=THREAD_TWO)
        completed = self.service.finish_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            terminal_revision=self.revision,
            repository_common_dir=self.common_dir,
        )
        self.assertEqual(completed["preparation_status"], "completed")
        self.assertEqual(self.service.set_archived("a1", True)["disposition"], "archived")

    def manifest(self, condition: str | None = None) -> dict:
        dependencies = []
        if condition:
            dependencies.append(
                {
                    "task": "frontend",
                    "blocked_by": "backend",
                    "condition": condition,
                    "reason": "Requires the integrated API contract",
                }
            )
        return {
            "initiative": {
                "title": "Checkout improvements",
                "brief": "Deliver backend and frontend changes with independent acceptance.",
            },
            "cards": [
                {
                    "key": "backend",
                    "title": "Backend contract",
                    "brief": "Implement and verify the API contract.",
                    "repository": str(self.repository),
                },
                {
                    "key": "frontend",
                    "title": "Frontend flow",
                    "brief": "Consume and verify the API contract.",
                    "repository": str(self.repository),
                },
            ],
            "dependencies": dependencies,
        }

    def decompose(self, condition: str | None = None) -> dict:
        return self.service.decompose_task(
            task_ref="A1",
            manifest=self.manifest(condition),
            confirmed=True,
            idempotency_key=f"decompose-{condition or 'parallel'}",
        )

    def test_decomposition_requires_confirmation_and_is_atomic_and_idempotent(self) -> None:
        source = self.create_task()
        with self.assertRaises(ControlError):
            self.service.decompose_task(
                task_ref="A1",
                manifest=self.manifest(),
                confirmed=False,
                idempotency_key="not-confirmed",
            )
        self.assertEqual([task["short_id"] for task in self.service.list_tasks()], ["A1"])
        invalid = self.manifest()
        invalid["dependencies"] = [
            {
                "task": "backend",
                "blocked_by": "frontend",
                "condition": "completed",
                "reason": "one",
            },
            {
                "task": "frontend",
                "blocked_by": "backend",
                "condition": "completed",
                "reason": "two",
            },
        ]
        with self.assertRaises(ControlError) as cycle:
            self.service.decompose_task(
                task_ref="A1", manifest=invalid, confirmed=True, idempotency_key="cycle"
            )
        self.assertIn("cycle", cycle.exception.reason)
        created = self.decompose()
        repeated = self.decompose()
        self.assertEqual(created["key_map"], {"backend": "A1", "frontend": "A2"})
        self.assertEqual(repeated["key_map"], created["key_map"])
        self.assertEqual(created["cards"][0]["id"], source["id"])
        self.assertEqual(created["cards"][0]["brief_revision"], 2)
        self.assertEqual(
            [item["short_id"] for item in created["cards"][0]["parallel_with"]], ["A2"]
        )
        self.assertEqual(self.create_task("after-decompose")["short_id"], "A3")

    def test_more_than_three_cards_requires_individual_reasons(self) -> None:
        self.create_task()
        manifest = self.manifest()
        manifest["cards"].extend(
            [
                {
                    "key": "docs",
                    "title": "Documentation",
                    "brief": "Document the contract.",
                    "repository": str(self.repository),
                },
                {
                    "key": "ops",
                    "title": "Operations",
                    "brief": "Verify operational acceptance.",
                    "repository": str(self.repository),
                },
            ]
        )
        with self.assertRaises(ControlError) as error:
            self.service.decompose_task(
                task_ref="A1", manifest=manifest, confirmed=True, idempotency_key="too-many"
            )
        self.assertIn("decomposition_reason", error.exception.reason)

    def test_completed_dependency_blocks_adoption_until_finish(self) -> None:
        self.create_task()
        self.decompose("completed")
        self.prepare("A1")
        self.prepare("A2")
        with self.assertRaises(ControlError) as blocked:
            self.service.adopt_task(
                task_ref="A2",
                thread_id=THREAD_TWO,
                repository=str(self.repository),
                current_revision=self.revision,
                repository_common_dir=self.common_dir,
                ancestor_contains=lambda _revision: True,
            )
        self.assertEqual(blocked.exception.status, "blocked")
        self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        self.service.finish_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            terminal_revision=self.revision,
            repository_common_dir=self.common_dir,
        )
        adopted = self.service.adopt_task(
            task_ref="A2",
            thread_id=THREAD_TWO,
            repository=str(self.repository),
            current_revision=self.revision,
            repository_common_dir=self.common_dir,
            ancestor_contains=lambda _revision: True,
        )
        self.assertEqual(adopted["preparation_status"], "adopted")

    def test_delivered_dependency_requires_evidence_and_checkout_containment(self) -> None:
        self.create_task()
        self.decompose("delivered")
        self.prepare("A1")
        self.prepare("A2")
        self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        self.service.finish_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            terminal_revision=self.revision,
            repository_common_dir=self.common_dir,
        )
        with self.assertRaises(ControlError):
            self.service.adopt_task(
                task_ref="A2",
                thread_id=THREAD_TWO,
                repository=str(self.repository),
                current_revision=self.revision,
                repository_common_dir=self.common_dir,
                ancestor_contains=lambda _revision: True,
            )
        delivered = self.service.record_delivery(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            task_revision=self.revision,
            delivery_revision=self.revision,
            kind="local-integration",
            repository_common_dir=self.common_dir,
        )
        self.assertEqual(delivered["delivery_revision"], self.revision)
        with self.assertRaises(ControlError) as stale:
            self.service.adopt_task(
                task_ref="A2",
                thread_id=THREAD_TWO,
                repository=str(self.repository),
                current_revision=self.revision,
                repository_common_dir=self.common_dir,
                ancestor_contains=lambda _revision: False,
            )
        self.assertIn("checkout-update-required", stale.exception.reason)
        adopted = self.service.adopt_task(
            task_ref="A2",
            thread_id=THREAD_TWO,
            repository=str(self.repository),
            current_revision=self.revision,
            repository_common_dir=self.common_dir,
            ancestor_contains=lambda revision: revision == self.revision,
        )
        self.assertEqual(adopted["preparation_status"], "adopted")

    def test_cli_adopt_uses_codex_thread_id_and_never_creates_checkout(self) -> None:
        self.create_task()
        self.prepare("A1")
        before = self.git("worktree", "list", "--porcelain").stdout
        result, missing = self.cli("task", "adopt", "--task", "A1", "--repository", str(self.repository))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(missing["status"], "blocked")
        result, adopted = self.cli(
            "task", "adopt", "--task", "a1", "--repository", str(self.repository), thread=THREAD_ONE
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(adopted["task"]["adopted_thread_id"], THREAD_ONE)
        self.assertEqual(before, self.git("worktree", "list", "--porcelain").stdout)

    def test_mcp_exposes_preparation_but_not_execution_or_ownership(self) -> None:
        process = subprocess.run(
            [sys.executable, str(MCP_HELPER)],
            cwd=ROOT,
            input="\n".join(
                (
                    json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}),
                    json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
                )
            ) + "\n",
            capture_output=True,
            text=True,
            check=True,
        )
        messages = [json.loads(line) for line in process.stdout.splitlines()]
        names = {tool["name"] for tool in messages[1]["result"]["tools"]}
        self.assertIn("task_prepare", names)
        self.assertIn("task_decompose", names)
        for forbidden in (
            "task_adopt",
            "task_transfer",
            "task_reclaim",
            "task_finish",
            "task_record_delivery",
            "run_start",
            "run_respond",
            "run_reopen",
            "run_reconcile",
            "run_interactions",
            "run_resolve",
        ):
            self.assertNotIn(forbidden, names)

    def test_mcp_decomposition_uses_structured_arrays(self) -> None:
        definition = TOOLS["task_decompose"]["inputSchema"]
        self.assertEqual(definition["properties"]["cards"]["type"], "array")
        self.assertEqual(definition["properties"]["dependencies"]["type"], "array")
        arguments = {
            "task": "A1",
            "initiative": self.manifest()["initiative"],
            "cards": self.manifest()["cards"],
            "dependencies": [],
            "confirmed": True,
            "idempotency_key": "mcp-decompose",
        }
        command = cli_arguments("task_decompose", arguments)
        self.assertEqual(command[:2], ["task", "decompose"])
        encoded = command[command.index("--manifest-json") + 1]
        self.assertEqual(json.loads(encoded)["cards"], arguments["cards"])

    def test_schema_v2_migration_preserves_legacy_rows_without_short_ids(self) -> None:
        self.state_root.mkdir(mode=0o700)
        database = self.state_root / "control.sqlite3"
        connection = sqlite3.connect(database)
        try:
            connection.executescript(
                """
                CREATE TABLE tasks (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, brief TEXT NOT NULL,
                    brief_revision INTEGER NOT NULL DEFAULT 1,
                    source_harness TEXT NOT NULL, source_conversation TEXT NOT NULL,
                    source_message TEXT NOT NULL, repository TEXT, rank INTEGER NOT NULL,
                    disposition TEXT NOT NULL, idempotency_key TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE task_notes (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
                    body TEXT NOT NULL, source_harness TEXT NOT NULL,
                    source_reference TEXT NOT NULL, idempotency_key TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE runs (
                    id TEXT PRIMARY KEY, task_id TEXT NOT NULL REFERENCES tasks(id),
                    repository TEXT NOT NULL, base_revision TEXT NOT NULL,
                    delivery TEXT NOT NULL, status TEXT NOT NULL, thread_uuid TEXT,
                    active_turn_id TEXT, last_turn_id TEXT, last_result_kind TEXT,
                    last_result_json TEXT, retained_resources_json TEXT NOT NULL DEFAULT '[]',
                    cancel_requested_at TEXT, cancelled_at TEXT,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE turns (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    idempotency_key TEXT NOT NULL UNIQUE, input_digest TEXT NOT NULL,
                    input_text TEXT NOT NULL, response_to TEXT, status TEXT NOT NULL,
                    turn_uuid TEXT, result_json TEXT, created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE interactions (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    turn_record_id TEXT NOT NULL REFERENCES turns(id), thread_uuid TEXT NOT NULL,
                    turn_uuid TEXT NOT NULL, item_id TEXT, method TEXT NOT NULL,
                    params_json TEXT NOT NULL, fingerprint TEXT NOT NULL, status TEXT NOT NULL,
                    response_json TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                PRAGMA user_version = 2;
                """
            )
            connection.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, 1, ?, '', '', NULL, 1, 'open', ?, ?, ?)",
                ("legacy-uuid", "Legacy", "Old task", "test", "legacy-key", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
            )
            connection.commit()
        finally:
            connection.close()
        os.chmod(database, 0o600)
        legacy = self.service.get_task("legacy-uuid")
        self.assertIsNone(legacy["short_id"])
        self.assertEqual(legacy["preparation_status"], "legacy")
        self.assertEqual(self.create_task()["short_id"], "A1")
        connection = sqlite3.connect(database)
        try:
            self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)
        finally:
            connection.close()

    def test_schema_v3_migration_preserves_prepared_cards(self) -> None:
        created = self.create_task()
        database = self.state_root / "control.sqlite3"
        connection = sqlite3.connect(database)
        try:
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("DROP TABLE task_dependencies")
            connection.execute("DROP INDEX tasks_initiative")
            for column in (
                "previous_harness",
                "adopted_harness",
                "delivered_at",
                "delivery_kind",
                "delivery_revision",
                "delivered_task_revision",
                "completed_revision",
                "repository_common_dir",
                "decomposition_reason",
                "initiative_id",
            ):
                connection.execute(f"ALTER TABLE tasks DROP COLUMN {column}")
            connection.execute("DROP TABLE task_initiatives")
            connection.execute("PRAGMA user_version = 3")
            connection.commit()
        finally:
            connection.close()
        migrated = self.service.get_task("A1")
        self.assertEqual(migrated["id"], created["id"])
        self.assertIsNone(migrated["initiative_id"])
        connection = sqlite3.connect(database)
        try:
            self.assertEqual(
                connection.execute("PRAGMA user_version").fetchone()[0],
                SCHEMA_VERSION,
            )
        finally:
            connection.close()

    def test_schema_v4_migration_namespaces_historical_owners_as_codex(self) -> None:
        self.create_task()
        self.prepare("A1")
        self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
        )
        self.service.reclaim_task(
            task_ref="A1",
            thread_id=THREAD_TWO,
            repository=str(self.repository),
            current_revision=self.revision,
            authorized=True,
        )
        database = self.state_root / "control.sqlite3"
        connection = sqlite3.connect(database)
        try:
            connection.execute("ALTER TABLE tasks DROP COLUMN previous_harness")
            connection.execute("ALTER TABLE tasks DROP COLUMN adopted_harness")
            connection.execute("PRAGMA user_version = 4")
            connection.commit()
        finally:
            connection.close()
        migrated = self.service.get_task("A1")
        self.assertEqual(migrated["adopted_thread_id"], THREAD_TWO)
        self.assertEqual(migrated["adopted_harness"], "codex")
        self.assertEqual(migrated["previous_thread_id"], THREAD_ONE)
        self.assertEqual(migrated["previous_harness"], "codex")

    def test_equal_textual_ids_from_different_hosts_are_distinct_owners(self) -> None:
        self.create_task()
        self.prepare("A1")
        adopted = self.service.adopt_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
            source_harness="cursor",
        )
        self.assertEqual(adopted["adopted_harness"], "cursor")
        with self.assertRaises(ControlError) as busy:
            self.service.adopt_task(
                task_ref="A1",
                thread_id=THREAD_ONE,
                repository=str(self.repository),
                current_revision=self.revision,
                source_harness="codex",
            )
        self.assertEqual(busy.exception.status, "busy")
        reclaimed = self.service.reclaim_task(
            task_ref="A1",
            thread_id=THREAD_ONE,
            repository=str(self.repository),
            current_revision=self.revision,
            authorized=True,
            source_harness="codex",
        )
        self.assertEqual(reclaimed["adopted_harness"], "codex")
        self.assertEqual(reclaimed["previous_harness"], "cursor")


if __name__ == "__main__":
    unittest.main()
