"""Tests for deterministic Orchestra root-model detection."""

from __future__ import annotations

import importlib.util
import json
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
        **extra: object,
    ) -> None:
        with self.rollout.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"type": "event_msg", "payload": {}}) + "\n")
            stream.write(json.dumps({
                "type": "turn_context",
                "payload": {
                    "model": model,
                    "multi_agent_version": version,
                    "effort": effort,
                    **extra,
                },
            }) + "\n")

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

    def test_orchestra_sol_alias_v1_selects_external_mode(self) -> None:
        self.write_context("orchestra-v1/gpt-5.6-sol", "v1")
        self.assertEqual(self.inspect()["modelconfig"], "external")

    def test_latest_turn_context_is_authoritative(self) -> None:
        self.write_context("gpt-5.6-terra", "v2")
        self.write_context("gpt-5.6-sol", "v2")
        self.assertEqual(self.inspect()["modelconfig"], "native")

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

    def test_unsupported_root_effort_blocks(self) -> None:
        self.write_context("gpt-5.6-sol", "v2", "xhigh")
        result = self.inspect()
        self.assertEqual(result["status"], "blocked")
        self.assertIn("effort", result["reason"])

    def test_missing_thread_or_context_blocks(self) -> None:
        self.assertEqual(
            session_model.inspect_session(self.codex_home, None)["status"],
            "blocked",
        )
        self.assertEqual(self.inspect()["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
