"""JSON command-line interface for local task intake and Orchestra discovery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any
import uuid

from .app_server import (
    AppServerError,
    TurnInterrupted,
    completed_result_from_thread,
    execute_turn,
    read_thread,
    set_thread_archived,
)
from .service import ControlError, ControlService


DEFAULT_MODEL = "gpt-5.6-sol"
DEFAULT_EFFORT = "medium"


class JsonParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print(json.dumps({"status": "invalid", "reason": message}, sort_keys=True))
        raise SystemExit(2)


def emit(status: str, **values: Any) -> int:
    print(json.dumps({"status": status, **values}, ensure_ascii=False, sort_keys=True))
    return 0 if status == "ok" else 1


def repository_identity(value: str) -> tuple[Path, str]:
    root = Path(value).expanduser().resolve()
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel", "HEAD^{commit}"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = result.stdout.splitlines()
    if result.returncode or len(lines) != 2 or Path(lines[0]).resolve() != root:
        raise ControlError("invalid", f"not a canonical Git worktree root: {root}")
    return root, lines[1]


def initial_prompt(task: dict[str, Any], task_id: str) -> str:
    return f"""$orchestra

Adopt durable task {task_id}: {task['title']}

Objective brief: {task['brief']}

This is a discovery-first Control Plane run. Reuse the normal Orchestra contract. First recommend the initial tier and stop for the user's explicit choice. After the tier is supplied, run mandatory repository_context, synthesize a candidate specification, and stop again. Do not draft the formal plan until the user confirms that specification. Do not implement without exact plan approval. Delivery is hold.

Return only the JSON object required by the turn output schema. Put the user-facing checkpoint or outcome in message. Use a stable checkpoint_id for questions. List exact artifact identifiers and retained resources when known.
"""


def response_prompt(task_id: str, response_to: str | None, text: str) -> str:
    reference = response_to or "the current open checkpoint"
    return f"""Continue durable task {task_id} on this exact thread. The user response to {reference} is:

{text}

Follow the existing Orchestra discovery/approval contract. Return only the JSON object required by the output schema, including the next checkpoint or final outcome. Do not infer implementation, commit, or delivery authority beyond the user's exact response.
"""


def reopen_prompt(task_id: str) -> str:
    return f"""Continue durable task {task_id} on this exact thread after its reversible interruption.

