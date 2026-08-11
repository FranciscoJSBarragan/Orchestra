"""One-turn Codex App Server client with fail-closed continuity."""

from __future__ import annotations

import json
import queue
from pathlib import Path
import subprocess
import threading
from typing import Any, Callable
import uuid


RESULT_KINDS = (
    "tier_selection",
    "discovery_spec",
    "plan_checkpoint",
    "needs_user",
    "blocked",
    "implementation_complete",
    "needs_reconciliation",
)

RESULT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": list(RESULT_KINDS)},
        "checkpoint_id": {"type": ["string", "null"]},
        "message": {"type": "string"},
        "recommended_tier": {"type": ["string", "null"], "enum": ["standard", "critical", None]},
        "artifacts": {"type": "array", "items": {"type": "string"}},
        "retained_resources": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "kind",
        "checkpoint_id",
        "message",
        "recommended_tier",
        "artifacts",
        "retained_resources",
    ],
    "additionalProperties": False,
}
RESULT_FIELDS = frozenset(RESULT_SCHEMA["required"])


class AppServerError(Exception):
    def __init__(self, reason: str, *, ambiguous: bool = False) -> None:
        super().__init__(reason)
        self.reason = reason
        self.ambiguous = ambiguous


class TurnInterrupted(AppServerError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def valid_uuid(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise AppServerError(f"{label} is missing")
    try:
        uuid.UUID(value)
    except ValueError as error:
        raise AppServerError(f"{label} is not a UUID") from error
    return value


class Client:
    def __init__(
        self,
        process: subprocess.Popen[str],
        server_request_handler: Callable[[str, dict[str, Any]], dict[str, Any] | None] | None = None,
    ) -> None:
        if process.stdin is None or process.stdout is None:
            raise AppServerError("App Server stdio is unavailable")
        self.process = process
        self.stdin = process.stdin
        self.stdout = process.stdout
        self.request_id = 0
        self.notifications: list[dict[str, Any]] = []
        self._stderr_chunks: list[str] = []
        self._stderr_lock = threading.Lock()
        self._messages: queue.Queue[str | None] = queue.Queue()
        self.server_request_handler = server_request_handler
        self.interaction_waiting = False
        if process.stderr is not None:
            threading.Thread(target=self._drain_stderr, daemon=True).start()
        threading.Thread(target=self._drain_stdout, daemon=True).start()

    def _drain_stdout(self) -> None:
        while True:
            line = self.stdout.readline()
            if not line:
                self._messages.put(None)
                return
            self._messages.put(line)

    def _drain_stderr(self) -> None:
        assert self.process.stderr is not None
        while True:
            chunk = self.process.stderr.read(1024)
            if not chunk:
                return
            with self._stderr_lock:
                self._stderr_chunks.append(chunk)
                joined = "".join(self._stderr_chunks)
                self._stderr_chunks = [joined[-4000:]]

    def stderr_detail(self) -> str:
        with self._stderr_lock:
            return "".join(self._stderr_chunks).strip()

    def _send(self, message: dict[str, Any]) -> None:
        try:
            self.stdin.write(json.dumps(message, separators=(",", ":")) + "\n")
            self.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise AppServerError(f"cannot write to App Server: {error}", ambiguous=True) from error

    def notify(self, method: str, params: dict[str, Any]) -> None:
        self._send({"method": method, "params": params})

    def _read(self, timeout: float | None = None) -> dict[str, Any] | None:
        try:
            line = self._messages.get(timeout=timeout) if timeout is not None else self._messages.get()
        except queue.Empty:
            return None
        if line is None:
            detail = self.stderr_detail()
            raise AppServerError(detail or "App Server closed stdout", ambiguous=True)
        try:
            message = json.loads(line)
        except json.JSONDecodeError as error:
            raise AppServerError("App Server emitted invalid JSON", ambiguous=True) from error
        if not isinstance(message, dict):
            raise AppServerError("App Server emitted a non-object message", ambiguous=True)
        return message

    def _dispatch(self, message: dict[str, Any]) -> None:
        method = message.get("method")
        if "id" in message and isinstance(method, str):
            params = message.get("params")
            if not isinstance(params, dict):
                params = {}
            response = (
                self.server_request_handler(method, params)
                if self.server_request_handler is not None
                else None
            )
            if response is None:
                self._send({
                    "id": message["id"],
                    "error": {
                        "code": -32000,
                        "message": "interaction persisted; explicit user response required",
                    },
                })
                self.interaction_waiting = True
            else:
                self._send({"id": message["id"], "result": response})
            return
        if isinstance(method, str):
            self.notifications.append(message)

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.request_id += 1
        request_id = self.request_id
        self._send({"id": request_id, "method": method, "params": params})
        while True:
            message = self._read()
            assert message is not None
            if message.get("id") != request_id:
                self._dispatch(message)
                continue
            if "error" in message:
                raise AppServerError(
                    f"{method} rejected: {json.dumps(message['error'], sort_keys=True)}"
                )
            result = message.get("result", {})
            if not isinstance(result, dict):
                raise AppServerError(f"{method} returned a non-object result")
            return result

    def wait_for_turn(
        self,
        thread_id: str,
        turn_id: str,
        should_cancel: Callable[[], bool] | None = None,
    ) -> dict[str, Any]:
        interrupt_sent = False
        while True:
            pending = list(self.notifications)
            self.notifications.clear()
            for message in pending:
                completion = _completion(message, thread_id, turn_id)
                if completion is not None:
                    return completion
                self.notifications.append(message)
            if (self.interaction_waiting or (should_cancel is not None and should_cancel())) and not interrupt_sent:
                self.request_id += 1
                self._send({
                    "id": self.request_id,
                    "method": "turn/interrupt",
                    "params": {"threadId": thread_id, "turnId": turn_id},
                })
                interrupt_sent = True
            message = self._read(timeout=0.25)
            if message is None:
                if interrupt_sent and self.process.poll() is not None:
                    raise AppServerError("App Server exited while interrupting turn", ambiguous=True)
                continue
            completion = _completion(message, thread_id, turn_id)
            if completion is not None:
                return completion
            self._dispatch(message)


def _completion(message: dict[str, Any], thread_id: str, turn_id: str) -> dict[str, Any] | None:
    if message.get("method") != "turn/completed":
        return None
    params = message.get("params")
    if not isinstance(params, dict) or params.get("threadId") != thread_id:
        return None
    turn = params.get("turn")
    if not isinstance(turn, dict) or turn.get("id") != turn_id:
        return None
    return turn


def _final_result(notifications: list[dict[str, Any]], turn: dict[str, Any]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for message in notifications:
        if message.get("method") != "item/completed":
            continue
        params = message.get("params")
        item = params.get("item") if isinstance(params, dict) else None
        if isinstance(item, dict):
            items.append(item)
    for item in turn.get("items", []):
        if isinstance(item, dict):
            items.append(item)
    messages = [
        item
        for item in items
        if item.get("type") == "agentMessage" and item.get("phase") in (None, "final_answer")
    ]
    if not messages:
        raise AppServerError("completed turn omitted a final agentMessage", ambiguous=True)
    text = messages[-1].get("text")
    if not isinstance(text, str):
        raise AppServerError("final agentMessage omitted text", ambiguous=True)
    try:
        result = json.loads(text)
    except json.JSONDecodeError as error:
        raise AppServerError("final agentMessage violated outputSchema", ambiguous=True) from error
    if not isinstance(result, dict) or set(result) != RESULT_FIELDS:
        raise AppServerError("structured result has invalid fields", ambiguous=True)
    if result.get("kind") not in RESULT_KINDS:
        raise AppServerError("structured result has an invalid kind", ambiguous=True)
    if result.get("checkpoint_id") is not None and not isinstance(result["checkpoint_id"], str):
        raise AppServerError("structured result has an invalid checkpoint_id", ambiguous=True)
    if not isinstance(result.get("message"), str):
        raise AppServerError("structured result has an invalid message", ambiguous=True)
    if result.get("recommended_tier") not in (None, "standard", "critical"):
        raise AppServerError("structured result has an invalid recommended_tier", ambiguous=True)
    for field in ("artifacts", "retained_resources"):
        value = result.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise AppServerError(f"structured result has invalid {field}", ambiguous=True)
    return result


def completed_result_from_thread(
    payload: dict[str, Any], *, thread_uuid: str, turn_uuid: str
) -> dict[str, Any] | None:
    """Return the exact terminal turn result, or None when it is not safely adoptable."""

    thread = payload.get("thread")
    if not isinstance(thread, dict) or thread.get("id") != thread_uuid:
        raise AppServerError("thread/read did not return the persisted thread UUID", ambiguous=True)
    turns = thread.get("turns")
    if not isinstance(turns, list):
        raise AppServerError("thread/read omitted turns", ambiguous=True)
    matches = [turn for turn in turns if isinstance(turn, dict) and turn.get("id") == turn_uuid]
    if len(matches) > 1:
        raise AppServerError("thread/read returned the active turn more than once", ambiguous=True)
    if not matches or matches[0].get("status") != "completed":
        return None
    return _final_result([], matches[0])


def execute_turn(
    *,
    codex_bin: str,
    repository: Path,
    prompt: str,
    thread_uuid: str | None,
    model: str,
    effort: str,
    message_id: str,
    on_thread: Callable[[str], None],
    on_turn: Callable[[str], None],
    should_cancel: Callable[[], bool] | None = None,
    on_interaction: Callable[[str, dict[str, Any]], dict[str, Any] | None] | None = None,
) -> tuple[str, str, dict[str, Any]]:
    try:
        process = subprocess.Popen(
            [codex_bin, "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except OSError as error:
        raise AppServerError(f"cannot launch Codex App Server: {error}") from error
    client = Client(process, on_interaction)
    try:
        client.request(
            "initialize",
            {
                "clientInfo": {
                    "name": "orchestra_task_control",
                    "title": "Orchestra Task Control",
                    "version": "0.1.0",
                },
                "capabilities": {"experimentalApi": True},
            },
        )
        client.notify("initialized", {})
        params = {"cwd": str(repository), "model": model, "config": {"model_reasoning_effort": effort}}
        if thread_uuid is None:
            thread_result = client.request(
                "thread/start", {**params, "ephemeral": False, "threadSource": "vscode"}
            )
        else:
            thread_result = client.request("thread/resume", {**params, "threadId": thread_uuid})
        thread = thread_result.get("thread")
        if not isinstance(thread, dict):
            raise AppServerError("thread response omitted metadata", ambiguous=thread_uuid is None)
        observed_thread = valid_uuid(thread.get("id"), "thread UUID")
        if thread_uuid is not None and observed_thread != thread_uuid:
            raise AppServerError("App Server resumed a different UUID")
        on_thread(observed_thread)
        turn_result = client.request(
            "turn/start",
            {
                "threadId": observed_thread,
                "input": [{"type": "text", "text": prompt}],
                "clientUserMessageId": message_id,
                "cwd": str(repository),
                "model": model,
                "effort": effort,
                "outputSchema": RESULT_SCHEMA,
            },
        )
        turn = turn_result.get("turn")
        if not isinstance(turn, dict):
            raise AppServerError("turn/start omitted turn metadata", ambiguous=True)
        turn_id = valid_uuid(turn.get("id"), "turn UUID")
        on_turn(turn_id)
        completed = client.wait_for_turn(observed_thread, turn_id, should_cancel)
        if completed.get("status") == "interrupted":
            reason = "needs_user" if client.interaction_waiting else "cancelled"
            raise TurnInterrupted(reason)
        if completed.get("status") != "completed":
            raise AppServerError(f"turn ended with status {completed.get('status', 'unknown')}")
        return observed_thread, turn_id, _final_result(client.notifications, completed)
    finally:
        _stop_process(process)


def _stop_process(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def read_thread(*, codex_bin: str, thread_uuid: str) -> dict[str, Any]:
    process = subprocess.Popen(
        [codex_bin, "app-server", "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    client = Client(process)
    try:
        client.request(
            "initialize",
            {"clientInfo": {"name": "orchestra_task_control", "title": "Orchestra Task Control", "version": "0.1.0"}},
        )
        client.notify("initialized", {})
        return client.request("thread/read", {"threadId": thread_uuid, "includeTurns": True})
    finally:
        _stop_process(process)


def set_thread_archived(*, codex_bin: str, thread_uuid: str, archived: bool) -> None:
    process = subprocess.Popen(
        [codex_bin, "app-server", "--stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    client = Client(process)
    try:
        client.request(
            "initialize",
            {"clientInfo": {"name": "orchestra_task_control", "title": "Orchestra Task Control", "version": "0.1.0"}},
        )
        client.notify("initialized", {})
        method = "thread/archive" if archived else "thread/unarchive"
        client.request(method, {"threadId": thread_uuid})
    finally:
        _stop_process(process)
