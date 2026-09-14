"""Focused process-boundary tests for the standalone delegation adapter."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import signal
import re
import stat
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "codex/scripts/delegate.py"
_SPEC = importlib.util.spec_from_file_location("orchestra_delegate_tests", HELPER)
assert _SPEC is not None and _SPEC.loader is not None
delegate = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = delegate
_SPEC.loader.exec_module(delegate)


class DelegateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Orchestra Test")
        self.git("config", "user.email", "orchestra@example.invalid")
        (self.repo / "source.txt").write_text("seed\n", encoding="utf-8")
        self.git("add", "source.txt")
        self.git("commit", "-q", "-m", "seed")
        self.head = self.git("rev-parse", "HEAD").stdout.strip()
        self.prompt = self.root / "prompt.txt"
        self.prompt.write_text("Inspect the fixture.\n", encoding="utf-8")
        self.log = self.root / "events.jsonl"
        self.bin = self.root / "bin"
        self.bin.mkdir()

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *arguments],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def fake_cli(self, name: str, body: str) -> Path:
        path = self.bin / name
        path.write_text("#!/usr/bin/env python3\n" + textwrap.dedent(body), encoding="utf-8")
        path.chmod(0o700)
        return path

    def run_cli(
        self,
        executor: str,
        capability: str = "general_implementation",
        *,
        model: str = "test-model",
        permissions: str = "default",
        timeout: str | None = None,
        resume: str | None = None,
        expected_head: str | None = None,
        output_paths: tuple[str, ...] = (),
        env: dict[str, str] | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        arguments = [
            sys.executable,
            str(HELPER),
            "--repo",
            str(self.repo),
            "--executor",
            executor,
            "--capability",
            capability,
            "--model",
            model,
            "--prompt-file",
            str(self.prompt),
            "--log-file",
            str(self.log),
            "--expected-head",
            expected_head or self.head,
            "--permissions",
            permissions,
        ]
        if timeout is not None:
            arguments.extend(("--timeout", timeout))
        if resume is not None:
            arguments.extend(("--resume", resume))
        for output_path in output_paths:
            arguments.extend(("--output-path", output_path))
        child_env = os.environ.copy()
        child_env["PATH"] = os.fspath(self.bin) + os.pathsep + child_env.get("PATH", "")
        if env:
            child_env.update(env)
        result = subprocess.run(
            arguments,
            cwd=ROOT,
            env=child_env,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(result.stdout + result.stderr)
        return result, payload

    def test_command_authority_is_scoped_by_capability_and_permissions(self) -> None:
        cursor_default = delegate.build_command(
            executor="cursor",
            repo=self.repo,
            model="cursor-model",
            capability="independent_review",
            permissions="default",
            prompt="brief",
        )
        self.assertIn("--mode", cursor_default)
        self.assertIn("ask", cursor_default)
        self.assertNotIn("--force", cursor_default)
        self.assertNotIn("--trust", cursor_default)

        cursor_trusted = delegate.build_command(
            executor="cursor",
            repo=self.repo,
            model="cursor-model",
            capability="general_implementation",
            permissions="trusted",
            prompt="brief",
        )
        self.assertIn("--trust", cursor_trusted)
        self.assertIn("--force", cursor_trusted)

        cursor_trusted_readonly = delegate.build_command(
            executor="cursor",
            repo=self.repo,
            model="cursor-model",
            capability="runtime_verification",
            permissions="trusted",
            prompt="brief",
        )
        self.assertIn("--trust", cursor_trusted_readonly)
        self.assertIn("--force", cursor_trusted_readonly)
        self.assertNotIn("--mode", cursor_trusted_readonly)

        grok_trusted = delegate.build_command(
            executor="grok",
            repo=self.repo,
            model="grok-model",
            capability="general_implementation",
            permissions="trusted",
            prompt="brief",
            grok_prompt_file=self.prompt,
            session_id="11111111-1111-4111-8111-111111111111",
        )
        self.assertIn("--permission-mode", grok_trusted)
        self.assertIn("bypassPermissions", grok_trusted)
        self.assertIn("--no-subagents", grok_trusted)
        self.assertNotIn("--continue", grok_trusted)
        self.assertNotIn("--worktree", grok_trusted)

        grok_readonly = delegate.build_command(
            executor="grok",
            repo=self.repo,
            model="grok-model",
            capability="runtime_verification",
            permissions="trusted",
            prompt="brief",
            grok_prompt_file=self.prompt,
            session_id="11111111-1111-4111-8111-111111111111",
        )
        self.assertIn("bypassPermissions", grok_readonly)
        self.assertNotIn("plan", grok_readonly)

    def test_cursor_protocol_is_parsed_and_live_events_are_appended_exactly(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            print(json.dumps({"type":"system","subtype":"init","session_id":"cursor-1","model":"test-model"}), flush=True)
            print(json.dumps({"type":"assistant","message":{"role":"assistant"}}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"CURSOR_OK","session_id":"cursor-1"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor", permissions="trusted")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["session_id"], "cursor-1")
        self.assertEqual(payload["observed_model"], "test-model")
        self.assertEqual(payload["result"], "CURSOR_OK")
        self.assertEqual(
            self.log.read_bytes(),
            b'{"type": "system", "subtype": "init", "session_id": "cursor-1", "model": "test-model"}\n'
            b'{"type": "assistant", "message": {"role": "assistant"}}\n'
            b'{"type": "result", "subtype": "success", "is_error": false, "result": "CURSOR_OK", "session_id": "cursor-1"}\n',
        )
        self.assertIn("session_id=cursor-1", result.stderr)

    def test_grok_protocol_allocates_new_session_and_concatenates_text(self) -> None:
        self.fake_cli(
            "grok",
            """
            import json
            print(json.dumps({"type":"text","data":"GROK_"}), flush=True)
            print(json.dumps({"type":"text","data":"OK"}), flush=True)
            print(json.dumps({"type":"end","stopReason":"end_turn","sessionId":"grok-1","modelUsage":{"test-model":{}}}), flush=True)
            """,
        )
        result, payload = self.run_cli("grok", model="test-model")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["session_id"], "grok-1")
        self.assertEqual(payload["result"], "GROK_OK")
        self.assertEqual(payload["observed_model"], "test-model")
        self.assertRegex(
            payload["allocated_session_id"],
            re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"),
        )

    def test_resume_is_explicit_and_does_not_add_ambiguous_continue(self) -> None:
        command = delegate.build_command(
            executor="cursor",
            repo=self.repo,
            model="cursor-model",
            capability="repository_context",
            permissions="default",
            prompt="brief",
            resume="cursor-exact-id",
        )
        self.assertEqual(command[command.index("--resume") + 1], "cursor-exact-id")
        self.assertNotIn("--continue", command)

        self.fake_cli(
            "cursor-agent",
            """
            import json
            print(json.dumps({"type":"system","subtype":"init","session_id":"resume-id","model":"test-model"}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"RESUMED"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor", resume="resume-id")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["result"], "RESUMED")

    def test_model_display_label_does_not_create_a_false_mismatch(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            print(json.dumps({"type":"system","subtype":"init","session_id":"label-1","model":"Claude Fable 5.1 300K Medium"}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"DONE"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor", model="claude-fable-5-1-thinking-medium")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["requested_model"], "claude-fable-5-1-thinking-medium")
        self.assertEqual(payload["observed_model"], "Claude Fable 5.1 300K Medium")

    def test_cursor_terminal_requires_success_and_explicit_non_error(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            print(json.dumps({"type":"result","subtype":"success","result":"DONE"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "partial")
        self.assertTrue(payload["terminal_seen"])
        self.assertFalse(payload["final_seen"])

    def test_readonly_tracked_mutation_blocks_and_reports_content_change(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            from pathlib import Path
            Path('source.txt').write_text('changed\\n', encoding='utf-8')
            print(json.dumps({"type":"system","subtype":"init","session_id":"review-1","model":"test-model"}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"DONE"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor", capability="independent_review")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["changed_paths"], ["source.txt"])
        self.assertEqual(payload["source_changed_paths"], ["source.txt"])

    def test_implementation_mutation_is_reported_without_readonly_rejection(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            from pathlib import Path
            Path('source.txt').write_text('implementation\\n', encoding='utf-8')
            print(json.dumps({"type":"system","subtype":"init","session_id":"impl-1","model":"test-model"}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"IMPLEMENTED"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor", permissions="trusted")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["changed_paths"], ["source.txt"])

    def test_readonly_index_mutation_is_reported_and_blocked(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            import subprocess
            from pathlib import Path
            Path('source.txt').write_text('staged\\n', encoding='utf-8')
            subprocess.run(['git', 'add', 'source.txt'], check=True)
            print(json.dumps({"type":"system","subtype":"init","session_id":"index-1","model":"test-model"}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"CHECKED"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor", capability="independent_review")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["index_changed_paths"], ["source.txt"])
        self.assertTrue(payload["index_changed"])

    def test_verification_may_report_new_untracked_output_but_blocks_tracked_source(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            from pathlib import Path
            Path('verification-output.txt').write_text('report\\n', encoding='utf-8')
            print(json.dumps({"type":"system","subtype":"init","session_id":"verify-1","model":"test-model"}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"CHECKED"}), flush=True)
            """,
        )
        result, payload = self.run_cli(
            "cursor",
            capability="runtime_verification",
            output_paths=("verification-output.txt",),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["changed_paths"], ["verification-output.txt"])

    def test_nonzero_quota_is_blocked_and_missing_final_is_partial(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import sys
            print('quota exceeded', file=sys.stderr, flush=True)
            raise SystemExit(7)
            """,
        )
        result, payload = self.run_cli("cursor")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("quota", payload["reason"])

        self.log.unlink()
        self.fake_cli(
            "cursor-agent",
            """
            import json
            print(json.dumps({"type":"system","subtype":"init","session_id":"missing-1","model":"test-model"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "partial")
        self.assertIn("without a final result", payload["reason"])

    def test_timeout_terminates_only_the_delegation_process_group(self) -> None:
        child_pid_file = self.root / "child.pid"
        self.fake_cli(
            "cursor-agent",
            """
            import os
            import subprocess
            import sys
            from pathlib import Path
            child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'])
            Path(os.environ['CHILD_PID_FILE']).write_text(str(child.pid), encoding='utf-8')
            time = __import__('time')
            time.sleep(30)
            """,
        )
        result, payload = self.run_cli(
            "cursor",
            timeout="1.0",
            env={"CHILD_PID_FILE": str(child_pid_file)},
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "partial")
        self.assertTrue(payload["timed_out"])
        child_pid = int(child_pid_file.read_text(encoding="utf-8"))
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        else:
            self.fail("delegation child process survived timeout cleanup")

    def test_head_binding_blocks_moved_head(self) -> None:
        self.fake_cli(
            "cursor-agent",
            """
            import json
            import subprocess
            subprocess.run(['git','commit','--allow-empty','-q','-m','delegated'], check=True)
            print(json.dumps({"type":"system","subtype":"init","session_id":"moved-1","model":"test-model"}), flush=True)
            print(json.dumps({"type":"result","subtype":"success","is_error":False,"result":"DONE"}), flush=True)
            """,
        )
        result, payload = self.run_cli("cursor")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertNotEqual(payload["before_head"], payload["after_head"])

    def test_path_and_flag_validation_rejects_repo_log_symlinks_and_continue(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(HELPER),
                "--repo",
                str(self.repo),
                "--executor",
                "cursor",
                "--capability",
                "general_implementation",
                "--model",
                "test-model",
                "--prompt-file",
                str(self.prompt),
                "--log-file",
                str(self.repo / "events.jsonl"),
                "--expected-head",
                self.head,
                "--continue",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid")

        symlink = self.root / "prompt-link"
        symlink.symlink_to(self.prompt)
        arguments = [
            sys.executable,
            str(HELPER),
            "--repo",
            str(self.repo),
            "--executor",
            "cursor",
            "--capability",
            "general_implementation",
            "--model",
            "test-model",
            "--prompt-file",
            str(symlink),
            "--log-file",
            str(self.log),
            "--expected-head",
            self.head,
        ]
        result = subprocess.run(arguments, cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid")

    def test_existing_log_and_tracked_output_allowlist_are_rejected(self) -> None:
        self.log.write_bytes(b"existing\n")
        result, payload = self.run_cli("cursor")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["status"], "invalid")
        self.assertEqual(self.log.read_bytes(), b"existing\n")
        self.log.unlink()
        result, payload = self.run_cli(
            "cursor", capability="runtime_verification", output_paths=("source.txt",),
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(payload["status"], "invalid")

    def test_codex_commands_preserve_exact_model_effort_and_resume_permissions(self) -> None:
        session = "11111111-1111-4111-8111-111111111111"
        for capability, permissions, expected_sandbox in (
            ("general_implementation", "trusted", "danger-full-access"),
            ("runtime_verification", "trusted", "danger-full-access"),
            ("independent_review", "trusted", "read-only"),
            ("architecture_analysis", "default", "read-only"),
            ("general_implementation", "default", None),
        ):
            for resume in (None, session):
                with self.subTest(capability=capability, permissions=permissions, resume=resume):
                    cmd = delegate.build_command(executor="codex", repo=self.repo,
                        model="selected-model", capability=capability,
                        permissions=permissions, prompt="exact prompt", effort="low", resume=resume)
                    self.assertEqual(cmd[:2], ["codex", "exec"])
                    self.assertEqual(cmd[cmd.index("--model")+1], "selected-model")
                    self.assertIn('model_reasoning_effort="low"', cmd)
                    self.assertEqual(cmd[cmd.index("--cd")+1], str(self.repo))
                    self.assertEqual(cmd[-1], "exact prompt")
                    self.assertNotIn("--last", cmd)
                    self.assertNotIn("--ephemeral", cmd)
                    if expected_sandbox:
                        self.assertEqual(cmd[cmd.index("--sandbox")+1], expected_sandbox)
                    else:
                        self.assertNotIn("--sandbox", cmd)
                        self.assertNotIn('approval_policy="never"', cmd)
                    if resume:
                        self.assertEqual(cmd[cmd.index("resume")+1], session)
                        self.assertLess(cmd.index("--cd"), cmd.index("resume"))

    def test_codex_rejects_browser_and_ambiguous_resume(self) -> None:
        for capability, resume in (("browser_acceptance", None),
                                   ("general_implementation", "a task title")):
            with self.assertRaises(delegate.DelegateInputError):
                delegate.build_command(executor="codex", repo=self.repo, model="selected",
                    capability=capability, permissions="trusted", prompt="brief", resume=resume)

    def test_codex_protocol_requires_terminal_and_agent_result(self) -> None:
        for terminal, message, expected in (("turn.completed", "DONE", "ok"),
                                           ("turn.completed", "", "partial"),
                                           ("turn.failed", "DONE", "partial"),
                                           (None, "DONE", "partial")):
            with self.subTest(terminal=terminal, message=message):
                self.log.unlink(missing_ok=True)
                self.fake_cli("codex", f'''
                    import json
                    print(json.dumps({{"type":"thread.started","thread_id":"11111111-1111-4111-8111-111111111111"}}))
                    print(json.dumps({{"type":"turn.started"}}))
                    print(json.dumps({{"type":"item.completed","item":{{"type":"agent_message","text":{message!r}}}}}))
                    if {terminal!r}: print(json.dumps({{"type":{terminal!r},"error":{{"message":"failed"}}}}))
                ''')
                result, payload = self.run_cli("codex")
                self.assertEqual(payload["status"], expected)
                self.assertIsNone(payload["observed_model"])
                self.assertEqual(payload["session_id"], "11111111-1111-4111-8111-111111111111")
                self.assertEqual(result.returncode, 0 if expected == "ok" else 1)

    def test_codex_readonly_changes_remain_blocked(self) -> None:
        self.fake_cli("codex", '''
            import json
            from pathlib import Path
            Path('source.txt').write_text('unauthorized')
            print(json.dumps({"type":"item.completed","item":{"type":"agent_message","text":"DONE"}}))
            print(json.dumps({"type":"turn.completed"}))
        ''')
        _, payload = self.run_cli("codex", capability="independent_review", permissions="trusted")
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["changed_paths"], ["source.txt"])

    def assert_process_stopped(self, pid: int) -> None:
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.03)
        self.fail(f"owned process {pid} survived cleanup")

    def test_sigterm_returns_partial_changes_and_stops_owned_group(self) -> None:
        pid_file = self.root / "running.pid"
        self.fake_cli("cursor-agent", f'''
            import os, time
            from pathlib import Path
            Path('source.txt').write_text('partial edit')
            Path({str(pid_file)!r}).write_text(str(os.getpid()))
            time.sleep(30)
        ''')
        env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ.get("PATH", ""))
        command = [sys.executable, str(HELPER), "--repo", str(self.repo),
                   "--executor", "cursor", "--capability", "general_implementation",
                   "--model", "test-model", "--expected-head", self.head,
                   "--prompt-file", str(self.prompt), "--log-file", str(self.log)]
        process = subprocess.Popen(command, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True)
        unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            deadline = time.monotonic() + 8
            while not pid_file.exists() and time.monotonic() < deadline:
                time.sleep(0.03)
            self.assertTrue(pid_file.exists())
            process.send_signal(signal.SIGTERM)
            stdout, stderr = process.communicate(timeout=8)
            payload = json.loads(stdout)
            self.assertEqual(payload["status"], "partial", stderr)
            self.assertTrue(payload["cancelled"])
            self.assertEqual(payload["changed_paths"], ["source.txt"])
            self.assertEqual(payload["after_head"], self.head)
            self.assert_process_stopped(int(pid_file.read_text()))
            self.assertIsNone(unrelated.poll())
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=8)
            unrelated.terminate()
            unrelated.wait(timeout=5)

    def test_normal_leader_exit_stops_detached_pipe_descendant(self) -> None:
        pid_file = self.root / "child.pid"
        self.fake_cli("cursor-agent", f'''
            import json, subprocess, sys
            from pathlib import Path
            child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
            Path({str(pid_file)!r}).write_text(str(child.pid))
            print(json.dumps({{"type":"result","subtype":"success","is_error":False,"result":"DONE"}}), flush=True)
        ''')
        result, payload = self.run_cli("cursor")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assert_process_stopped(int(pid_file.read_text()))

    def test_log_write_failure_stops_process_and_returns_transport_error(self) -> None:
        pid_file = self.root / "transport.pid"
        code = ("import os,time; from pathlib import Path; "
                f"Path({str(pid_file)!r}).write_text(str(os.getpid())); "
                "print('event', flush=True); time.sleep(30)")
        log = mock.Mock()
        log.write.side_effect = OSError("disk full")
        capture = delegate._run_process([sys.executable, "-c", code], self.repo,
                                        "cursor", "test-model", log, 5)
        self.assertIn("disk full", capture.transport_error)
        self.assert_process_stopped(int(pid_file.read_text()))


if __name__ == "__main__":
    unittest.main()
