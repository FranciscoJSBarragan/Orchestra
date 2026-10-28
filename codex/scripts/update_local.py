#!/usr/bin/env python3
"""Rebuild Orchestra into ROOT/current, keep the last build in ROOT/previous and reinstall it."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from package_plugin import ROOT as SOURCE, build_plugin

PLUGIN = "orchestra"


def run(*command: str, check: bool = True) -> str:
    return subprocess.run(command, check=check, capture_output=True, text=True).stdout


def promote(root: Path) -> None:
    current, previous, staging = root / "current", root / "previous", root / "next"
    if previous.exists():
        shutil.rmtree(previous)
    if current.exists():
        current.rename(previous)
    staging.rename(current)


def carry_over(root: Path, targets: list[str]) -> None:
    for target in targets:
        if (root / "current" / target).exists():
            shutil.copytree(root / "current" / target, root / "next" / target, symlinks=True)


def same_files(bundle: Path, installed: Path) -> bool:
    files = [path.relative_to(bundle) for path in bundle.rglob("*") if path.is_file()]
    return all((installed / name).is_file()
               and (installed / name).read_bytes() == (bundle / name).read_bytes() for name in files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="bundles folder holding current and previous")
    parser.add_argument("--claude", metavar="MARKETPLACE", help="Claude Code marketplace name")
    parser.add_argument("--codex", metavar="MARKETPLACE", help="Codex marketplace name")
    parser.add_argument("--cursor", action="store_true", help="copy into Cursor's local plugins folder")
    args = parser.parse_args()
    if not (args.claude or args.codex or args.cursor):
        parser.error("name at least one of --claude, --codex or --cursor")
    root = args.root.expanduser().absolute()
    version = json.loads((SOURCE / "packaging/orchestra/.codex-plugin/plugin.json").read_text())["version"]
    try:
        run(sys.executable, str(SOURCE / "codex/scripts/validate_suite.py"), "--full")
        staging = root / "next"
        if staging.exists():
            shutil.rmtree(staging)
        if args.claude:
            build_plugin(SOURCE, staging / "claude" / PLUGIN, "claude")
            catalog = {"name": args.claude, "owner": {"name": "Orchestra"},
                       "plugins": [{"name": PLUGIN, "source": f"./{PLUGIN}"}]}
            (staging / "claude/.claude-plugin").mkdir()
            (staging / "claude/.claude-plugin/marketplace.json").write_text(json.dumps(catalog, indent=2) + "\n")
        if args.codex:
            build_plugin(SOURCE, staging / "portable" / PLUGIN, "portable")
        if args.cursor:
            build_plugin(SOURCE, staging / "cursor" / PLUGIN, "cursor")
        targets = (("claude", args.claude), ("portable", args.codex), ("cursor", args.cursor))
        carry_over(root, [name for name, wanted in targets if not wanted])
        promote(root)
        installed: dict[Path, Path] = {}
        if args.claude:
            plugin = f"{PLUGIN}@{args.claude}"
            run("claude", "plugin", "marketplace", "update", args.claude)
            run("claude", "plugin", "uninstall", "--keep-data", plugin, check=False)
            run("claude", "plugin", "install", plugin)
            entry = next(item for item in json.loads(run("claude", "plugin", "list", "--json")) if item["id"] == plugin)
            installed[root / "current/claude" / PLUGIN] = Path(entry["installPath"])
        if args.codex:
            plugin = f"{PLUGIN}@{args.codex}"
            run("codex", "plugin", "remove", plugin, check=False)
            run("codex", "plugin", "add", plugin)
            codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
            installed[root / "current/portable" / PLUGIN] = codex_home / "plugins/cache" / args.codex / PLUGIN / version
        if args.cursor:
            local = Path.home() / ".cursor/plugins/local" / PLUGIN
            if local.exists():
                shutil.rmtree(local)
            shutil.copytree(root / "current/cursor" / PLUGIN, local)
            installed[root / "current/cursor" / PLUGIN] = local
    except (subprocess.CalledProcessError, StopIteration, ValueError, OSError) as exc:
        detail = getattr(exc, "stderr", None) or getattr(exc, "stdout", None) or exc
        print(f"error: {detail}", file=sys.stderr)
        return 1
    stale = [str(copy) for bundle, copy in installed.items() if not same_files(bundle, copy)]
    if stale:
        print(f"error: installed copy differs from {version}: {', '.join(stale)}", file=sys.stderr)
        return 1
    print(f"Installed {PLUGIN} {version}; previous build kept in {root / 'previous'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
