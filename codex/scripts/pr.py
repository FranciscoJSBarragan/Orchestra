#!/usr/bin/env python3
"""Open, observe, or merge an Orchestra pull request through direct gh commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from policy import blocked, load_policy, run_checks
from _common import SHA_PATTERN, _git, _run


CAPSULE_START = "<!-- PR-CONTEXT:start -->"
CAPSULE_END = "<!-- PR-CONTEXT:end -->"
CAPSULE_PATTERN = re.compile(
    re.escape(CAPSULE_START) + r".*?" + re.escape(CAPSULE_END), re.DOTALL
)
REPOSITORY_PATTERN = re.compile(r"[^/\s]+/[^/\s]+\Z")
GRAPHQL_QUERY = """
query($owner:String!, $name:String!, $number:Int!) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100) {
        pageInfo { hasNextPage }
        nodes {
          isResolved
          isOutdated
          comments(last:1) { nodes { body url author { login } } }
        }
      }
    }
  }
}
""".strip()


def _gh(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run(repo, ["gh", *args])


def _command_error(name: str, result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    detail = result.stderr.strip() or result.stdout.strip() or "no output"
    return blocked(f"{name} failed: {detail}")


def _json_output(
    name: str, result: subprocess.CompletedProcess[str]
) -> tuple[Any | None, dict[str, Any] | None]:
    if result.returncode:
        return None, _command_error(name, result)
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as error:
        return None, blocked(f"{name} returned invalid JSON: {error}")


def _repository_root(repo: Path) -> tuple[Path | None, dict[str, Any] | None]:
    resolved = repo.resolve()
    result = _git(resolved, "rev-parse", "--show-toplevel")
    if result.returncode:
        return None, blocked("repository is not a Git worktree")
    if Path(result.stdout.strip()).resolve() != resolved:
        return None, blocked("--repo must be the Git worktree root")
    return resolved, None


def _resolve_commit(repo: Path, revision: str) -> str | None:
    result = _git(repo, "rev-parse", "--verify", f"{revision}^{{commit}}")
    sha = result.stdout.strip()
    return sha if not result.returncode and SHA_PATTERN.fullmatch(sha) else None


def _upsert_capsule(body: str, capsule: str) -> tuple[str | None, str | None]:
    inside = False
    for token in re.finditer(
        f"{re.escape(CAPSULE_START)}|{re.escape(CAPSULE_END)}", body
    ):
        if token.group(0) == CAPSULE_START:
            if inside:
                return None, "PR body has unmatched, misordered, or nested PR-CONTEXT markers"
            inside = True
        else:
            if not inside:
                return None, "PR body has unmatched, misordered, or nested PR-CONTEXT markers"
            inside = False
    if inside:
        return None, "PR body has unmatched, misordered, or nested PR-CONTEXT markers"

    matches = list(CAPSULE_PATTERN.finditer(body))
    residual = body
    for match in reversed(matches):
        residual = residual[: match.start()] + residual[match.end() :]
    if CAPSULE_START in residual or CAPSULE_END in residual:
        return None, "PR body has unmatched, misordered, or nested PR-CONTEXT markers"
    human_body = residual.strip()
    updated = f"{human_body}\n\n{capsule}\n" if human_body else f"{capsule}\n"
    updated_matches = list(CAPSULE_PATTERN.finditer(updated))
    if (
        len(updated_matches) != 1
        or updated.count(CAPSULE_START) != 1
        or updated.count(CAPSULE_END) != 1
        or updated.find(CAPSULE_START) >= updated.find(CAPSULE_END)
    ):
        return None, "PR-CONTEXT postcondition failed"
    return updated, None


def open_pr(
    repo: Path,
    repository: str,
    base: str,
    head: str,
    title: str,
    body_file: Path,
    context_file: Path,
    authorized: bool,
    policy_path: Path | None,
) -> dict[str, Any]:
    """Create or update one PR after inspecting the complete base..HEAD range."""
    if not authorized:
        return blocked("explicit open-PR authorization is required")
    repo, error = _repository_root(repo)
    if error:
        return error
    assert repo is not None
    if not REPOSITORY_PATTERN.fullmatch(repository):
        return blocked("--repository must be OWNER/REPO")
    policy, policy_result = load_policy(
        policy_path.resolve() if policy_path else repo / "orchestra.toml"
    )
    if policy is None:
        return policy_result
    if policy["mode"] not in {"pr-required", "hybrid"}:
        return blocked("delivery policy does not permit the PR lane")
    if not title.strip() or not base or not head:
        return blocked("base, head, and title are required")
    base_sha = _resolve_commit(repo, base)
    head_sha = _resolve_commit(repo, head)
    if base_sha is None or head_sha is None:
        return blocked("base or head does not resolve to a commit")

    commits = _git(repo, "log", "--format=%H%x09%s", f"{base}..{head}")
    if commits.returncode:
        return _command_error("git log base..HEAD", commits)
    commit_lines = [line for line in commits.stdout.splitlines() if line]
    if not commit_lines:
        return blocked("base..HEAD contains no commits")
    changed = _git(repo, "diff", "--no-renames", "--name-only", f"{base}..{head}")
    if changed.returncode:
        return _command_error("git diff base..HEAD", changed)
    changed_paths = [path for path in changed.stdout.splitlines() if path]
    if not changed_paths:
        return blocked("base..HEAD contains no changed paths")

    try:
        human_body = body_file.read_text(encoding="utf-8")
        intent = context_file.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError) as file_error:
        return blocked(f"cannot read PR input: {file_error}")
    if not intent:
        return blocked("PR context input is empty")
    if CAPSULE_START in intent or CAPSULE_END in intent:
        return blocked("PR context input must not contain capsule markers")

    commit_summary = "\n".join(
        f"- {line.split(chr(9), 1)[0][:12]} {line.split(chr(9), 1)[-1]}"
        for line in commit_lines
    )
    path_summary = "\n".join(f"- {path}" for path in changed_paths)
    capsule = (
        f"{CAPSULE_START}\n"
        f"Base: {base} ({base_sha})\n"
        f"Head: {head_sha}\n"
        f"Commits ({len(commit_lines)}):\n{commit_summary}\n"
        f"Changed paths ({len(changed_paths)}):\n{path_summary}\n"
        f"Intent:\n{intent}\n"
        f"{CAPSULE_END}"
    )

    existing_result = _gh(
        repo,
        "pr",
        "list",
        "--repo",
        repository,
        "--state",
        "open",
        "--base",
        base,
        "--head",
        head,
        "--limit",
        "2",
        "--json",
        "number,body,url",
    )
    existing, error = _json_output("gh pr list", existing_result)
    if error:
        return error
    if not isinstance(existing, list) or len(existing) > 1:
        return blocked("open PR lookup is invalid or ambiguous")

    if existing:
        pr = existing[0]
        if not isinstance(pr, dict) or not isinstance(pr.get("number"), int):
            return blocked("open PR lookup returned invalid state")
        existing_body = pr.get("body")
        if not isinstance(existing_body, str):
            return blocked("existing PR body is unavailable")
        body, marker_error = _upsert_capsule(existing_body, capsule)
        if marker_error:
            return blocked(marker_error)
        assert body is not None
        update = _gh(
            repo,
            "pr",
            "edit",
            str(pr["number"]),
            "--repo",
            repository,
            "--title",
            title,
            "--body",
            body,
        )
        if update.returncode:
            return _command_error("gh pr edit", update)
        return {
            "status": "ok",
            "action": "updated",
            "pr": pr["number"],
            "head": head_sha,
            "commits": len(commit_lines),
        }

    body, marker_error = _upsert_capsule(human_body, capsule)
    if marker_error:
        return blocked(marker_error)
    assert body is not None
    create = _gh(
        repo,
        "pr",
        "create",
        "--repo",
        repository,
        "--base",
        base,
        "--head",
        head,
        "--title",
        title,
        "--body",
        body,
    )
    if create.returncode:
        return _command_error("gh pr create", create)
    url = create.stdout.strip().splitlines()[-1] if create.stdout.strip() else ""
    return {
        "status": "ok",
        "action": "created",
        "url": url,
        "head": head_sha,
        "commits": len(commit_lines),
    }


def _check_state(check: Any) -> str:
    if not isinstance(check, dict):
        return "invalid"
    status = check.get("status")
    conclusion = check.get("conclusion")
    state = check.get("state")
    if state in {"PENDING", "EXPECTED"} or status in {
        "QUEUED",
        "IN_PROGRESS",
        "PENDING",
        "WAITING",
        "REQUESTED",
    }:
        return "pending"
    if state in {"FAILURE", "ERROR"}:
        return "failed"
    if state in {"SUCCESS", "NEUTRAL", "SKIPPED"}:
        return "passed"
    if status == "COMPLETED":
        return "passed" if conclusion in {"SUCCESS", "NEUTRAL", "SKIPPED"} else "failed"
    return "invalid"


def observe_pr(
    repo: Path,
    repository: str,
    pr_number: int,
    previous_clean_head: str | None,
) -> dict[str, Any]:
    """Return a factual current snapshot and in-memory two-observation result."""
    repo, error = _repository_root(repo)
    if error:
        return error
    assert repo is not None
    match = REPOSITORY_PATTERN.fullmatch(repository)
    if not match:
        return blocked("--repository must be OWNER/REPO")
    owner, name = repository.split("/", 1)
    view_result = _gh(
        repo,
        "pr",
        "view",
        str(pr_number),
        "--repo",
        repository,
        "--json",
        "number,state,headRefOid,statusCheckRollup,reviewDecision,mergeStateStatus",
    )
    view, error = _json_output("gh pr view", view_result)
    if error:
        return error
    if not isinstance(view, dict) or view.get("state") != "OPEN":
        return blocked("PR state is closed or invalid")
    head = view.get("headRefOid")
    checks = view.get("statusCheckRollup")
    review_decision = view.get("reviewDecision")
    merge_state = view.get("mergeStateStatus")
    if not isinstance(head, str) or not SHA_PATTERN.fullmatch(head):
        return blocked("PR head is invalid")
    if checks is None:
        checks = []
    if not isinstance(checks, list):
        return blocked("PR check state is invalid")
    if review_decision not in {None, "", "APPROVED", "REVIEW_REQUIRED", "CHANGES_REQUESTED"}:
        return blocked("PR review decision is invalid")
    if not isinstance(merge_state, str) or not merge_state:
        return blocked("PR merge state is invalid")

    threads_result = _gh(
        repo,
        "api",
        "graphql",
        "--field",
        f"query={GRAPHQL_QUERY}",
        "-F",
        f"owner={owner}",
        "-F",
        f"name={name}",
        "-F",
        f"number={pr_number}",
    )
    threads_payload, error = _json_output("gh api graphql", threads_result)
    if error:
        return error
    try:
        thread_connection = threads_payload["data"]["repository"]["pullRequest"][
            "reviewThreads"
        ]
        thread_nodes = thread_connection["nodes"]
        has_next_page = thread_connection["pageInfo"]["hasNextPage"]
    except (KeyError, TypeError):
        return blocked("review-thread state is invalid")
    if not isinstance(thread_nodes, list) or not isinstance(has_next_page, bool):
        return blocked("review-thread state is invalid")

    unresolved_feedback: list[dict[str, str]] = []
    for thread in thread_nodes:
        if not isinstance(thread, dict):
            return blocked("review-thread state is invalid")
        resolved = thread.get("isResolved")
        outdated = thread.get("isOutdated")
        if not isinstance(resolved, bool) or not isinstance(outdated, bool):
            return blocked("review-thread state is invalid")
        if resolved or outdated:
            continue
        comments = thread.get("comments", {}).get("nodes", [])
        latest = comments[-1] if isinstance(comments, list) and comments else {}
        author = latest.get("author") or {}
        unresolved_feedback.append(
            {
                "author": str(author.get("login") or "unknown")[:100],
                "body": " ".join(str(latest.get("body") or "").split())[:500],
                "url": str(latest.get("url") or "")[:500],
            }
        )

    check_states = [_check_state(check) for check in checks]
    if "invalid" in check_states:
        return blocked("PR check state is invalid")
    snapshot: dict[str, Any] = {
        "head": head,
        "checks": {
            "passed": check_states.count("passed"),
            "pending": check_states.count("pending"),
            "failed": check_states.count("failed"),
        },
        "unresolved_feedback": unresolved_feedback,
        "feedback_complete": not has_next_page,
        "review_decision": review_decision,
        "merge_state": merge_state,
    }
    if has_next_page:
        return {"status": "partial", "reason": "review threads are paginated", **snapshot}
    if unresolved_feedback:
        return {"status": "partial", "reason": "unresolved feedback remains", **snapshot}
    if review_decision in {"REVIEW_REQUIRED", "CHANGES_REQUESTED"}:
        return {"status": "partial", "reason": "required review is not approved", **snapshot}
    if merge_state != "CLEAN":
        return {"status": "partial", "reason": "PR merge state is not clean", **snapshot}
    if "pending" in check_states or "failed" in check_states:
        return {"status": "partial", "reason": "checks are not clean", **snapshot}
    if previous_clean_head == head:
        return {"status": "ok", "clean_observation": 2, **snapshot}
    return {"status": "partial", "reason": "first clean observation", "clean_observation": 1, **snapshot}


def merge_pr(
    repo: Path,
    repository: str,
    pr_number: int,
    clean_head: str,
    method: str,
    authorized: bool,
    policy_path: Path | None,
) -> dict[str, Any]:
    """Merge only an explicitly authorized, freshly checked current PR head."""
    if not authorized:
        return blocked("separate explicit merge authorization is required")
    repo, error = _repository_root(repo)
    if error:
        return error
    assert repo is not None
    if not REPOSITORY_PATTERN.fullmatch(repository):
        return blocked("--repository must be OWNER/REPO")
    if method not in {"merge", "squash", "rebase"}:
        return blocked("merge method must be merge, squash, or rebase")
    policy, policy_result = load_policy(
        policy_path.resolve() if policy_path else repo / "orchestra.toml"
    )
    if policy is None:
        return policy_result
    if policy["mode"] not in {"pr-required", "hybrid"}:
        return blocked("delivery policy does not permit the PR lane")

    preflight = _merge_preflight(repo, repository, pr_number, clean_head)
    if preflight is not None:
        return preflight

    check_result = run_checks(repo, policy["checks"])
    if check_result["status"] != "ok":
        return check_result
    preflight = _merge_preflight(repo, repository, pr_number, clean_head)
    if preflight is not None:
        return preflight

    merge = _gh(
        repo,
        "pr",
        "merge",
        str(pr_number),
        "--repo",
        repository,
        f"--{method}",
    )
    if merge.returncode:
        return _command_error("gh pr merge", merge)
    post_result = _gh(
        repo,
        "pr",
        "view",
        str(pr_number),
        "--repo",
        repository,
        "--json",
        "state,headRefOid,mergedAt",
    )
    if post_result.returncode:
        detail = post_result.stderr.strip() or post_result.stdout.strip() or "no output"
        return {
            "status": "partial",
            "reason": f"merge command succeeded but post-state query failed: {detail}"[:500],
            "head": clean_head,
        }
    try:
        post = json.loads(post_result.stdout)
    except json.JSONDecodeError:
        post = None
    if (
        not isinstance(post, dict)
        or post.get("state") != "MERGED"
        or post.get("headRefOid") != clean_head
        or not isinstance(post.get("mergedAt"), str)
        or not post["mergedAt"].strip()
    ):
        return {
            "status": "partial",
            "reason": "merge command succeeded but merged post-state is unverified",
            "head": clean_head,
        }
    return {
        "status": "ok",
        "action": "merged",
        "pr": pr_number,
        "head": clean_head,
        "method": method,
        "checks": check_result["checks"],
        "merged_at": post["mergedAt"],
    }


def _merge_preflight(
    repo: Path, repository: str, pr_number: int, clean_head: str
) -> dict[str, Any] | None:
    if not _worktree_clean(repo):
        return blocked("local worktree must be clean before merge checks")
    current_head = _resolve_commit(repo, "HEAD")
    if current_head != clean_head:
        return blocked("local HEAD does not match the supplied clean PR head")
    view_result = _gh(
        repo,
        "pr",
        "view",
        str(pr_number),
        "--repo",
        repository,
        "--json",
        "state,headRefOid,mergeStateStatus",
    )
    view, error = _json_output("gh pr view", view_result)
    if error:
        return error
    if not isinstance(view, dict) or view.get("state") != "OPEN":
        return blocked("PR state is closed or invalid")
    if view.get("headRefOid") != clean_head:
        return blocked("PR head changed after clean observation")
    if view.get("mergeStateStatus") != "CLEAN":
        return blocked("PR merge state is not clean")
    return None


def _worktree_clean(repo: Path) -> bool:
    result = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    return not result.returncode and not result.stdout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)

    open_parser = subparsers.add_parser("open")
    open_parser.add_argument("--repo", type=Path, required=True)
    open_parser.add_argument("--repository", required=True)
    open_parser.add_argument("--base", required=True)
    open_parser.add_argument("--head", required=True)
    open_parser.add_argument("--title", required=True)
    open_parser.add_argument("--body-file", type=Path, required=True)
    open_parser.add_argument("--context-file", type=Path, required=True)
    open_parser.add_argument("--authorized", action="store_true")
    open_parser.add_argument("--policy", type=Path)

    observe_parser = subparsers.add_parser("observe")
    observe_parser.add_argument("--repo", type=Path, required=True)
    observe_parser.add_argument("--repository", required=True)
    observe_parser.add_argument("--pr", type=int, required=True)
    observe_parser.add_argument("--previous-clean-head")

    merge_parser = subparsers.add_parser("merge")
    merge_parser.add_argument("--repo", type=Path, required=True)
    merge_parser.add_argument("--repository", required=True)
    merge_parser.add_argument("--pr", type=int, required=True)
    merge_parser.add_argument("--clean-head", required=True)
    merge_parser.add_argument("--method", choices=("merge", "squash", "rebase"), required=True)
    merge_parser.add_argument("--authorized", action="store_true")
    merge_parser.add_argument("--policy", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.action == "open":
        result = open_pr(
            args.repo,
            args.repository,
            args.base,
            args.head,
            args.title,
            args.body_file,
            args.context_file,
            args.authorized,
            args.policy,
        )
    elif args.action == "observe":
        result = observe_pr(
            args.repo, args.repository, args.pr, args.previous_clean_head
        )
    else:
        result = merge_pr(
            args.repo,
            args.repository,
            args.pr,
            args.clean_head,
            args.method,
            args.authorized,
            args.policy,
        )
    print(json.dumps(result, sort_keys=True))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
