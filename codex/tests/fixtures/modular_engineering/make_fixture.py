#!/usr/bin/env python3
"""Create two disposable repos whose local tests miss a contract mismatch."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


SERVICE = '''import json


def response():
    return {"display_name": "Ada"}


if __name__ == "__main__":
    print(json.dumps(response()))
'''
CLIENT = '''import json
import sys


def render(payload):
    return "Hello, " + payload["label"]


if __name__ == "__main__":
    print(render(json.load(sys.stdin)))
'''
INTEGRATION = '''#!/usr/bin/env python3
"""Verify the actual clean service/client revisions, not stubbed contracts."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
revisions = {}
for name in ("service", "client"):
    repo = root / name
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=repo).strip():
        raise SystemExit(f"BLOCKED: {name} contains uncommitted changes")
    revisions[name] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()
print(json.dumps({"revisions": revisions}), flush=True)
response = subprocess.check_output([sys.executable, "service.py"], cwd=root / "service")
result = subprocess.run(
    [sys.executable, "client.py"], input=response, capture_output=True, cwd=root / "client"
)
if result.returncode or result.stdout != b"Hello, Ada\\n":
    print("FAIL: real response did not render Hello, Ada")
    print(result.stderr.decode(), end="")
    raise SystemExit(1)
print("PASS: real service response renders Hello, Ada")
'''


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo, text=True, stderr=subprocess.STDOUT
    ).strip()


def create_fixture(destination: Path) -> Path:
    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    for name, source, test in (
        ("service", SERVICE, 'from service import response\nassert response() == {"display_name": "Ada"}\n'),
        ("client", CLIENT, 'from client import render\nassert render({"label": "Ada"}) == "Hello, Ada"\n'),
    ):
        repo = destination / name
        repo.mkdir()
        (repo / f"{name}.py").write_text(source, encoding="utf-8")
        (repo / "check.py").write_text(test, encoding="utf-8")
        (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
        (repo / "AGENTS.md").write_text(
            "# Fixture instructions\n\nThis repository owns the " + name + " only.\n"
            "Run `python3 check.py` before handoff. Do not edit the sibling repo.\n"
            "Use the parent-approved shared contract; local stubs do not define it.\n",
            encoding="utf-8",
        )
        git(repo, "init", "-q", "-b", "main")
        git(repo, "config", "user.name", "Orchestra Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "add", "--", f"{name}.py", "check.py", ".gitignore", "AGENTS.md")
        git(repo, "commit", "-q", "-m", "test: seed independent project")
    (destination / "verify_integration.py").write_text(INTEGRATION, encoding="utf-8")
    (destination / "BRIEF.md").write_text(
        "# Shared fixture brief\n\n"
        "The agreed response field is `display_name`. The real client must render "
        "`Hello, Ada` from the service response. Local checks are mandatory but "
        "insufficient. Only the affected child should change.\n\n"
        "This is disposable evaluation data with no production, network or "
        "publication authority. The evaluation caller supplies any child/commit "
        "authority explicitly. Read both repositories' AGENTS.md separately.\n\n"
        "Prerequisite: Python 3 and Git. In each repo run `python3 check.py`. "
        "At this root run `python3 verify_integration.py`; it must initially "
        "fail despite green local checks. The command prints the actual clean "
        "revisions. No server, credentials or cleanup process is needed.\n",
        encoding="utf-8",
    )
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="new disposable directory")
    print(create_fixture(parser.parse_args().destination))
