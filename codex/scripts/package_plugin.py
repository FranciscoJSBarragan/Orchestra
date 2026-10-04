#!/usr/bin/env python3
"""Build a self-contained plugin from Orchestra's canonical sources."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from sync import AGENTS, HELPERS, SKILLS

TARGETS = ("portable", "cursor", "grok", "devin", "claude")
ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_plugin(source: Path, output: Path, target: str) -> Path:
    """Output must be new; never overwrite an installation or user-owned files."""
    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    if output.name != "orchestra":
        raise ValueError("output directory must be named orchestra")
    if output.exists() or output.is_symlink():
        raise ValueError(f"output already exists: {output}; choose a new destination")
    metadata_path = source / "packaging/orchestra/.codex-plugin/plugin.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    files: list[tuple[Path, Path]] = []
    for skill in SKILLS:
        if not (source / "codex/skills" / skill / "SKILL.md").is_file():
            raise ValueError(f"missing skill: {skill}")
        for path in sorted((source / "codex/skills" / skill).rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                relative = path.relative_to(source / "codex/skills" / skill)
                files.append((path, Path("skills") / skill / relative))
    for helper in HELPERS:
        files.append((source / "codex/scripts" / helper, Path("scripts") / helper))
    for profile in AGENTS:
        filename = f"{profile}.toml"
        files.append((source / "codex/agents" / filename, Path("profiles") / filename))
    for host, matrix in (
        ("codex", "codex/config/roles.native.toml"),
        ("cursor", "hosts/cursor/config/roles.cursor.toml"),
        ("grok", "hosts/grok/config/roles.grok.toml"),
        ("devin", "hosts/devin/config/roles.devin.toml"),
        ("claude", "hosts/claude/config/roles.claude.toml"),
    ):
        files.append((source / matrix, Path("hosts") / host / "roles.toml"))
        if host != "codex":
            files.append((source / "hosts" / host / "references/spawn.md",
                          Path("hosts") / host / "spawn.md"))
    for original, destination in (
        ("docs/WORKFLOW.md", "WORKFLOW.md"),
        ("codex/config/execution-presets.toml", "execution-presets.toml"),
        ("LICENSE", "LICENSE"),
        ("packaging/README.md", "README.md"),
    ):
        files.append((source / original, Path(destination)))
    if target == "devin":
        for profile in AGENTS:
            files.append((source / "hosts/devin/agents" / f"{profile}.md",
                          Path("agents") / f"{profile}.md"))
    elif target == "claude":
        for path in sorted((source / "hosts/claude/agents").glob("orchestra_*.md")):
            files.append((path, Path("agents") / path.name))
        for name in ("hooks.json", "read_package.py"):
            files.append((source / "hosts/claude/plugin/hooks" / name, Path("hooks") / name))
    # Preflight every source before creating anything at the destination.
    for original, _ in files:
        if (not original.is_file() or original.is_symlink()
                or not original.resolve().is_relative_to(source.resolve())):
            raise ValueError(f"missing or unsafe package source: {original}")
    output.mkdir(parents=True)
    try:
        for original, relative in files:
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, destination)
        write_json(output / ".codex-plugin/plugin.json", metadata)
        common = {key: metadata[key] for key in (
            "name", "version", "description", "author", "license", "keywords",
        )}
        if target == "portable":
            write_json(output / "plugin.json", {"$schema": SCHEMA, **common})
        elif target == "cursor":
            write_json(output / ".cursor-plugin/plugin.json", {**common, "skills": "./skills/"})
        elif target == "devin":
            write_json(output / ".devin-plugin/plugin.json", {**common, "skills": "./skills/"})
        else:
            write_json(output / ".claude-plugin/plugin.json", common)
    except Exception:
        shutil.rmtree(output)
        raise
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=TARGETS, default="portable")
    parser.add_argument("--output", type=Path, required=True, help="new destination ending in /orchestra")
    args = parser.parse_args()
    try:
        path = build_plugin(ROOT, args.output.absolute(), args.target)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Built {args.target} plugin: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
