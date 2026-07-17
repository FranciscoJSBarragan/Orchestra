#!/usr/bin/env python3
"""Shared helpers for Orchestra git-helper scripts.

Only pieces whose duplicated variants are semantically identical across
consumers live here. Materially different variants stay local to their script.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess


SHA_PATTERN = re.compile(r"[0-9a-f]{40,64}\Z")


def _run(repo: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return _run(repo, ["git", *args])
