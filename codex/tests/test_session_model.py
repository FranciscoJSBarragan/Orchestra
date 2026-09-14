"""Tests for deterministic Orchestra root-model detection."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "codex/scripts/session_model.py"
SPEC = importlib.util.spec_from_file_location("session_model", HELPER)
assert SPEC is not None and SPEC.loader is not None
session_model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(session_model)


class SessionModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.codex_home = Path(self.temporary.name)
        self.thread_id = "019fb9da-17ff-71a1-9ed2-8679dbc5dc2a"
        self.other_thread_id = "019fb9da-17ff-71a1-9ed2-8679dbc5dc2b"
        self.rollout = (
            self.codex_home
            / "sessions/2026/07/31"
            / f"rollout-2026-07-31T14-25-05-{self.thread_id}.jsonl"
        )
        self.rollout.parent.mkdir(parents=True)

    def write_context(
        self,
        model: str,
        version: str,
        effort: str = "high",
        *,
        path: Path | None = None,
        identity: str | None = None,
        timestamp: str | None = None,
        malformed_tail: str | None = None,
        **extra: object,
    ) -> Path:
        target = path or self.rollout
        target.parent.mkdir(parents=True, exist_ok=True)
        first_write = not target.exists() or target.stat().st_size == 0
        with target.open("a", encoding="utf-8") as stream:
            if first_write:
                session_id = identity or self.thread_id
                stream.write(
                    json.dumps(
                        {
                            "type": "session_meta",
                            "timestamp": "2026-07-31T14:24:59Z",
                            "payload": {
                                "id": session_id,
                                "session_id": session_id,
                            },
                        }
                    )
                    + "\n"
                )
            entry: dict[str, object] = {
                "type": "turn_context",
                "payload": {
                    "model": model,
                    "multi_agent_version": version,
                    "effort": effort,
                    **extra,
                },
            }
            if timestamp is not None:
                entry["timestamp"] = timestamp
            stream.write(json.dumps(entry) + "\n")
            if malformed_tail is not None:
                stream.write(malformed_tail)
        return target

    def inspect(self) -> dict:
        return session_model.inspect_session(self.codex_home, self.thread_id)

    def test_native_sol_v2_selects_native_mode(self) -> None:
        self.write_context("gpt-5.6-sol", "v2", "medium")
        self.assertEqual(
            self.inspect(),
            {
                "status": "ok",
                "model": "gpt-5.6-sol",
                "multi_agent_version": "v2",
                "reasoning_effort": "medium",
                "modelconfig": "native",
            },
        )

    def test_native_astra_v2_accepts_catalog_efforts(self) -> None:
        for effort in ("low", "medium", "high", "xhigh", "max", "ultra"):
            with self.subTest(effort=effort):
                self.rollout.write_text("", encoding="utf-8")
                self.write_context("gpt-6-astra", "v2", effort)
                result = self.inspect()
                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["modelconfig"], "native")
                self.assertEqual(result["reasoning_effort"], effort)

    def test_orchestra_sol_alias_v1_selects_external_mode(self) -> None:
        self.write_context("orchestra-v1/gpt-5.6-sol", "v1")
        self.assertEqual(self.inspect()["modelconfig"], "external")

    def test_latest_turn_context_uses_observed_timestamp(self) -> None:
        self.write_context(
            "gpt-5.6-terra",
            "v2",
            timestamp="2026-07-31T14:25:00Z",
        )
        self.write_context(
            "gpt-5.6-sol",
            "v2",
            timestamp="2026-07-31T14:25:01Z",
        )
        self.assertEqual(self.inspect()["modelconfig"], "native")

    def test_continuation_timestamp_wins_over_filesystem_mtime(self) -> None:
        continuation = self.rollout.parent / f"{self.thread_id}_continued.jsonl"
        self.write_context(
            "gpt-5.6-sol",
            "v2",
            "high",
            timestamp="2026-07-31T14:25:00Z",
        )
        self.write_context(
            "gpt-6-astra",
            "v2",
            "low",
            path=continuation,
            timestamp="2026-07-31T14:25:10Z",
        )
        os.utime(self.rollout, (2_000, 2_000))
        os.utime(continuation, (1_000, 1_000))
        result = self.inspect()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["model"], "gpt-6-astra")

    def test_wrong_identity_continuation_is_ignored(self) -> None:
        continuation = self.rollout.parent / f"{self.thread_id}_wrong.jsonl"
        self.write_context(
            "gpt-5.6-sol",
            "v2",
            timestamp="2026-07-31T14:25:00Z",
        )
        self.write_context(
            "gpt-6-astra",
            "v2",
            "low",
            path=continuation,
            identity=self.other_thread_id,
            timestamp="2026-07-31T14:25:10Z",
        )
        result = self.inspect()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["model"], "gpt-5.6-sol")

    def test_changed_protocol_in_latest_context_blocks(self) -> None:
        self.write_context(
            "gpt-5.6-sol",
            "v2",
            timestamp="2026-07-31T14:25:00Z",
        )
        self.write_context(
            "orchestra-v1/gpt-5.6-sol",
            "v2",
            timestamp="2026-07-31T14:25:01Z",
        )
        result = self.inspect()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("incompatible", result["reason"])

    def test_malformed_tail_keeps_last_complete_context(self) -> None:
        self.write_context(
            "gpt-6-astra",
            "v2",
            "low",
            timestamp="2026-07-31T14:25:00Z",
            malformed_tail='{"type":"turn_context","payload":',
        )
        result = self.inspect()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["model"], "gpt-6-astra")

    def test_wrong_identity_without_valid_rollout_blocks(self) -> None:
        self.write_context(
            "gpt-6-astra",
            "v2",
            "low",
            identity=self.other_thread_id,
        )
        result = self.inspect()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("rollout", result["reason"])

    def test_unsupported_model_effort_combination_blocks(self) -> None:
        self.write_context("gpt-6-astra", "v2", "unsupported")
        result = self.inspect()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("effort", result["reason"])

    def test_permission_context_does_not_gate_model_routing(self) -> None:
        for permissions, approval, reviewer in (
            (":workspace", "on-request", "auto_review"),
            (":danger-full-access", "never", "user"),
            ("manual", "on-request", "user"),
        ):
            with self.subTest(permissions=permissions):
                self.rollout.write_text("", encoding="utf-8")
                self.write_context(
                    "gpt-5.6-sol",
                    "v2",
                    "medium",
                    default_permissions=permissions,
                    approval_policy=approval,
                    approvals_reviewer=reviewer,
                )
                self.assertEqual(self.inspect()["modelconfig"], "native")

    def test_missing_session_meta_or_context_blocks(self) -> None:
        self.rollout.write_text(
            json.dumps(
                {
                    "type": "turn_context",
                    "payload": {
                        "model": "gpt-5.6-sol",
                        "multi_agent_version": "v2",
                        "effort": "medium",
                    },
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.assertEqual(self.inspect()["status"], "blocked")
        self.rollout.write_text("", encoding="utf-8")
        self.assertEqual(self.inspect()["status"], "blocked")

    def test_incompatible_model_or_protocol_blocks(self) -> None:
        for model, version in [
            ("gpt-5.6-sol", "v1"),
            ("orchestra-v1/gpt-5.6-sol", "v2"),
            ("gpt-5.6-terra", "v2"),
        ]:
            self.rollout.write_text("", encoding="utf-8")
            self.write_context(model, version)
            result = self.inspect()
            self.assertEqual(result["status"], "blocked")
            self.assertIn("incompatible", result["reason"])

    def test_missing_thread_blocks(self) -> None:
        self.assertEqual(
            session_model.inspect_session(self.codex_home, None)["status"],
            "blocked",
        )

    def test_latest_incomplete_context_cannot_reuse_older_routing(self) -> None:
        self.write_context("gpt-6-astra", "v2", "low", timestamp="2026-07-31T14:25:00Z")
        continuation = self.rollout.parent / f"{self.thread_id}_new.jsonl"
        self.write_context("gpt-6-astra", "v2", "", path=continuation,
                           timestamp="2026-07-31T14:26:00Z")
        self.assertEqual(self.inspect()["status"], "blocked")

    def test_mixed_timestamp_contexts_are_ambiguous(self) -> None:
        self.write_context("gpt-6-astra", "v2", "low", timestamp="2026-07-31T14:25:00Z")
        self.write_context("gpt-5.6-sol", "v2", "high")
        self.assertEqual(self.inspect()["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
