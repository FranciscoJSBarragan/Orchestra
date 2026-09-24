#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

STATE = Path(__file__).resolve().parent.parent / "gh-state"
PRS = STATE / "prs.json"
CALLS = STATE / "calls.log"
REPO_LABEL_FILE = STATE / "repo-label"
HOST = "https://github.example"


def load_prs() -> list[dict]:
    return json.loads(PRS.read_text(encoding="utf-8")) if PRS.is_file() else []


def save_prs(prs: list[dict]) -> None:
    PRS.write_text(json.dumps(prs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def option(args: list[str], name: str, default: str | None = None) -> str | None:
    for index, argument in enumerate(args):
        if argument == name and index + 1 < len(args):
            return args[index + 1]
        if argument.startswith(f"{name}="):
            return argument.split("=", 1)[1]
    return default


def current_branch() -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def select(prs: list[dict], selector: str | None) -> dict | None:
    if selector is None:
        selector = current_branch()
    for pr in prs:
        if selector in (str(pr["number"]), pr["url"], pr["headRefName"]):
            return pr
    return None


def project(pr: dict, fields: str | None) -> dict:
    if not fields:
        return pr
    missing = [field for field in fields.split(",") if field not in pr]
    if missing:
        fail(f"unknown --json field(s): {', '.join(missing)}")
    return {field: pr[field] for field in fields.split(",")}


def fail(message: str, code: int = 1) -> None:
    print(f"gh fixture: {message}", file=sys.stderr)
    raise SystemExit(code)


def pr_create(args: list[str]) -> None:
    head = option(args, "--head") or current_branch()
    base = option(args, "--base")
    title = option(args, "--title")
    body_file = option(args, "--body-file")
    body = option(args, "--body")
    if body_file:
        body = sys.stdin.read() if body_file == "-" else Path(body_file).read_text(encoding="utf-8")
    if not (head and base and title and body is not None):
        fail("pr create needs --base, --head (or a current branch), --title, and --body/--body-file")
    prs = load_prs()
    if any(pr["headRefName"] == head and pr["state"] == "OPEN" for pr in prs):
        fail(f"a pull request for branch {head} already exists", 1)
    number = len(prs) + 1
    label = REPO_LABEL_FILE.read_text(encoding="utf-8").strip() if REPO_LABEL_FILE.is_file() else "fixture/lite"
    pr = {
        "number": number,
        "url": f"{HOST}/{label}/pull/{number}",
        "state": "OPEN",
        "isDraft": "--draft" in args,
        "baseRefName": base,
        "headRefName": head,
        "title": title,
        "body": body,
    }
    prs.append(pr)
    save_prs(prs)
    print(pr["url"])


def pr_edit(args: list[str]) -> None:
    prs = load_prs()
    selector = args[0] if args and not args[0].startswith("--") else None
    pr = select(prs, selector)
    if pr is None:
        fail("no pull request matches the selector")
    if (title := option(args, "--title")) is not None:
        pr["title"] = title
    body_file = option(args, "--body-file")
    if body_file:
        pr["body"] = sys.stdin.read() if body_file == "-" else Path(body_file).read_text(encoding="utf-8")
    elif (body := option(args, "--body")) is not None:
        pr["body"] = body
    save_prs(prs)
    print(pr["url"])


def pr_view(args: list[str]) -> None:
    selector = args[0] if args and not args[0].startswith("--") else None
    pr = select(load_prs(), selector)
    if pr is None:
        fail("no pull requests found", 1)
    fields = option(args, "--json")
    if fields is None:
        print(f"{pr['title']} #{pr['number']}\n{pr['url']}\nDraft: {str(pr['isDraft']).lower()}")
        return
    print(json.dumps(project(pr, fields), ensure_ascii=False))


def pr_list(args: list[str]) -> None:
    prs = load_prs()
    head = option(args, "--head")
    base = option(args, "--base")
    state = (option(args, "--state") or "open").upper()
    selected = [
        pr for pr in prs
        if (head is None or pr["headRefName"] == head)
        and (base is None or pr["baseRefName"] == base)
        and (state == "ALL" or pr["state"] == state)
    ]
    fields = option(args, "--json")
    if fields is None:
        for pr in selected:
            print(f"{pr['number']}\t{pr['title']}\t{pr['headRefName']}\t{'DRAFT' if pr['isDraft'] else 'OPEN'}")
        return
    print(json.dumps([project(pr, fields) for pr in selected], ensure_ascii=False))


def main(argv: list[str]) -> int:
    STATE.mkdir(parents=True, exist_ok=True)
    with CALLS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(argv, ensure_ascii=False) + "\n")
    if "--jq" in argv or any(argument.startswith("--jq=") for argument in argv):
        fail("--jq is not simulated; use --json and parse the output")
    if argv[:1] == ["--version"]:
        print("gh version 0.0.0-fixture")
        return 0
    if argv[:2] == ["auth", "status"]:
        print("Logged in to github.example as fixture (simulated)")
        return 0
    if argv[:2] == ["repo", "view"]:
        label = REPO_LABEL_FILE.read_text(encoding="utf-8").strip() if REPO_LABEL_FILE.is_file() else "fixture/lite"
        fields = option(argv[2:], "--json")
        record = {"nameWithOwner": label, "url": f"{HOST}/{label}", "defaultBranchRef": {"name": "main"}}
        print(json.dumps(project(record, fields), ensure_ascii=False) if fields else record["url"])
        return 0
    if argv[:1] == ["pr"] and len(argv) >= 2:
        handlers = {"create": pr_create, "view": pr_view, "list": pr_list, "edit": pr_edit}
        handler = handlers.get(argv[1])
        if handler is not None:
            handler(argv[2:])
            return 0
    fail(f"unsupported command in this fixture: {' '.join(argv) or '(none)'}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
