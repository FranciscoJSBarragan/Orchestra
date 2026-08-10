"""Deterministic fake-gh tests for Orchestra PR open, observe, and merge."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "codex/scripts/pr.py"
START = "<!-- PR-CONTEXT:start -->"
END = "<!-- PR-CONTEXT:end -->"


class PullRequestFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        root = Path(self.temporary_directory.name)
        self.base = root / "base"
        self.base.mkdir()
        self.repo = self.base
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Orchestra Test")
        self.git("config", "user.email", "orchestra@example.invalid")
        self.write("base.txt", "base\n")
        self.write("orchestra.toml", self.policy_text("pass"))
        self.git("add", "base.txt", "orchestra.toml")
        self.git("commit", "-q", "-m", "base")
        self.git("branch", "feature")
        task = root / "repo"
        self.git("worktree", "add", "-q", str(task), "feature")
        self.repo = task
        self.write("first.txt", "first\n")
        self.git("add", "first.txt")
        self.git("commit", "-q", "-m", "first change")
        self.write("second.txt", "second\n")
        self.git("add", "second.txt")
        self.git("commit", "-q", "-m", "second change")
        self.head = self.git("rev-parse", "HEAD").stdout.strip()
        self.remote = root / "remote.git"
        subprocess.run(
            ["git", "init", "--bare", "-q", str(self.remote)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-q", "origin", "main", "feature")

        self.body_file = root / "body.md"
        self.body_file.write_text("Human summary\n", encoding="utf-8")
        self.context_file = root / "context.md"
        self.context_file.write_text(
            "Why: deliver the feature.\nAcceptance: tests pass.\n",
            encoding="utf-8",
        )
        self.log = root / "gh.log"
        bin_dir = root / "bin"
        bin_dir.mkdir()
        fake_gh = bin_dir / "gh"
        fake_gh.write_text(
            """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
with Path(os.environ["FAKE_GH_LOG"]).open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(args) + "\\n")
if os.environ.get("FAKE_GH_FAIL") == "view" and args[:2] == ["pr", "view"]:
    print("intentional fake gh failure", file=sys.stderr)
    raise SystemExit(3)
if args[:2] == ["pr", "list"]:
    print(os.environ.get("FAKE_PR_LIST", "[]"))
elif args[:2] == ["pr", "create"]:
    print("https://example.invalid/acme/project/pull/7")
elif args[:2] == ["pr", "edit"]:
    print("https://example.invalid/acme/project/pull/7")
elif args[:2] == ["pr", "view"]:
    if any(
        arg.startswith("state,headRefOid") and "mergeStateStatus" in arg
        for arg in args
    ):
        view_file = os.environ.get("FAKE_MERGE_VIEW_FILE")
        if view_file and Path(view_file).exists():
            print(Path(view_file).read_text(encoding="utf-8"))
        else:
            print(os.environ["FAKE_MERGE_VIEW"])
    elif any("mergedAt" in arg for arg in args):
        print(os.environ["FAKE_POST_MERGE_VIEW"])
    else:
        print(os.environ["FAKE_OBSERVE_VIEW"])
elif args[:2] == ["api", "graphql"]:
    print(os.environ["FAKE_THREADS"])
elif args[:2] == ["pr", "merge"]:
    dirty = os.environ.get("FAKE_MERGE_DIRTY")
    if dirty:
        Path(dirty).write_text("dirty after merge\\n", encoding="utf-8")
    print("merged")
else:
    print("unsupported fake gh command", file=sys.stderr)
    raise SystemExit(2)
