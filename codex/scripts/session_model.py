#!/usr/bin/env python3
"""Report the current Codex root model and Orchestra routing mode."""

from __future__ import annotations

from datetime import datetime, timezone
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
    ("gpt-6-astra", "v2"): "native",
    ("gpt-5.6-sol", "v2"): "native",
    ("orchestra-v1/gpt-5.6-sol", "v1"): "external",
}
# Native efforts follow the host catalog; the external compatibility entry
# retains its existing contract.
ROOT_EFFORTS = {
    "gpt-6-astra": {
        "low",
        "medium",
        "high",
        "xhigh",
        "max",
        "ultra",
    },
    "gpt-5.6-sol": {"low", "medium", "high", "xhigh", "max", "ultra"},
    "orchestra-v1/gpt-5.6-sol": {"medium", "high"},
}


def _parse_timestamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(timezone.utc) if parsed.tzinfo else None


def _observe_rollout(target: Path, thread_id: str | None) -> dict[str, Any] | None:
    """Select complete JSON events; never substitute old routing for invalid new evidence."""
    contexts = []
    identity_seen = False
    try:
        with target.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream):
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    # A writer may not have finished the last JSON line yet.
                    continue
                if not isinstance(entry, dict):
                    continue
                payload = entry.get("payload")
                if entry.get("type") == "session_meta" and thread_id is not None:
                    if not isinstance(payload, dict):
                        return None
                    identities = [source[key] for source in (entry, payload)
                                  for key in ("id", "session_id", "thread_id") if key in source]
                    if not identities or any(value != thread_id for value in identities):
                        return None
                    identity_seen = True
                if entry.get("type") != "turn_context":
                    continue
                payload = payload if isinstance(payload, dict) else {}
                timestamp = _parse_timestamp(entry.get("timestamp") or payload.get("timestamp"))
                contexts.append((timestamp, line_number, payload))
    except (OSError, UnicodeError):
        return None
    if not contexts or (thread_id is not None and not identity_seen):
        return None
    dated = [item for item in contexts if item[0] is not None]
    if dated:
        if len(dated) != len(contexts):
            # Missing timestamps cannot safely be ordered against dated contexts.
            return {"path": target, "timestamp": None, "payload": {}}
        newest = max(item[0] for item in dated)
        matches = [item for item in dated if item[0] == newest]
        if len(matches) != 1:
            return {"path": target, "timestamp": newest, "payload": {}}
        chosen = matches[0]
    else:
        chosen = contexts[-1]  # Older single-file rollouts use physical event order.
    return {"path": target, "timestamp": chosen[0], "payload": chosen[2]}


def _rollout_candidates(codex_home: Path, thread_id: str) -> list[Path]:
    sessions = codex_home / "sessions"
    if not sessions.is_dir():
        return []

    original_suffix = f"-{thread_id}.jsonl"
    continuation_prefix = f"{thread_id}_"
    candidates: list[Path] = []
    for target in sessions.glob("*/*/*/*.jsonl"):
        name = target.name
        is_original = name.endswith(original_suffix)
        is_continuation = (
            name.startswith(continuation_prefix)
            and name.endswith(".jsonl")
            and len(name) > len(continuation_prefix) + len(".jsonl")
        )
        if not (is_original or is_continuation):
            continue
        if target.is_symlink() or not target.is_file():
            continue
        candidates.append(target)
    return sorted(set(candidates))


def find_rollout(codex_home: Path, thread_id: str) -> Path | None:
    observations = [
        observation
        for target in _rollout_candidates(codex_home, thread_id)
        if (observation := _observe_rollout(target, thread_id)) is not None
    ]
    if not observations:
        return None
    if len(observations) == 1:
        return observations[0]["path"]

    # A continuation may have an older filesystem mtime than its parent.  Only
    # event timestamps can order multiple validated rollouts.  Missing or tied
    # timestamps are intentionally ambiguous and block routing.
    if any(observation["timestamp"] is None for observation in observations):
        return None
    newest_timestamp = max(
        observation["timestamp"]
        for observation in observations
        if observation["timestamp"] is not None
    )
    newest = [
        observation
        for observation in observations
        if observation["timestamp"] == newest_timestamp
    ]
    if len(newest) != 1:
        return None
    return newest[0]["path"]


def read_latest_turn_context(
    target: Path,
    thread_id: str | None = None,
) -> dict[str, Any] | None:
    observation = _observe_rollout(target, thread_id)
    if observation is None:
        return None
    return observation["payload"]


def inspect_session(
    codex_home: Path,
    thread_id: str | None,
) -> dict[str, Any]:
    if not thread_id or not THREAD_ID_PATTERN.fullmatch(thread_id):
        return blocked("CODEX_THREAD_ID is missing or invalid")
    rollout = find_rollout(codex_home, thread_id)
    if rollout is None:
        return blocked("current Codex rollout could not be resolved")
    context = read_latest_turn_context(rollout, thread_id)
    if context is None:
        return blocked("current Codex turn context is unavailable")

    if not all(isinstance(context.get(k), str) and context[k].strip()
               for k in ("model", "multi_agent_version", "effort")):
        return blocked("latest Codex routing context is incomplete")
    model = context["model"]
    multi_agent_version = context["multi_agent_version"]
    reasoning_effort = context["effort"]
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
    supported_efforts = ROOT_EFFORTS.get(model, set())
    if reasoning_effort not in supported_efforts:
        return blocked(
            "Orchestra root reasoning effort is unsupported by the selected root model",
            model=model,
            multi_agent_version=multi_agent_version,
            reasoning_effort=reasoning_effort,
            supported_efforts=sorted(supported_efforts),
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
