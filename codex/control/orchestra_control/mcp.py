"""Harness-neutral stdio MCP adapter for Orchestra task control."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any


PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18")


def schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


S = {"type": "string"}
TOOLS: dict[str, dict[str, Any]] = {
    "task_create": {"description": "Create one durable task.", "inputSchema": schema({"title": S, "brief": S, "source_harness": S, "source_conversation": S, "source_message": S, "repository": S, "idempotency_key": S}, ["title", "brief"]), "readOnly": False},
    "task_get": {"description": "Get a durable task with notes and runs.", "inputSchema": schema({"task": S}, ["task"]), "readOnly": True},
    "task_list": {"description": "List durable inbox tasks.", "inputSchema": schema({"include_archived": {"type": "boolean"}}), "readOnly": True},
    "task_note": {"description": "Attach durable context to a task.", "inputSchema": schema({"task": S, "body": S, "source_harness": S, "source_reference": S, "idempotency_key": S}, ["task", "body"]), "readOnly": False},
    "task_archive": {"description": "Archive a non-running task and its Codex thread.", "inputSchema": schema({"task": S, "codex_bin": S}, ["task"]), "readOnly": False},
    "task_restore": {"description": "Restore an archived task and its Codex thread.", "inputSchema": schema({"task": S, "codex_bin": S}, ["task"]), "readOnly": False},
    "task_cancel": {"description": "Request reversible cancellation of the active task turn.", "inputSchema": schema({"task": S}, ["task"]), "readOnly": False},
    "run_start": {"description": "Start discovery on a persistent Codex-Orchestra thread.", "inputSchema": schema({"task": S, "repository": S, "idempotency_key": S, "codex_bin": S, "model": S, "effort": S}, ["task"]), "readOnly": False},
    "run_respond": {"description": "Answer the current checkpoint on the same thread.", "inputSchema": schema({"task": S, "text": S, "response_to": S, "idempotency_key": S, "codex_bin": S, "model": S, "effort": S}, ["task", "text"]), "readOnly": False},
    "run_reopen": {"description": "Reopen a cancelled run on the same persistent thread.", "inputSchema": schema({"task": S, "idempotency_key": S, "codex_bin": S, "model": S, "effort": S}, ["task"]), "readOnly": False},
    "run_status": {"description": "Get the latest run status.", "inputSchema": schema({"task": S}, ["task"]), "readOnly": True},
    "run_reconcile": {"description": "Reconcile only the exact persisted active turn.", "inputSchema": schema({"task": S, "codex_bin": S}, ["task"]), "readOnly": False},
    "run_interactions": {"description": "List pending or resolved App Server interactions.", "inputSchema": schema({"task": S, "include_consumed": {"type": "boolean"}}, ["task"]), "readOnly": True},
    "run_resolve": {"description": "Persist one exact response for an App Server interaction.", "inputSchema": schema({"interaction": S, "response": {"type": "object"}}, ["interaction", "response"]), "readOnly": False},
}


def tool_definition(name: str, definition: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "description": definition["description"],
        "inputSchema": definition["inputSchema"],
        "annotations": {
            "readOnlyHint": definition["readOnly"],
            "destructiveHint": False,
            "idempotentHint": name not in {"run_start", "run_respond", "run_reopen"},
            "openWorldHint": name in {"run_start", "run_respond", "run_reopen", "run_reconcile"},
        },
    }


def cli_arguments(name: str, arguments: dict[str, Any]) -> list[str]:
    group, command = name.split("_", 1)
    command = {"create": "create", "get": "get", "list": "list", "note": "note", "archive": "archive", "restore": "restore", "cancel": "cancel", "start": "start", "respond": "respond", "reopen": "reopen", "status": "status", "reconcile": "reconcile", "interactions": "interactions", "resolve": "resolve"}[command]
    result = [group, command]
    for key, value in arguments.items():
        if value is None or value is False:
            continue
        flag = "--" + key.replace("_", "-")
        if value is True:
            result.append(flag)
        else:
            result.extend((flag, json.dumps(value, separators=(",", ":")) if key == "response" else str(value)))
    return result


def call_tool(name: str, arguments: Any) -> dict[str, Any]:
    if name not in TOOLS or not isinstance(arguments, dict):
        return {"content": [{"type": "text", "text": json.dumps({"status": "invalid", "reason": "unknown tool or invalid arguments"})}], "isError": True}
    helper = Path(__file__).resolve().parents[2] / "scripts" / "task_control.py"
    completed = subprocess.run(
        [sys.executable, str(helper), *cli_arguments(name, arguments)],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"status": "unavailable", "reason": completed.stderr.strip() or "task-control helper returned invalid JSON"}
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return {
        "content": [{"type": "text", "text": encoded}],
        "structuredContent": payload,
        "isError": completed.returncode != 0 or payload.get("status") != "ok",
    }


def response(request_id: Any, result: dict[str, Any] | None = None, error: dict[str, Any] | None = None) -> None:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    payload["error" if error is not None else "result"] = error if error is not None else result
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), flush=True)


def main() -> int:
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            response(None, error={"code": -32700, "message": "Parse error"})
            continue
        if not isinstance(message, dict) or message.get("jsonrpc") not in (None, "2.0"):
            response(message.get("id") if isinstance(message, dict) else None, error={"code": -32600, "message": "Invalid Request"})
            continue
        if "id" not in message:
            continue
        method = message.get("method")
        params = message.get("params") if isinstance(message.get("params"), dict) else {}
        if method == "initialize":
            requested = params.get("protocolVersion")
            protocol = requested if requested in PROTOCOLS else PROTOCOLS[-1]
            response(message["id"], {"protocolVersion": protocol, "capabilities": {"tools": {"listChanged": False}}, "serverInfo": {"name": "orchestra-task-control", "version": "0.2.0"}})
        elif method == "ping":
            response(message["id"], {})
        elif method == "tools/list":
            response(message["id"], {"tools": [tool_definition(name, definition) for name, definition in TOOLS.items()]})
        elif method == "tools/call":
            response(message["id"], call_tool(str(params.get("name", "")), params.get("arguments", {})))
        else:
            response(message["id"], error={"code": -32601, "message": "Method not found"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
