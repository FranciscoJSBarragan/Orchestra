#!/usr/bin/env python3
"""Initialize, resolve, or clean one worktree-local Orchestra task state."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import (
    blocked,
    cleanup_private_task_state,
    initialize_private_task_state,
    resolve_private_task_state,
)


def resolve(worktree: Path) -> dict[str, Any]:
    state, error = resolve_private_task_state(worktree)
    if error:
        return blocked(error)
    assert state is not None
    return {"status": "ok", **state}


def cleanup(worktree: Path) -> dict[str, Any]:
    state, error = resolve_private_task_state(worktree)
    if error:
        return blocked(error)
    assert state is not None
    cleanup_error = cleanup_private_task_state(worktree)
    if cleanup_error:
        return blocked(cleanup_error, layout=state["layout"])
    return {
        "status": "ok",
        "layout": state["layout"],
        "cleanup": ["private_state"] if state["exists"] else [],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    for action in ("init", "resolve", "cleanup"):
        command = subparsers.add_parser(action)
        command.add_argument("--worktree", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.action == "init":
        result = initialize_private_task_state(args.worktree)
    elif args.action == "resolve":
        result = resolve(args.worktree)
    else:
        result = cleanup(args.worktree)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