Resume from the durable conversation and current Orchestra checkpoint. Do not replay a prior command or infer new authority. If an exact resolved interaction is presented again, use only its persisted one-use response. Return only the JSON object required by the output schema.
"""


def drive_turn(
    service: ControlService,
    *,
    run: dict[str, Any],
    turn: dict[str, Any],
    prompt: str,
    codex_bin: str,
    model: str,
    effort: str,
) -> dict[str, Any]:
    run_id = run["id"]
    turn_id = turn["id"]

    def on_thread(value: str) -> None:
        service.update_transport(run_id=run_id, turn_record_id=turn_id, thread_uuid=value)

    def on_turn(value: str) -> None:
        service.update_transport(run_id=run_id, turn_record_id=turn_id, active_turn_id=value)

    def on_interaction(method: str, params: dict[str, Any]) -> dict[str, Any] | None:
        thread_uuid = str(params.get("threadId") or service.get_run(run_id).get("thread_uuid") or "")
        turn_uuid = str(params.get("turnId") or service.get_run(run_id).get("active_turn_id") or "")
        item_id = params.get("itemId")
        canonical = json.dumps(
            {"method": method, "params": params},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        _, response = service.record_interaction(
            run_id=run_id,
            turn_record_id=turn_id,
            thread_uuid=thread_uuid,
            turn_uuid=turn_uuid,
            item_id=str(item_id) if item_id is not None else None,
            method=method,
            params=params,
            fingerprint=fingerprint,
        )
        return response

    try:
        thread_uuid, active_turn, result = execute_turn(
            codex_bin=codex_bin,
            repository=Path(run["repository"]),
            prompt=prompt,
            thread_uuid=run.get("thread_uuid"),
            model=model,
            effort=effort,
            message_id=turn_id,
            on_thread=on_thread,
            on_turn=on_turn,
            should_cancel=lambda: service.cancellation_requested(run_id),
            on_interaction=on_interaction,
        )
    except TurnInterrupted as error:
        if error.reason == "needs_user":
            return service.mark_needs_user(run_id, turn_id)
        return service.mark_cancelled(run_id, turn_id)
    except AppServerError as error:
        if error.ambiguous:
            return service.update_transport(
                run_id=run_id, turn_record_id=turn_id, ambiguous=error.reason
            )
        blocked = {
            "kind": "blocked",
            "checkpoint_id": None,
            "message": error.reason,
            "recommended_tier": None,
            "artifacts": [],
            "retained_resources": [],
        }
        return service.update_transport(
            run_id=run_id, turn_record_id=turn_id, completed_result=blocked
        )
    return service.update_transport(
        run_id=run_id,
        turn_record_id=turn_id,
        thread_uuid=thread_uuid,
        active_turn_id=active_turn,
        completed_result=result,
    )


def build_parser() -> JsonParser:
    parser = JsonParser(prog="orchestra-task-control")
    parser.add_argument("--state-root", type=Path)
    groups = parser.add_subparsers(dest="group", required=True)
    task = groups.add_parser("task")
    task_commands = task.add_subparsers(dest="command", required=True)
    create = task_commands.add_parser("create")
    create.add_argument("--title", required=True)
    create.add_argument("--brief", required=True)
    create.add_argument("--source-harness", default="local")
    create.add_argument("--source-conversation", default="")
    create.add_argument("--source-message", default="")
    create.add_argument("--repository")
    create.add_argument("--idempotency-key", default=None)
    for name in ("get", "archive", "restore", "cancel"):
        command = task_commands.add_parser(name)
        command.add_argument("--task", required=True)
        if name in ("archive", "restore"):
            command.add_argument("--codex-bin", default="codex")
    listing = task_commands.add_parser("list")
    listing.add_argument("--include-archived", action="store_true")
    note = task_commands.add_parser("note")
    note.add_argument("--task", required=True)
    note.add_argument("--body", required=True)
    note.add_argument("--source-harness", default="local")
    note.add_argument("--source-reference", default="")
    note.add_argument("--idempotency-key", default=None)

    run = groups.add_parser("run")
    run_commands = run.add_subparsers(dest="command", required=True)
    start = run_commands.add_parser("start")
    start.add_argument("--task", required=True)
    start.add_argument("--repository")
    start.add_argument("--idempotency-key", default=None)
    start.add_argument("--codex-bin", default="codex")
    start.add_argument("--model", default=DEFAULT_MODEL)
    start.add_argument("--effort", default=DEFAULT_EFFORT)
    respond = run_commands.add_parser("respond")
    respond.add_argument("--task", required=True)
    respond.add_argument("--text", required=True)
    respond.add_argument("--response-to")
    respond.add_argument("--idempotency-key", default=None)
    respond.add_argument("--codex-bin", default="codex")
    respond.add_argument("--model", default=DEFAULT_MODEL)
    respond.add_argument("--effort", default=DEFAULT_EFFORT)
    status = run_commands.add_parser("status")
    status.add_argument("--task", required=True)
    reconcile = run_commands.add_parser("reconcile")
    reconcile.add_argument("--task", required=True)
    reconcile.add_argument("--codex-bin", default="codex")
    reopen = run_commands.add_parser("reopen")
    reopen.add_argument("--task", required=True)
    reopen.add_argument("--idempotency-key", default=None)
    reopen.add_argument("--codex-bin", default="codex")
    reopen.add_argument("--model", default=DEFAULT_MODEL)
    reopen.add_argument("--effort", default=DEFAULT_EFFORT)
    interactions = run_commands.add_parser("interactions")
    interactions.add_argument("--task", required=True)
    interactions.add_argument("--include-consumed", action="store_true")
    resolve = run_commands.add_parser("resolve")
    resolve.add_argument("--interaction", required=True)
    resolve.add_argument("--response", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = ControlService(args.state_root)
    try:
        if args.group == "task" and args.command == "create":
            key = args.idempotency_key or str(uuid.uuid4())
            task = service.create_task(
                title=args.title,
                brief=args.brief,
                source_harness=args.source_harness,
                source_conversation=args.source_conversation,
                source_message=args.source_message,
                repository=args.repository,
                idempotency_key=key,
            )
            return emit("ok", task=task)
        if args.group == "task" and args.command == "get":
            return emit("ok", task=service.get_task(args.task))
        if args.group == "task" and args.command == "list":
            return emit("ok", tasks=service.list_tasks(args.include_archived))
        if args.group == "task" and args.command == "note":
            note = service.add_note(
                task_id=args.task,
                body=args.body,
                source_harness=args.source_harness,
                source_reference=args.source_reference,
                idempotency_key=args.idempotency_key or str(uuid.uuid4()),
            )
            return emit("ok", note=note)
        if args.group == "task" and args.command == "cancel":
            return emit("ok", run=service.request_cancel(args.task))
        if args.group == "task" and args.command in ("archive", "restore"):
            archived = args.command == "archive"
            task = service.get_task(args.task)
            runs = task.get("runs", [])
            latest = runs[-1] if runs else None
            if archived and latest and latest.get("active_turn_id"):
                return emit("busy", reason="task has an unresolved active turn")
            if latest and latest.get("thread_uuid"):
                try:
                    set_thread_archived(
                        codex_bin=args.codex_bin,
                        thread_uuid=latest["thread_uuid"],
                        archived=archived,
                    )
                except AppServerError as error:
                    return emit("blocked", reason=error.reason)
            return emit("ok", task=service.set_archived(args.task, archived))
        if args.group == "run" and args.command == "status":
            return emit("ok", run=service.latest_run(args.task))
        if args.group == "run" and args.command == "interactions":
            return emit(
                "ok",
                interactions=service.list_interactions(args.task, args.include_consumed),
            )
        if args.group == "run" and args.command == "resolve":
            try:
                response = json.loads(args.response)
            except json.JSONDecodeError as error:
                raise ControlError("invalid", f"invalid interaction response JSON: {error}") from error
            return emit("ok", interaction=service.resolve_interaction(args.interaction, response))
        if args.group == "run" and args.command == "start":
            task = service.get_task(args.task)
            repository_value = args.repository or task.get("repository")
            if not repository_value:
                return emit("needs_repository", task_id=args.task)
            repository, revision = repository_identity(repository_value)
            run = service.prepare_run(args.task, str(repository), revision)
            turn = service.prepare_turn(
                run_id=run["id"],
                text=initial_prompt(task, args.task),
                idempotency_key=args.idempotency_key or f"start:{args.task}",
            )
            if turn["status"] == "completed":
                return emit("ok", run=service.get_run(run["id"]))
            if turn["status"] != "prepared":
                return emit(turn["status"], reason="start turn is not safe to replay", run=run)
            result = drive_turn(
                service,
                run=run,
                turn=turn,
                prompt=turn["input_text"],
                codex_bin=args.codex_bin,
                model=args.model,
                effort=args.effort,
            )
            return emit("ok", run=result)
        if args.group == "run" and args.command == "respond":
            run = service.latest_run(args.task)
            turn = service.prepare_turn(
                run_id=run["id"],
                text=args.text,
                idempotency_key=args.idempotency_key or str(uuid.uuid4()),
                response_to=args.response_to,
            )
            if turn["status"] == "completed":
                return emit("ok", run=service.get_run(run["id"]))
            if turn["status"] != "prepared":
                return emit(turn["status"], reason="turn is not safe to replay", run=run)
            result = drive_turn(
                service,
                run=run,
                turn=turn,
                prompt=response_prompt(args.task, args.response_to, args.text),
                codex_bin=args.codex_bin,
                model=args.model,
                effort=args.effort,
            )
            return emit("ok", run=result)
        if args.group == "run" and args.command == "reopen":
            run = service.reopen(args.task)
            turn = service.prepare_turn(
                run_id=run["id"],
                text=reopen_prompt(args.task),
                idempotency_key=args.idempotency_key or str(uuid.uuid4()),
            )
            result = drive_turn(
                service,
                run=run,
                turn=turn,
                prompt=turn["input_text"],
                codex_bin=args.codex_bin,
                model=args.model,
                effort=args.effort,
            )
            return emit("ok", run=result)
        if args.group == "run" and args.command == "reconcile":
            run = service.latest_run(args.task)
            if not run.get("thread_uuid"):
                return emit("needs_reconciliation", reason="run has no persisted thread UUID", run=run)
            active_turn_id = run.get("active_turn_id")
            if not active_turn_id:
                return emit(
                    "needs_reconciliation",
                    reason="run has no exact active turn to reconcile",
                    run=run,
                )
            run_detail = service.get_run(run["id"])
            local_turns = [
                turn for turn in run_detail["turns"] if turn.get("turn_uuid") == active_turn_id
            ]
            if len(local_turns) != 1:
                return emit(
                    "needs_reconciliation",
                    reason="active turn does not map to one local turn record",
                    run=run,
                )
            try:
                observed = read_thread(codex_bin=args.codex_bin, thread_uuid=run["thread_uuid"])
                result = completed_result_from_thread(
                    observed,
                    thread_uuid=run["thread_uuid"],
                    turn_uuid=active_turn_id,
                )
            except AppServerError as error:
                reconciled = service.update_transport(
                    run_id=run["id"],
                    turn_record_id=local_turns[0]["id"],
                    ambiguous=error.reason,
                )
                return emit("needs_reconciliation", reason=error.reason, run=reconciled)
            if result is None:
                return emit(
                    "needs_reconciliation",
                    reason="persisted active turn is not completed with a valid result",
                    run=run,
                )
            reconciled = service.update_transport(
                run_id=run["id"],
                turn_record_id=local_turns[0]["id"],
                active_turn_id=active_turn_id,
                completed_result=result,
            )
            return emit("ok", run=reconciled)
        raise ControlError("invalid", "unsupported command")
    except ControlError as error:
        return emit(error.status, reason=error.reason)
    except (OSError, subprocess.SubprocessError) as error:
        return emit("unavailable", reason=str(error))


if __name__ == "__main__":
    raise SystemExit(main())