""",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        self.environment = {
            **os.environ,
            "PATH": str(bin_dir) + os.pathsep + os.environ.get("PATH", ""),
            "FAKE_GH_LOG": str(self.log),
            "FAKE_PR_LIST": "[]",
            "FAKE_OBSERVE_VIEW": json.dumps(
                {
                    "number": 7,
                    "state": "OPEN",
                    "headRefOid": self.head,
                    "statusCheckRollup": [],
                    "reviewDecision": "APPROVED",
                    "mergeStateStatus": "CLEAN",
                }
            ),
            "FAKE_MERGE_VIEW": json.dumps(
                {
                    "state": "OPEN",
                    "headRefOid": self.head,
                    "headRefName": "feature",
                    "baseRefName": "main",
                    "mergeStateStatus": "CLEAN",
                }
            ),
            "FAKE_THREADS": self.threads([]),
            "FAKE_POST_MERGE_VIEW": json.dumps(
                {
                    "state": "MERGED",
                    "headRefOid": self.head,
                    "headRefName": "feature",
                    "baseRefName": "main",
                    "mergedAt": "2026-07-14T12:00:00Z",
                }
            ),
        }

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            self.fail(result.stdout + result.stderr)
        return result

    def write(self, relative: str, content: str) -> None:
        (self.repo / relative).write_text(content, encoding="utf-8")

    def threads(self, nodes: list[dict], has_next_page: bool = False) -> str:
        return json.dumps(
            {
                "data": {
                    "repository": {
                        "pullRequest": {
                            "reviewThreads": {
                                "pageInfo": {"hasNextPage": has_next_page},
                                "nodes": nodes,
                            }
                        }
                    }
                }
            }
        )

    def run_pr(
        self, *args: str, environment: dict[str, str] | None = None
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [sys.executable, str(HELPER), *args],
            cwd=self.repo,
            check=False,
            capture_output=True,
            text=True,
            env=environment or self.environment,
        )
        return result, json.loads(result.stdout)

    def open_args(self) -> list[str]:
        return [
            "open",
            "--repo",
            str(self.repo),
            "--repository",
            "acme/project",
            "--base",
            "main",
            "--head",
            "feature",
            "--title",
            "Feature delivery",
            "--body-file",
            str(self.body_file),
            "--context-file",
            str(self.context_file),
            "--authorized",
        ]

    def observe_args(self, previous: str | None = None) -> list[str]:
        args = [
            "observe",
            "--repo",
            str(self.repo),
            "--repository",
            "acme/project",
            "--pr",
            "7",
        ]
        if previous:
            args.extend(("--previous-clean-head", previous))
        return args

    def merge_args(
        self,
        method: str = "merge",
        clean_head: str | None = None,
        authorized: bool = True,
        checkout_mode: str = "managed",
        start_revision: str | None = None,
    ) -> list[str]:
        args = [
            "merge",
            "--repo",
            str(self.repo),
            "--base-worktree",
            str(self.base),
            "--task-branch",
            "feature",
            "--base-branch",
            "main",
            "--remote",
            "origin",
            "--repository",
            "acme/project",
            "--pr",
            "7",
            "--clean-head",
            clean_head or self.head,
            "--method",
            method,
        ]
        if authorized:
            args.append("--authorized")
        if checkout_mode != "managed":
            args.extend(("--checkout-mode", checkout_mode))
        if start_revision:
            args.extend(("--start-revision", start_revision))
        return args

    def remote_head(self) -> str | None:
        result = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", "refs/heads/feature"],
            cwd=self.base,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.split()[0] if result.stdout.strip() else None

    def log_entries(self) -> list[list[str]]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def set_observation(
        self,
        checks: list[dict],
        threads: list[dict],
        head: str | None = None,
        review_decision: str | None = "APPROVED",
        merge_state: str = "CLEAN",
    ) -> None:
        self.environment["FAKE_OBSERVE_VIEW"] = json.dumps(
            {
                "number": 7,
                "state": "OPEN",
                "headRefOid": head or self.head,
                "statusCheckRollup": checks,
                "reviewDecision": review_decision,
                "mergeStateStatus": merge_state,
            }
        )
        self.environment["FAKE_THREADS"] = self.threads(threads)

    def policy_text(self, command: str, mode: str = "hybrid") -> str:
        return (
            f"[delivery]\nmode = {json.dumps(mode)}\n\n"
            "[[checks]]\nname = \"suite\"\n"
            f"command = [{json.dumps(sys.executable)}, \"-c\", {json.dumps(command)}]\n"
        )

    def write_policy_command(self, command: str, mode: str = "hybrid") -> None:
        self.write("orchestra.toml", self.policy_text(command, mode))
        self.git("add", "orchestra.toml")
        staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=self.repo, check=False
        )
        if staged.returncode:
            self.git("commit", "-q", "-m", "configure policy")
        self.head = self.git("rev-parse", "HEAD").stdout.strip()
        self.environment["FAKE_MERGE_VIEW"] = json.dumps(
            {
                "state": "OPEN",
                "headRefOid": self.head,
                "headRefName": "feature",
                "baseRefName": "main",
                "mergeStateStatus": "CLEAN",
            }
        )
        self.environment["FAKE_POST_MERGE_VIEW"] = json.dumps(
            {
                "state": "MERGED",
                "headRefOid": self.head,
                "headRefName": "feature",
                "baseRefName": "main",
                "mergedAt": "2026-07-14T12:00:00Z",
            }
        )

    def write_policy(self, passing: bool) -> None:
        self.write_policy_command("pass" if passing else "raise SystemExit(4)")

    def test_open_create_uses_full_range_and_one_capsule(self) -> None:
        result, payload = self.run_pr(*self.open_args())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["action"], "created")
        self.assertEqual(payload["commits"], 2)
        create = next(entry for entry in self.log_entries() if entry[:2] == ["pr", "create"])
        body = create[create.index("--body") + 1]
        self.assertEqual(body.count(START), 1)
        self.assertEqual(body.count(END), 1)
        self.assertIn("Human summary", body)
        self.assertIn("first change", body)
        self.assertIn("second change", body)
        self.assertIn("first.txt", body)
        self.assertIn("second.txt", body)

    def test_open_blocks_missing_authority_before_gh(self) -> None:
        args = self.open_args()
        args.remove("--authorized")

        result, payload = self.run_pr(*args)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authorization", payload["reason"])
        self.assertEqual(self.log_entries(), [])

    def test_open_blocks_missing_or_local_only_policy_before_gh(self) -> None:
        (self.repo / "orchestra.toml").unlink()
        missing_result, missing = self.run_pr(*self.open_args())
        self.assertNotEqual(missing_result.returncode, 0)
        self.assertIn("missing", missing["reason"])
        self.assertEqual(self.log_entries(), [])

        self.write("orchestra.toml", self.policy_text("pass", mode="local-direct"))
        local_result, local = self.run_pr(*self.open_args())
        self.assertNotEqual(local_result.returncode, 0)
        self.assertIn("permit", local["reason"])
        self.assertEqual(self.log_entries(), [])

    def test_open_update_preserves_human_body_and_replaces_capsule(self) -> None:
        self.environment["FAKE_PR_LIST"] = json.dumps(
            [
                {
                    "number": 7,
                    "url": "https://example.invalid/7",
                    "body": (
                        f"Human maintained text\n\n{START}\nold one\n{END}\n\n"
                        f"{START}\nold two\n{END}\n"
                    ),
                }
            ]
        )

        result, payload = self.run_pr(*self.open_args())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["action"], "updated")
        edit = next(entry for entry in self.log_entries() if entry[:2] == ["pr", "edit"])
        body = edit[edit.index("--body") + 1]
        self.assertIn("Human maintained text", body)
        self.assertNotIn("old one", body)
        self.assertNotIn("old two", body)
        self.assertEqual(body.count(START), 1)
        self.assertEqual(body.count(END), 1)

    def test_open_blocks_misordered_or_nested_capsule_markers_before_mutation(self) -> None:
        malformed_bodies = (
            f"Human\n{END}\ntext\n{START}\n",
            f"Human\n{START}\nouter\n{START}\ninner\n{END}\n{END}\n",
            f"Human\n{START}\nouter\n{START}\ninner\n{END}\n",
        )
        for body in malformed_bodies:
            with self.subTest(body=body):
                self.log.unlink(missing_ok=True)
                self.environment["FAKE_PR_LIST"] = json.dumps(
                    [{"number": 7, "url": "https://example.invalid/7", "body": body}]
                )
                result, payload = self.run_pr(*self.open_args())
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("PR-CONTEXT", payload["reason"])
                mutations = [
                    entry
                    for entry in self.log_entries()
                    if entry[:2] in (["pr", "create"], ["pr", "edit"])
                ]
                self.assertEqual(mutations, [])

    def test_observe_pending_and_unresolved_feedback_are_partial(self) -> None:
        self.set_observation([{"status": "IN_PROGRESS", "conclusion": None}], [])
        pending_result, pending = self.run_pr(*self.observe_args())
        self.assertEqual(pending_result.returncode, 0)
        self.assertEqual(pending["status"], "partial")
        self.assertEqual(pending["checks"]["pending"], 1)

        thread = {
            "isResolved": False,
            "isOutdated": False,
            "comments": {
                "nodes": [
                    {
                        "body": "Handle the error",
                        "url": "https://example.invalid/comment",
                        "author": {"login": "reviewer"},
                    }
                ]
            },
        }
        self.set_observation([{"status": "COMPLETED", "conclusion": "SUCCESS"}], [thread])
        unresolved_result, unresolved = self.run_pr(*self.observe_args())
        self.assertEqual(unresolved_result.returncode, 0)
        self.assertEqual(unresolved["status"], "partial")
        self.assertEqual(
            unresolved["unresolved_feedback"][0]["body"], "Handle the error"
        )

    def test_observe_requires_two_clean_observations_on_same_head(self) -> None:
        self.set_observation([{"status": "COMPLETED", "conclusion": "SUCCESS"}], [])

        first_result, first = self.run_pr(*self.observe_args())
        second_result, second = self.run_pr(*self.observe_args(self.head))

        self.assertEqual(first_result.returncode, 0)
        self.assertEqual(first["status"], "partial")
        self.assertEqual(first["clean_observation"], 1)
        self.assertEqual(second_result.returncode, 0)
        self.assertEqual(second["status"], "ok")
        self.assertEqual(second["clean_observation"], 2)

    def test_head_change_resets_and_outdated_feedback_is_ignored(self) -> None:
        new_head = "a" * 40
        outdated = {
            "isResolved": False,
            "isOutdated": True,
            "comments": {"nodes": [{"body": "old", "url": "", "author": None}]},
        }
        self.set_observation([], [outdated], head=new_head)

        result, payload = self.run_pr(*self.observe_args(self.head))

        self.assertEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["clean_observation"], 1)
        self.assertEqual(payload["unresolved_feedback"], [])
        self.assertEqual(payload["head"], new_head)

    def test_review_requirement_and_nonclean_merge_state_never_report_clean(self) -> None:
        for decision, merge_state in (
            ("REVIEW_REQUIRED", "CLEAN"),
            ("CHANGES_REQUESTED", "CLEAN"),
            ("APPROVED", "BLOCKED"),
            ("APPROVED", "DIRTY"),
        ):
            with self.subTest(decision=decision, merge_state=merge_state):
                self.set_observation(
                    [{"status": "COMPLETED", "conclusion": "SUCCESS"}],
                    [],
                    review_decision=decision,
                    merge_state=merge_state,
                )
                result, payload = self.run_pr(*self.observe_args(self.head))
                self.assertEqual(result.returncode, 0)
                self.assertEqual(payload["status"], "partial")
                self.assertEqual(payload["review_decision"], decision)
                self.assertEqual(payload["merge_state"], merge_state)

    def test_observe_command_and_closed_state_block(self) -> None:
        failed_environment = {**self.environment, "FAKE_GH_FAIL": "view"}
        failed_result, failed = self.run_pr(
            *self.observe_args(), environment=failed_environment
        )
        self.assertNotEqual(failed_result.returncode, 0)
        self.assertIn("gh pr view failed", failed["reason"])

        self.environment["FAKE_OBSERVE_VIEW"] = json.dumps(
            {
                "number": 7,
                "state": "CLOSED",
                "headRefOid": self.head,
                "statusCheckRollup": [],
            }
        )
        closed_result, closed = self.run_pr(*self.observe_args())
        self.assertNotEqual(closed_result.returncode, 0)
        self.assertIn("closed or invalid", closed["reason"])

    def test_merge_requires_authority_and_current_head(self) -> None:
        result, payload = self.run_pr(*self.merge_args("squash", authorized=False))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authorization", payload["reason"])
        self.assertEqual(self.log_entries(), [])

        self.write_policy(passing=True)
        result, payload = self.run_pr(
            *self.merge_args("squash", clean_head="b" * 40)
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("local HEAD", payload["reason"])
        self.assertEqual(self.log_entries(), [])

    def test_merge_blocks_failed_checks_without_calling_gh_merge(self) -> None:
        self.write_policy(passing=False)

        result, payload = self.run_pr(*self.merge_args())

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "blocked")
        self.assertIn("check", payload["reason"])
        self.assertFalse(any(entry[:2] == ["pr", "merge"] for entry in self.log_entries()))

    def test_merge_requires_clean_worktree_before_checks(self) -> None:
        self.write("private.txt", "dirty\n")

        result, payload = self.run_pr(*self.merge_args())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("clean", payload["reason"])
        self.assertEqual(self.log_entries(), [])

    def test_merge_rechecks_dirty_worktree_and_changed_head_after_checks(self) -> None:
        self.write_policy_command(
            "from pathlib import Path; Path('dirty.txt').write_text('dirty')"
        )
        dirty_result, dirty = self.run_pr(*self.merge_args())
        self.assertNotEqual(dirty_result.returncode, 0)
        self.assertIn("worktree must be clean", dirty["reason"])
        self.assertFalse(any(entry[:2] == ["pr", "merge"] for entry in self.log_entries()))

        (self.repo / "dirty.txt").unlink()
        self.log.unlink(missing_ok=True)
        self.write_policy_command(
            "import subprocess; subprocess.run(['git', 'commit', '--allow-empty', "
            "'-m', 'check moved head'], check=True)"
        )
        clean_head = self.head
        changed_result, changed = self.run_pr(
            *self.merge_args(clean_head=clean_head)
        )
        self.assertNotEqual(changed_result.returncode, 0)
        self.assertIn("local HEAD", changed["reason"])
        self.assertFalse(any(entry[:2] == ["pr", "merge"] for entry in self.log_entries()))

    def test_merge_rechecks_remote_head_after_checks(self) -> None:
        view_file = Path(self.temporary_directory.name) / "merge-view.json"
        changed_view = json.dumps(
            {
                "state": "OPEN",
                "headRefOid": "c" * 40,
                "headRefName": "feature",
                "baseRefName": "main",
                "mergeStateStatus": "CLEAN",
            }
        )
        self.environment["FAKE_MERGE_VIEW_FILE"] = str(view_file)
        self.write_policy_command(
            "from pathlib import Path; "
            f"Path({str(view_file)!r}).write_text({changed_view!r})"
        )

        result, payload = self.run_pr(*self.merge_args())

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("head", payload["reason"])
        self.assertFalse(any(entry[:2] == ["pr", "merge"] for entry in self.log_entries()))

    def test_merge_exit_zero_without_merged_poststate_is_partial(self) -> None:
        self.environment["FAKE_POST_MERGE_VIEW"] = json.dumps(
            {
                "state": "OPEN",
                "headRefOid": self.head,
                "headRefName": "feature",
                "baseRefName": "main",
                "mergedAt": None,
            }
        )

        result, payload = self.run_pr(*self.merge_args("squash"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "partial")
        self.assertIn("unverified", payload["reason"])
        self.assertEqual(payload["cleanup"], [])
        self.assertEqual(
            {item["resource"] for item in payload["retained_resources"]},
            {"remote_branch", "worktree", "local_branch"},
        )
        self.assertTrue(self.repo.exists())
        self.assertEqual(self.remote_head(), self.head)
        self.assertTrue(any(entry[:2] == ["pr", "merge"] for entry in self.log_entries()))

    def test_merge_fake_success_uses_selected_method(self) -> None:
        self.write_policy(passing=True)
        private = self.repo / ".orchestra"
        private.mkdir()
        (private / ".gitignore").write_text(
            "# Orchestra task-private state; removed after successful delivery.\n*\n",
            encoding="utf-8",
        )
        plan_path = private / "plan.md"
        plan_path.write_text("status: completed\n", encoding="utf-8")

        result, payload = self.run_pr(*self.merge_args("rebase"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["method"], "rebase")
        self.assertEqual(payload["merged_at"], "2026-07-14T12:00:00Z")
        self.assertEqual(
            payload["cleanup"],
            ["remote_branch", "private_state", "worktree", "local_branch"],
        )
        self.assertEqual(payload["retained_resources"], [])
        self.assertFalse(self.repo.exists())
        self.assertFalse(plan_path.exists())
        local_branch = subprocess.run(
            ["git", "branch", "--list", "feature"],
            cwd=self.base,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(local_branch.stdout, "")
        self.assertIsNone(self.remote_head())
        merge = next(entry for entry in self.log_entries() if entry[:2] == ["pr", "merge"])
        self.assertIn("--rebase", merge)

    def test_hybrid_merge_restores_start_branch_and_preserves_checkout(self) -> None:
        self.write_policy(passing=True)
        start_revision = self.git("rev-parse", "main").stdout.strip()
        private = self.repo / ".orchestra"
        (private / "artifacts").mkdir(parents=True)
        (private / ".gitignore").write_text(
            "# Orchestra task-private state; removed after successful delivery.\n*\n",
            encoding="utf-8",
        )
        (private / "plan.md").write_text("status: completed\n", encoding="utf-8")
        (private / "artifacts/report.md").write_text("done\n", encoding="utf-8")
        subprocess.run(
            ["git", "switch", "--detach"],
            cwd=self.base,
            check=True,
            capture_output=True,
            text=True,
        )

        args = self.merge_args(
            "merge", checkout_mode="hybrid", start_revision=start_revision
        )
        base_index = args.index("--base-worktree") + 1
        args[base_index] = str(self.repo)
        result, payload = self.run_pr(*args)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(self.repo.exists())
        self.assertEqual(self.git("branch", "--show-current").stdout.strip(), "main")
        self.assertEqual(self.git("rev-parse", "HEAD").stdout.strip(), start_revision)
        self.assertEqual(self.git("branch", "--list", "feature").stdout, "")
        self.assertEqual(
            payload["cleanup"], ["remote_branch", "local_branch", "private_state"]
        )
        self.assertEqual(payload["preserved"], ["worktree"])
        self.assertFalse(private.exists())

    def test_merge_cleanup_accepts_an_absent_remote_branch(self) -> None:
        self.write_policy(passing=True)
        self.git("push", "-q", "origin", "--delete", "feature")

        result, payload = self.run_pr(*self.merge_args("squash"))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["retained_resources"], [])
        self.assertFalse(self.repo.exists())

    def test_merge_cleanup_preserves_a_moved_remote_branch(self) -> None:
        main_head = subprocess.run(
            ["git", "rev-parse", "main"],
            cwd=self.base,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        subprocess.run(
            [
                "git",
                "--git-dir",
                str(self.remote),
                "update-ref",
                "refs/heads/feature",
                main_head,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        result, payload = self.run_pr(*self.merge_args())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(
            [item["resource"] for item in payload["retained_resources"]],
            ["remote_branch"],
        )
        self.assertEqual(self.remote_head(), main_head)
        self.assertFalse(self.repo.exists())

    def test_merge_cleanup_preserves_dirty_post_merge_work(self) -> None:
        dirty_path = self.repo / "post-merge.txt"
        environment = {
            **self.environment,
            "FAKE_MERGE_DIRTY": str(dirty_path),
        }

        result, payload = self.run_pr(*self.merge_args(), environment=environment)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(
            {item["resource"] for item in payload["retained_resources"]},
            {"remote_branch", "worktree", "local_branch"},
        )
        self.assertTrue(dirty_path.exists())
        self.assertEqual(self.remote_head(), self.head)

    def test_merge_cleanup_reports_locked_worktree_as_partial(self) -> None:
        self.git("worktree", "lock", str(self.repo))

        result, payload = self.run_pr(*self.merge_args())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(
            [item["resource"] for item in payload["retained_resources"]],
            ["worktree", "local_branch"],
        )
        self.assertTrue(self.repo.exists())
        self.assertIsNone(self.remote_head())

    def test_merge_cleanup_rejects_unrecognized_private_state(self) -> None:
        private = self.repo / ".orchestra"
        private.mkdir()
        (private / ".gitignore").write_text(
            "# Orchestra task-private state; removed after successful delivery.\n*\n",
            encoding="utf-8",
        )
        (private / "unknown.txt").write_text("do not delete\n", encoding="utf-8")

        result, payload = self.run_pr(*self.merge_args())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(payload["status"], "partial")
        retained = {
            item["resource"]: item["reason"]
            for item in payload["retained_resources"]
        }
        self.assertIn("unknown entries", retained["private_state"])
        self.assertEqual(set(retained), {"private_state", "worktree", "local_branch"})
        self.assertTrue((private / "unknown.txt").is_file())


if __name__ == "__main__":
    unittest.main()
