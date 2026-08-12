"""JSON command-line interface for the local prepared-task Kanban."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
from typing import Any
import uuid

from .service import ControlError, ControlService


class JsonParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        print(json.dumps({"status": "invalid", "reason": message}, sort_keys=True))
        raise SystemExit(2)


def emit(status: str, **values: Any) -> int:
    print(json.dumps({"status": status, **values}, ensure_ascii=False, sort_keys=True))
    return 0 if status == "ok" else 1


def repository_identity(value: str) -> tuple[Path, str, Path]:
    root = Path(value).expanduser().resolve()
    try:
        identity = subprocess.run(
            ["git", "rev-parse", "--show-toplevel", "HEAD^{commit}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        common_dir_result = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as error:
        raise ControlError("unavailable", f"cannot inspect Git repository: {error}") from error
    lines = identity.stdout.splitlines()
    if (
        identity.returncode
        or common_dir_result.returncode
        or len(lines) != 2
        or Path(lines[0]).resolve() != root
    ):
        raise ControlError("invalid", f"not a canonical Git worktree root: {root}")
    common_dir = Path(common_dir_result.stdout.strip()).resolve()
    return root, lines[1], common_dir


def ancestor_checker(repository: Path, head_revision: str):
    def contains(revision: str) -> bool:
        try:
            result = subprocess.run(
                ["git", "merge-base", "--is-ancestor", revision, head_revision],
                cwd=repository,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as error:
            raise ControlError("unavailable", f"cannot verify delivered revision: {error}") from error
        if result.returncode == 0:
            return True
        if result.returncode == 1:
            return False
        # A delivery object that is not present in this checkout is the normal
        # stale-checkout case. Adoption reports the dependency as blocked and
        # asks for an explicit checkout update instead of pulling implicitly.
        return False

    return contains


def _read_document(path: Path, label: str) -> str:
    try:
        resolved = path.expanduser().resolve(strict=True)
        if not resolved.is_file():
            raise OSError("not a regular file")
        return resolved.read_text(encoding="utf-8")
    except OSError as error:
        raise ControlError("invalid", f"cannot read {label}: {error}") from error


def build_parser() -> JsonParser:
    parser = JsonParser(prog="orchestra-task-control")
    parser.add_argument("--state-root", type=Path)
    groups = parser.add_subparsers(dest="group", required=True)
    task = groups.add_parser("task")
    commands = task.add_subparsers(dest="command", required=True)

    create = commands.add_parser("create")
    create.add_argument("--title", required=True)
    create.add_argument("--brief", required=True)
    create.add_argument("--source-harness", default="local")
    create.add_argument("--source-conversation", default="")
    create.add_argument("--source-message", default="")
    create.add_argument("--repository")
    create.add_argument("--idempotency-key", default=None)

    for name in ("get", "archive", "restore"):
        command = commands.add_parser(name)
        command.add_argument("--task", required=True)

    decompose = commands.add_parser("decompose")
    decompose.add_argument("--task", required=True)
    manifest = decompose.add_mutually_exclusive_group(required=True)
    manifest.add_argument("--manifest-file", type=Path)
    manifest.add_argument("--manifest-json", help=argparse.SUPPRESS)
    decompose.add_argument("--confirmed", action="store_true")
    decompose.add_argument("--idempotency-key", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("--include-archived", action="store_true")

    note = commands.add_parser("note")
    note.add_argument("--task", required=True)
    note.add_argument("--body", required=True)
    note.add_argument("--source-harness", default="local")
    note.add_argument("--source-reference", default="")
    note.add_argument("--idempotency-key", default=None)

    prepare = commands.add_parser("prepare")
    prepare.add_argument("--task", required=True)
    prepare.add_argument("--repository", required=True)
    prepare.add_argument("--prepared-revision")
    context = prepare.add_mutually_exclusive_group(required=True)
    context.add_argument("--repository-context")
    context.add_argument("--repository-context-file", type=Path)
    specification = prepare.add_mutually_exclusive_group(required=True)
    specification.add_argument("--specification")
    specification.add_argument("--specification-file", type=Path)
    prepare.add_argument("--confirmed", action="store_true")

    adopt = commands.add_parser("adopt")
    adopt.add_argument("--task", required=True)
    adopt.add_argument("--repository", required=True)

    transfer = commands.add_parser("transfer")
    transfer.add_argument("--task", required=True)
    transfer.add_argument("--stable-checkpoint", action="store_true")

    finish = commands.add_parser("finish")
    finish.add_argument("--task", required=True)
    finish.add_argument("--repository", required=True)
    finish.add_argument("--task-revision", required=True)

    delivery = commands.add_parser("record-delivery")
    delivery.add_argument("--task", required=True)
    delivery.add_argument("--repository", required=True)
    delivery.add_argument("--task-revision", required=True)
    delivery.add_argument("--delivery-revision", required=True)
    delivery.add_argument(
        "--kind", required=True, choices=("local-integration", "pr-merge")
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    service = ControlService(args.state_root)
    try:
        if args.group != "task":
            raise ControlError("invalid", "unsupported command group")
        if args.command == "create":
            task = service.create_task(
                title=args.title,
                brief=args.brief,
                source_harness=args.source_harness,
                source_conversation=args.source_conversation,
                source_message=args.source_message,
                repository=args.repository,
                idempotency_key=args.idempotency_key or str(uuid.uuid4()),
            )
            return emit("ok", task=task)
        if args.command == "get":
            return emit("ok", task=service.get_task(args.task))
        if args.command == "decompose":
            if args.manifest_json is not None and os.environ.get("ORCHESTRA_MCP_INTERNAL") != "1":
                raise ControlError("invalid", "inline decomposition manifest is reserved for MCP")
            raw_manifest = (
                args.manifest_json
                if args.manifest_json is not None
                else _read_document(args.manifest_file, "decomposition manifest")
            )
            try:
                manifest = json.loads(raw_manifest)
            except json.JSONDecodeError as error:
                raise ControlError("invalid", f"invalid decomposition manifest JSON: {error}") from error
            cards = manifest.get("cards") if isinstance(manifest, dict) else None
            if not isinstance(cards, list):
                raise ControlError("invalid", "decomposition manifest cards must be an array")
            for card in cards:
                if not isinstance(card, dict) or not isinstance(card.get("repository"), str):
                    raise ControlError("invalid", "each decomposition card requires a repository")
                repository, _, _ = repository_identity(card["repository"])
                card["repository"] = str(repository)
            result = service.decompose_task(
                task_ref=args.task,
                manifest=manifest,
                confirmed=args.confirmed,
                idempotency_key=args.idempotency_key,
            )
            return emit("ok", **result)
        if args.command == "list":
            return emit("ok", tasks=service.list_tasks(args.include_archived))
        if args.command == "note":
            note = service.add_note(
                task_id=args.task,
                body=args.body,
                source_harness=args.source_harness,
                source_reference=args.source_reference,
                idempotency_key=args.idempotency_key or str(uuid.uuid4()),
            )
            return emit("ok", note=note)
        if args.command == "prepare":
            repository, observed_revision, common_dir = repository_identity(args.repository)
            requested_revision = args.prepared_revision or observed_revision
            if requested_revision != observed_revision:
                raise ControlError(
                    "invalid",
                    "prepared revision must match the repository's current HEAD",
                )
            context = (
                args.repository_context
                if args.repository_context is not None
                else _read_document(args.repository_context_file, "repository context")
            )
            specification = (
                args.specification
                if args.specification is not None
                else _read_document(args.specification_file, "specification")
            )
            prepared = service.prepare_task(
                task_ref=args.task,
                repository=str(repository),
                prepared_revision=observed_revision,
                repository_common_dir=str(common_dir),
                repository_context=context,
                specification=specification,
                confirmed=args.confirmed,
            )
            return emit("ok", task=prepared)
        if args.command == "adopt":
            repository, revision, common_dir = repository_identity(args.repository)
            adopted = service.adopt_task(
                task_ref=args.task,
                thread_id=os.environ.get("CODEX_THREAD_ID"),
                repository=str(repository),
                current_revision=revision,
                repository_common_dir=str(common_dir),
                ancestor_contains=ancestor_checker(repository, revision),
            )
            next_action = (
                "resume the existing Orchestra checkout and plan"
                if adopted["resume_existing_checkout"]
                else "activate Orchestra and create the task checkout using installed policy"
            )
            return emit("ok", task=adopted, next_action=next_action)
        if args.command == "transfer":
            transferred = service.transfer_task(
                task_ref=args.task,
                thread_id=os.environ.get("CODEX_THREAD_ID"),
                stable_checkpoint=args.stable_checkpoint,
            )
            return emit(
                "ok",
                task=transferred,
                next_action=f"open another native Codex chat and ask it to adopt {transferred['short_id']}",
            )
        if args.command == "finish":
            repository, revision, common_dir = repository_identity(args.repository)
            requested_revision = args.task_revision
            if requested_revision != revision:
                raise ControlError("invalid", "task revision must match the repository's current HEAD")
            completed = service.finish_task(
                task_ref=args.task,
                thread_id=os.environ.get("CODEX_THREAD_ID"),
                repository=str(repository),
                terminal_revision=revision,
                repository_common_dir=str(common_dir),
            )
            return emit("ok", task=completed)
        if args.command == "record-delivery":
            repository, _, common_dir = repository_identity(args.repository)
            completed = service.record_delivery(
                task_ref=args.task,
                thread_id=os.environ.get("CODEX_THREAD_ID"),
                repository=str(repository),
                task_revision=args.task_revision,
                delivery_revision=args.delivery_revision,
                kind=args.kind,
                repository_common_dir=str(common_dir),
            )
            return emit("ok", task=completed)
        if args.command in ("archive", "restore"):
            return emit(
                "ok",
                task=service.set_archived(args.task, args.command == "archive"),
            )
        raise ControlError("invalid", "unsupported command")
    except ControlError as error:
        return emit(error.status, reason=error.reason)
    except (OSError, subprocess.SubprocessError) as error:
        return emit("unavailable", reason=str(error))


if __name__ == "__main__":
    raise SystemExit(main())
