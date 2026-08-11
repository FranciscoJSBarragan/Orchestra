"""Tests for durable task intake and exact App Server continuity."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[2]
CONTROL_ROOT = ROOT / "codex/control"
sys.path.insert(0, str(CONTROL_ROOT))

from orchestra_control.service import ControlError, ControlService  # noqa: E402


HELPER = ROOT / "codex/scripts/task_control.py"
MCP_HELPER = ROOT / "codex/scripts/task_mcp.py"
THREAD_UUID = "11111111-1111-4111-8111-111111111111"
TURN_UUID = "22222222-2222-4222-8222-222222222222"


FAKE_CODEX = r'''#!/usr/bin/env python3
import json
import sys

thread_id = "11111111-1111-4111-8111-111111111111"
turn_id = "22222222-2222-4222-8222-222222222222"
result = {
    "kind": "tier_selection",
    "checkpoint_id": "tier-1",
    "message": "Choose standard or critical.",
    "recommended_tier": "standard",
    "artifacts": [],
    "retained_resources": [],
}
item = {"type": "agentMessage", "phase": "final_answer", "text": json.dumps(result)}
for line in sys.stdin:
    message = json.loads(line)
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}
    if method == "initialize":
        print(json.dumps({"id": request_id, "result": {}}), flush=True)
    elif method == "initialized":
        continue
    elif method in ("thread/start", "thread/resume"):
        if method == "thread/resume":
            assert params["threadId"] == thread_id
        print(json.dumps({"id": request_id, "result": {"thread": {"id": thread_id, "turns": []}, "cwd": params["cwd"]}}), flush=True)
    elif method == "thread/read":
        completed = {"id": turn_id, "status": "completed", "items": [item]}
        print(json.dumps({"id": request_id, "result": {"thread": {"id": thread_id, "turns": [completed]}}}), flush=True)
    elif method == "turn/start":
        assert params["threadId"] == thread_id
        assert params["clientUserMessageId"]
        assert params["outputSchema"]["additionalProperties"] is False
        print(json.dumps({"id": request_id, "result": {"turn": {"id": turn_id, "status": "inProgress", "items": []}}}), flush=True)
        print(json.dumps({"method": "item/completed", "params": {"threadId": thread_id, "turnId": turn_id, "item": item}}), flush=True)
        print(json.dumps({"method": "turn/completed", "params": {"threadId": thread_id, "turn": {"id": turn_id, "status": "completed", "items": []}}}), flush=True)
    elif method in ("thread/archive", "thread/unarchive"):
        assert params["threadId"] == thread_id
        print(json.dumps({"id": request_id, "result": {}}), flush=True)
'''

INTERRUPTIBLE_CODEX = r'''#!/usr/bin/env python3
import json
import sys
thread_id = "11111111-1111-4111-8111-111111111111"
turn_id = "22222222-2222-4222-8222-222222222222"
for line in sys.stdin:
    message = json.loads(line)
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        print(json.dumps({"id": request_id, "result": {}}), flush=True)
    elif method == "initialized":
        continue
    elif method == "thread/start":
        print(json.dumps({"id": request_id, "result": {"thread": {"id": thread_id}}}), flush=True)
    elif method == "turn/start":
        print(json.dumps({"id": request_id, "result": {"turn": {"id": turn_id, "status": "inProgress"}}}), flush=True)
    elif method == "turn/interrupt":
        print(json.dumps({"id": request_id, "result": {}}), flush=True)
        print(json.dumps({"method": "turn/completed", "params": {"threadId": thread_id, "turn": {"id": turn_id, "status": "interrupted", "items": []}}}), flush=True)
'''

INTERACTIVE_CODEX = INTERRUPTIBLE_CODEX.replace(
    'print(json.dumps({"id": request_id, "result": {"turn": {"id": turn_id, "status": "inProgress"}}}), flush=True)',
    'print(json.dumps({"id": request_id, "result": {"turn": {"id": turn_id, "status": "inProgress"}}}), flush=True)\n'
    '        print(json.dumps({"id": 90, "method": "item/commandExecution/requestApproval", "params": {"threadId": thread_id, "turnId": turn_id, "itemId": "command-1", "command": "make test"}}), flush=True)'
)


class TaskControlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.state_root = self.root / "state"
        self.service = ControlService(self.state_root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def create_task(self, key: str = "capture-1") -> dict[str, object]:
        return self.service.create_task(
            title="Durable task",
            brief="Inspect the repository and prepare a candidate specification.",
            source_harness="test",
            idempotency_key=key,
        )

    def test_capture_is_idempotent_and_database_is_private(self) -> None:
        first = self.create_task()
        second = self.create_task()
        self.assertEqual(first["id"], second["id"])
        database = self.state_root / "control.sqlite3"
        self.assertEqual(stat.S_IMODE(database.stat().st_mode), 0o600)
        self.assertEqual(len(self.service.list_tasks()), 1)

    def test_capture_preserves_structured_brief_and_note_text(self) -> None:
        task = self.service.create_task(
            title="Structured task",
            brief="Objective\n\n- acceptance one\n- acceptance two",
            source_harness="test",
            idempotency_key="structured-task",
        )
        note = self.service.add_note(
            task_id=str(task["id"]),
            body="Context\n\n```text\nexact value\n```",
            source_harness="test",
            source_reference="message-structured",
            idempotency_key="structured-note",
        )
        self.assertEqual(task["brief"], "Objective\n\n- acceptance one\n- acceptance two")
        self.assertEqual(note["body"], "Context\n\n```text\nexact value\n```")

    def test_conflicting_idempotency_keys_are_rejected(self) -> None:
        task = self.create_task()
        with self.assertRaises(ControlError) as task_error:
            self.service.create_task(
                title="Different task",
                brief="Different brief",
                source_harness="test",
                idempotency_key="capture-1",
            )
        self.assertEqual(task_error.exception.status, "invalid")
        self.service.add_note(
            task_id=str(task["id"]),
            body="Original note",
            source_harness="test",
            source_reference="message-1",
            idempotency_key="note-conflict",
        )
        with self.assertRaises(ControlError) as note_error:
            self.service.add_note(
                task_id=str(task["id"]),
                body="Different note",
                source_harness="test",
                source_reference="message-2",
                idempotency_key="note-conflict",
            )
        self.assertEqual(note_error.exception.status, "invalid")

    def test_notes_and_archive_are_recoverable(self) -> None:
        task = self.create_task()
        first = self.service.add_note(
            task_id=str(task["id"]),
            body="A later thought",
            source_harness="test",
            source_reference="message-2",
            idempotency_key="note-1",
        )
        second = self.service.add_note(
            task_id=str(task["id"]),
            body="A later thought",
            source_harness="test",
            source_reference="message-2",
            idempotency_key="note-1",
        )
        self.assertEqual(first["id"], second["id"])
        self.service.set_archived(str(task["id"]), True)
        self.assertEqual(self.service.list_tasks(), [])
        self.service.set_archived(str(task["id"]), False)
        self.assertEqual(len(self.service.get_task(str(task["id"]))["notes"]), 1)

    def test_archive_rejects_an_unresolved_turn(self) -> None:
        task = self.create_task()
        run = self.service.prepare_run(str(task["id"]), "/tmp/repository", "a" * 40)
        turn = self.service.prepare_turn(
            run_id=str(run["id"]), text="choose standard", idempotency_key="turn-1"
        )
        self.service.update_transport(
            run_id=str(run["id"]), turn_record_id=str(turn["id"]), active_turn_id=TURN_UUID
        )
        with self.assertRaises(ControlError) as raised:
            self.service.set_archived(str(task["id"]), True)
        self.assertEqual(raised.exception.status, "busy")

    def test_cancel_and_reopen_preserve_thread_and_checkpoint(self) -> None:
        task = self.create_task()
        run = self.service.prepare_run(str(task["id"]), "/tmp/repository", "a" * 40)
        turn = self.service.prepare_turn(
            run_id=str(run["id"]), text="checkpoint", idempotency_key="turn-cancel"
        )
        checkpoint = {
            "kind": "tier_selection",
            "checkpoint_id": "tier-1",
            "message": "Choose a tier",
            "recommended_tier": "standard",
            "artifacts": [],
            "retained_resources": [],
        }
        self.service.update_transport(
            run_id=str(run["id"]), turn_record_id=str(turn["id"]), thread_uuid=THREAD_UUID,
            active_turn_id=TURN_UUID, completed_result=checkpoint,
        )
        cancelled = self.service.request_cancel(str(task["id"]))
        self.assertEqual(cancelled["status"], "cancelled")
        self.assertEqual(cancelled["thread_uuid"], THREAD_UUID)
        self.assertEqual(cancelled["last_result_kind"], "tier_selection")
        reopened = self.service.reopen(str(task["id"]))
        self.assertEqual(reopened["status"], "ready")
        self.assertEqual(reopened["thread_uuid"], THREAD_UUID)
        self.assertEqual(reopened["last_result_kind"], "tier_selection")

    def test_interaction_response_is_exact_and_consumed_once(self) -> None:
        task = self.create_task()
        run = self.service.prepare_run(str(task["id"]), "/tmp/repository", "a" * 40)
        turn = self.service.prepare_turn(
            run_id=str(run["id"]), text="approve", idempotency_key="turn-interaction"
        )
        values = dict(
            run_id=str(run["id"]), turn_record_id=str(turn["id"]),
            thread_uuid=THREAD_UUID, turn_uuid=TURN_UUID, item_id="item-1",
            method="item/commandExecution/requestApproval",
            params={"threadId": THREAD_UUID, "turnId": TURN_UUID, "itemId": "item-1"},
            fingerprint="exact-fingerprint",
        )
        pending, response = self.service.record_interaction(**values)
        self.assertEqual(pending["status"], "pending")
        self.assertIsNone(response)
        self.service.resolve_interaction(str(pending["id"]), {"decision": "accept"})
        consumed, response = self.service.record_interaction(**values)
        self.assertEqual(consumed["status"], "consumed")
        self.assertEqual(response, {"decision": "accept"})
        next_pending, response = self.service.record_interaction(**values)
        self.assertEqual(next_pending["status"], "pending")
        self.assertIsNone(response)

    def test_list_includes_latest_run_and_pending_interaction_summary(self) -> None:
        task = self.create_task()
        run = self.service.prepare_run(str(task["id"]), "/tmp/repository", "a" * 40)
        turn = self.service.prepare_turn(
            run_id=str(run["id"]), text="approve", idempotency_key="turn-summary"
        )
        self.service.record_interaction(
            run_id=str(run["id"]), turn_record_id=str(turn["id"]),
            thread_uuid=THREAD_UUID, turn_uuid=TURN_UUID, item_id=None,
            method="example/request", params={}, fingerprint="summary-fingerprint",
        )
        listed = self.service.list_tasks()[0]
        self.assertEqual(listed["latest_run"]["id"], run["id"])
        self.assertEqual(listed["pending_interactions"], 1)

    def test_mcp_lists_tools_and_creates_a_task_through_the_canonical_cli(self) -> None:
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05"}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "task_create", "arguments": {"title": "From MCP", "brief": "Durable brief", "idempotency_key": "mcp-create"}}},
        ]
        environment = dict(os.environ)
        environment["HOME"] = str(self.root / "mcp-home")
        completed = subprocess.run(
            [sys.executable, str(MCP_HELPER)],
            input="".join(json.dumps(item) + "\n" for item in requests),
            capture_output=True, text=True, env=environment, check=True,
        )
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(responses[0]["result"]["protocolVersion"], "2024-11-05")
        tool_names = {item["name"] for item in responses[1]["result"]["tools"]}
        self.assertIn("task_cancel", tool_names)
        self.assertIn("run_resolve", tool_names)
        self.assertEqual(responses[2]["result"]["structuredContent"]["status"], "ok")

    def test_active_driver_observes_external_cancel_and_interrupts_exact_turn(self) -> None:
        repository = self.root / "interrupt-repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
        (repository / "README.md").write_text("canary\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repository), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(repository), "commit", "-qm", "canary"], check=True)
        task = self.service.create_task(
            title="Interrupt", brief="Wait for cancellation", source_harness="test",
            repository=str(repository), idempotency_key="interrupt-task",
        )
        fake = self.root / "interruptible-codex"
        fake.write_text(INTERRUPTIBLE_CODEX, encoding="utf-8")
        fake.chmod(0o755)
        process = subprocess.Popen(
            [sys.executable, str(HELPER), "--state-root", str(self.state_root),
             "run", "start", "--task", str(task["id"]), "--codex-bin", str(fake)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            for _ in range(100):
                try:
                    run = self.service.latest_run(str(task["id"]))
                except ControlError:
                    time.sleep(0.02)
                    continue
                if run.get("active_turn_id") == TURN_UUID:
                    break
                time.sleep(0.02)
            else:
                self.fail("driver did not persist the active turn")
            cancelled = subprocess.run(
                [sys.executable, str(HELPER), "--state-root", str(self.state_root),
                 "task", "cancel", "--task", str(task["id"])],
                capture_output=True, text=True, check=True,
            )
            self.assertEqual(json.loads(cancelled.stdout)["run"]["status"], "cancelling")
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            result = json.loads(stdout)["run"]
            self.assertEqual(result["status"], "cancelled")
            self.assertEqual(result["thread_uuid"], THREAD_UUID)
            self.assertIsNone(result["active_turn_id"])
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

    def test_interactive_app_server_request_is_persisted_and_stops_needs_user(self) -> None:
        repository = self.root / "interaction-repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
        (repository / "README.md").write_text("canary\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repository), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(repository), "commit", "-qm", "canary"], check=True)
        task = self.service.create_task(
            title="Interaction", brief="Request approval", source_harness="test",
            repository=str(repository), idempotency_key="interaction-task",
        )
        fake = self.root / "interactive-codex"
        fake.write_text(INTERACTIVE_CODEX, encoding="utf-8")
        fake.chmod(0o755)
        started = subprocess.run(
            [sys.executable, str(HELPER), "--state-root", str(self.state_root),
             "run", "start", "--task", str(task["id"]), "--codex-bin", str(fake)],
            capture_output=True, text=True, check=True, timeout=5,
        )
        run = json.loads(started.stdout)["run"]
        self.assertEqual(run["status"], "waiting_user")
        self.assertIsNone(run["active_turn_id"])
        interactions = self.service.list_interactions(str(task["id"]))
        self.assertEqual(len(interactions), 1)
        self.assertEqual(interactions[0]["status"], "pending")
        self.assertEqual(interactions[0]["item_id"], "command-1")

    def test_cli_starts_one_persistent_thread_with_structured_checkpoint(self) -> None:
        repository = self.root / "repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        subprocess.run(["git", "-C", str(repository), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(repository), "config", "user.email", "test@example.invalid"], check=True)
        (repository / "README.md").write_text("canary\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repository), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(repository), "commit", "-qm", "canary"], check=True)
        fake = self.root / "fake-codex"
        fake.write_text(FAKE_CODEX, encoding="utf-8")
        fake.chmod(0o755)

        create = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--state-root",
                str(self.state_root),
                "task",
                "create",
                "--title",
                "Canary",
                "--brief",
                "Prepare discovery",
                "--repository",
                str(repository),
                "--idempotency-key",
                "create-canary",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        task_id = json.loads(create.stdout)["task"]["id"]
        started = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--state-root",
                str(self.state_root),
                "run",
                "start",
                "--task",
                task_id,
                "--codex-bin",
                str(fake),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(started.stdout)
        self.assertEqual(payload["run"]["thread_uuid"], THREAD_UUID)
        self.assertEqual(payload["run"]["last_result_kind"], "tier_selection")
        self.assertEqual(payload["run"]["status"], "waiting_user")

    def test_reconcile_adopts_only_the_exact_persisted_completed_turn(self) -> None:
        task = self.create_task()
        run = self.service.prepare_run(str(task["id"]), "/tmp/repository", "a" * 40)
        turn = self.service.prepare_turn(
            run_id=str(run["id"]), text="choose standard", idempotency_key="turn-reconcile"
        )
        self.service.update_transport(
            run_id=str(run["id"]), turn_record_id=str(turn["id"]), thread_uuid=THREAD_UUID
        )
        self.service.update_transport(
            run_id=str(run["id"]), turn_record_id=str(turn["id"]), active_turn_id=TURN_UUID
        )
        self.service.update_transport(
            run_id=str(run["id"]),
            turn_record_id=str(turn["id"]),
            ambiguous="launcher stopped after turn/start",
        )
        fake = self.root / "fake-codex"
        fake.write_text(FAKE_CODEX, encoding="utf-8")
        fake.chmod(0o755)

        reconciled = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--state-root",
                str(self.state_root),
                "run",
                "reconcile",
                "--task",
                str(task["id"]),
                "--codex-bin",
                str(fake),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(reconciled.stdout)
        self.assertEqual(payload["run"]["status"], "waiting_user")
        self.assertEqual(payload["run"]["last_result_kind"], "tier_selection")
        self.assertIsNone(payload["run"]["active_turn_id"])

    def test_cli_archive_and_restore_mirror_the_persistent_thread(self) -> None:
        task = self.create_task()
        run = self.service.prepare_run(str(task["id"]), "/tmp/repository", "a" * 40)
        turn = self.service.prepare_turn(
            run_id=str(run["id"]), text="prepare discovery", idempotency_key="turn-archive"
        )
        self.service.update_transport(
            run_id=str(run["id"]), turn_record_id=str(turn["id"]), thread_uuid=THREAD_UUID
        )
        fake = self.root / "fake-codex"
        fake.write_text(FAKE_CODEX, encoding="utf-8")
        fake.chmod(0o755)

        for command, disposition in (("archive", "archived"), ("restore", "open")):
            changed = subprocess.run(
                [
                    sys.executable,
                    str(HELPER),
                    "--state-root",
                    str(self.state_root),
                    "task",
                    command,
                    "--task",
                    str(task["id"]),
                    "--codex-bin",
                    str(fake),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertEqual(json.loads(changed.stdout)["task"]["disposition"], disposition)


if __name__ == "__main__":
    unittest.main()
