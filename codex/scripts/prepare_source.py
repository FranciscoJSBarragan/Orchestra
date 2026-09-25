from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile


DEFAULT_REPOSITORY = "https://github.com/FranciscoJSBarragan/Orchestra.git"


def git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise ValueError(
            f"git {arguments[0]} failed (exit {result.returncode}); "
            "check repository access, the full revision and the destination."
        )
    return result.stdout.strip()


def inspect_source(root: Path, revision: str) -> dict[str, str]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("destination must be a source directory, not a symlink")
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root.resolve():
        raise ValueError("destination must be the Git checkout root")
    if git(root, "rev-parse", "HEAD") != revision:
        raise ValueError("destination has a different revision; choose another path")
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("destination has local changes; preserve them and choose another path")
    for relative in (
        "docs/WORKFLOW.md",
        "codex/skills/orchestra/SKILL.md",
        "codex/skills/orchestra/runtime.md",
        "codex/scripts/delegate.py",
    ):
        resource = root / relative
        if not resource.is_file() or not resource.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"revision lacks a usable Orchestra resource: {relative}")
    return {
        "revision": revision,
        "source_root": str(root),
        "skills_root": str(root / "codex/skills"),
        "runtime_root": str(root / "codex"),
        "workflow": str(root / "docs/WORKFLOW.md"),
    }


def prepare_source(repository: str, revision: str, destination: Path) -> dict[str, str]:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", revision):
        raise ValueError("revision must be a full 40-character Git commit SHA")
    revision = revision.lower()
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        return inspect_source(destination, revision)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".orchestra-prepare-", dir=destination.parent) as temporary:
        staging = Path(temporary) / "source"
        staging.mkdir()
        git(staging, "init", "--quiet")
        git(staging, "remote", "add", "origin", repository)
        git(staging, "fetch", "--quiet", "--depth=1", "origin", revision)
        git(staging, "checkout", "--quiet", "--detach", revision)
        inspect_source(staging, revision)
        if destination.exists() or destination.is_symlink():
            raise ValueError("destination appeared during preparation; inspect it before retrying")
        staging.rename(destination)
    return inspect_source(destination, revision)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare or verify a pinned Orchestra source checkout.")
    parser.add_argument("--revision", required=True)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    arguments = parser.parse_args()
    try:
        result = prepare_source(arguments.repository, arguments.revision, arguments.destination)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
