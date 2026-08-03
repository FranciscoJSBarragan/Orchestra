#!/usr/bin/env python3
"""Report the current Codex root model and Orchestra routing mode."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

from _common import blocked


THREAD_ID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\Z"
)
ROOT_MODELS = {
    ("gpt-5.6-sol", "v2"): "native",
    ("orchestra-v1/gpt-5.6-sol", "v1"): "external",
}
ROOT_EFFORTS = {"medium", "high"}


def find_rollout(codex_home: Path, thread_id: str) -> Path | None:
    matches = sorted(
        (codex_home / "sessions").glob(f"*/*/*/*-{thread_id}.jsonl"),
    )
    if len(matches) != 1:
        return None
    target = matches[0]
    if target.is_symlink() or not target.is_file():
        return None
    return target


def read_latest_turn_context(target: Path) -> dict[str, Any] | None:
    latest: dict[str, Any] | None = None
    try:
        with target.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") != "turn_context":
                    continue
                payload = entry.get("payload")
                if isinstance(payload, dict):
                    latest = payload
    except (OSError, UnicodeError):
        return None
    return latest


def inspect_session(
    codex_home: Path,
    thread_id: str | None,
) -> dict[str, Any]:
    if not thread_id or not THREAD_ID_PATTERN.fullmatch(thread_id):
        return blocked("CODEX_THREAD_ID is missing or invalid")
    rollout = find_rollout(codex_home, thread_id)
    if rollout is None:
        return blocked("current Codex rollout could not be resolved")
    context = read_latest_turn_context(rollout)
    if context is None:
        return blocked("current Codex turn context is unavailable")

    model = str(context.get("model") or "")
    multi_agent_version = str(context.get("multi_agent_version") or "")
    reasoning_effort = str(context.get("effort") or "")
    modelconfig = ROOT_MODELS.get((model, multi_agent_version))
    if modelconfig is None:
        return blocked(
            "root model and multi-agent version are incompatible with Orchestra dual mode",
            model=model,
            multi_agent_version=multi_agent_version,
            expected_models=sorted(
                f"{expected_model}:{version}"
                for expected_model, version in ROOT_MODELS
            ),
        )
    if reasoning_effort not in ROOT_EFFORTS:
        return blocked(
            "Orchestra root reasoning effort must be medium or high",
            model=model,
            multi_agent_version=multi_agent_version,
            reasoning_effort=reasoning_effort,
        )
    return {
        "status": "ok",
        "model": model,
        "multi_agent_version": multi_agent_version,
        "reasoning_effort": reasoning_effort,
        "modelconfig": modelconfig,
    }


def main() -> int:
    codex_home = Path(
        os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))
    ).expanduser()
    result = inspect_session(codex_home, os.environ.get("CODEX_THREAD_ID"))
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
