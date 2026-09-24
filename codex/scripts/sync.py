#!/usr/bin/env python3
"""Synchronize the repository-owned Orchestra runtime into host user paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import tomllib
from typing import Any


SKILLS = (
    "orchestra",
    "orchestra-task",
    "orchestra-project-start",
    "orchestra-repo-onboard",
    "orchestra-delegate",
    "orchestra-lite",
    "orchestra-engineering",
    "orchestra-project-verification",
    "orchestra-coordinate",
    "orchestra-repo-maintenance",
    "orchestra-phase-commit",
    "orchestra-delivery-policy",
    "orchestra-pr-open",
    "orchestra-pr-review",
    "orchestra-pr-merge",
    "orchestra-local-integrate",
    "orchestra-role-analyst",
    "orchestra-role-implementer",
    "orchestra-role-reviewer",
    "orchestra-role-verifier",
)
AGENTS = (
    "orchestra_analyst",
    "orchestra_implementation_worker",
    "orchestra_reviewer",
    "orchestra_verifier",
)
LEGACY_AGENTS = (
    "analyst",
    "browser_acceptance_tester",
    "debugging_investigator",
    "frontend_implementation_worker",
    "implementation_worker",
    "phase_committer",
    "plan_scope_auditor",
    "planner",
    "pr_polling_specialist",
    "pr_triage_specialist",
    "repo_context_explorer",
    "reviewer",
    "verifier",
    "web_researcher",
)
HELPERS = (
    "coordination.py",
    "task_state.py",
    "task_control.py",
    "task_mcp.py",
    "commit_phase.py",
    "delegate.py",
    "adopt_worktree.py",
    "policy.py",
    "pr.py",
    "integrate_local.py",
    "_common.py",
)
RETIRED_HELPERS = ("create_worktree.py", "session_model.py")
MODELCONFIGS = ("native",)
# Accepted only as ownership metadata for migration and uninstall.
LEGACY_MODELCONFIGS = ("external", "dual")
HOSTS = ("codex", "cursor", "grok", "devin", "all")
HOST_SCOPES = ("codex", "cursor", "grok", "devin")
ENTRY_SCOPES = ("shared", *HOST_SCOPES)
CHECKOUT_MODES = ("managed", "hybrid")
CURSOR_PLUGIN_ROOT = ".cursor/plugins/local/orchestra"
DEVIN_CONFIG_PATH = ".config/devin/config.json"
DEVIN_AGENTS_DIR = ".config/devin/agents"
DEVIN_SKILLS_DIR = ".config/devin/skills"
DEVIN_IDENTITY_SCRIPT = "hosts/devin/session_identity.py"
START = b"<!-- orchestra:start -->"
END = b"<!-- orchestra:end -->"
CONFIG_START = b"# orchestra-worktree-root:start"
CONFIG_END = b"# orchestra-worktree-root:end"
MANIFEST_PATH = "orchestra/install-manifest.json"
ORCHESTRA_MANIFEST_PATH = "install-manifest.json"
MANIFEST_SCHEMA_VERSION = 2
WORKTREE_ROOT_PATH = "orchestra/worktree-root"
CHECKOUT_MODE_PATH = "orchestra/checkout-mode"
ORCHESTRA_WORKTREE_ROOT_PATH = "worktree-root"
ORCHESTRA_CHECKOUT_MODE_PATH = "checkout-mode"
RETIRED_RULES_PATHS = ("rules/orchestra.rules",)
CACHE_TOOLS = ("poetry", "pip", "uv", "npm")
PERMISSION_BACKENDS = ("profile", "legacy")
PERMISSION_PROFILE = ":workspace"
RETIRED_PERMISSION_PROFILE = "orchestra-workspace"
GUARDIAN_MIN_VERSION = (0, 146, 0)
KNOWN_LEGACY_SANDBOX_KEYS = {
    "exclude_slash_tmp",
    "exclude_tmpdir_env_var",
    "network_access",
    "writable_roots",
}


class SyncError(Exception):
    """An unsafe or invalid synchronization state."""


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _result(
    status: str,
    action: str,
    changes: list[dict[str, str]],
    detail: str = "",
    *,
    modelconfig: str | None = None,
    checkout_mode: str | None = None,
    worktree_root: Path | None = None,
    sandbox_root: Path | None = None,
    cache_roots: dict[str, Path] | None = None,
    omitted_cache_tools: dict[str, str] | None = None,
    unconfigured_cache_tools: list[str] | None = None,
    restart_required: bool = False,
    codex_version: str | None = None,
    permission_backend: str | None = None,
    permission_profile: str | None = None,
    profile_configured: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"action": action, "changes": changes, "status": status}
    if detail:
        payload["detail"] = detail
    if modelconfig is not None:
        payload["modelconfig"] = modelconfig
    if checkout_mode is not None:
        payload["checkout_mode"] = checkout_mode
    if worktree_root is not None:
        payload["worktree_root"] = str(worktree_root)
    if sandbox_root is not None:
        payload["sandbox_root"] = str(sandbox_root)
    if cache_roots is not None:
        payload["cache_roots"] = {
            tool: str(cache_roots[tool]) for tool in sorted(cache_roots)
        }
    if omitted_cache_tools is not None:
        payload["omitted_cache_tools"] = {
            tool: omitted_cache_tools[tool] for tool in sorted(omitted_cache_tools)
        }
    if unconfigured_cache_tools is not None:
        payload["unconfigured_cache_tools"] = sorted(unconfigured_cache_tools)
    payload["restart_required"] = restart_required
    if codex_version is not None:
        payload["codex_version"] = codex_version
    if permission_backend is not None:
        payload["permission_backend"] = permission_backend
    payload["permission_profile"] = permission_profile
    payload["profile_configured"] = profile_configured
    return payload


def _orchestra_root(home: Path) -> Path:
    return Path(os.path.abspath(home / ".orchestra"))


def _orchestra_home(home: Path) -> Path:
    configured = os.environ.get("ORCHESTRA_HOME")
    if configured:
        return Path(os.path.abspath(configured))
    return _orchestra_root(home)


def _includes_codex(host: str) -> bool:
    return host in {"codex", "all"}


def _includes_cursor(host: str) -> bool:
    return host in {"cursor", "all"}


def _includes_grok(host: str) -> bool:
    return host in {"grok", "all"}


def _includes_devin(host: str) -> bool:
    return host in {"devin", "all"}


def _cursor_mcp_json(orchestra_home: Path) -> bytes:
    helper = orchestra_home / "scripts" / "task_mcp.py"
    payload = {
        "mcpServers": {
            "orchestra_tasks": {
                "command": "python3",
                "args": [str(helper)],
            }
        }
    }
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def _devin_hook_matcher(orchestra_home: Path) -> dict[str, Any]:
    script = orchestra_home / "hosts" / "devin" / "session_identity.py"
    return {
        "matcher": "",
        "hooks": [
            {
                "type": "command",
                "command": f'python3 "{script}"',
                "timeout": 10,
            }
        ],
    }


def _devin_canonical_matcher_bytes(matcher: dict[str, Any]) -> bytes:
    return (json.dumps(matcher, indent=2, sort_keys=True) + "\n").encode()


def _devin_managed_content(orchestra_home: Path) -> bytes:
    return _devin_canonical_matcher_bytes(_devin_hook_matcher(orchestra_home))


def _devin_parse_config(data: bytes) -> dict[str, Any]:
    if not data:
        return {}
    try:
        parsed = json.loads(data.decode())
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SyncError(f"invalid Devin config.json: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SyncError("invalid Devin config.json structure")
    return parsed


def _devin_render(parsed: dict[str, Any]) -> bytes:
    return (json.dumps(parsed, indent=2, ensure_ascii=False) + "\n").encode()


def _devin_matcher_command(matcher: dict[str, Any]) -> str | None:
    hook_list = matcher.get("hooks")
    if not isinstance(hook_list, list):
        return None
    for hook in hook_list:
        if (
            isinstance(hook, dict)
            and isinstance(hook.get("command"), str)
            and DEVIN_IDENTITY_SCRIPT in hook["command"]
        ):
            return hook["command"]
    return None


def _devin_find_matchers(parsed: dict[str, Any]) -> list[int]:
    hooks = parsed.get("hooks")
    if not isinstance(hooks, dict):
        return []
    session_start = hooks.get("SessionStart")
    if not isinstance(session_start, list):
        return []
    return [
        index
        for index, matcher in enumerate(session_start)
        if isinstance(matcher, dict) and _devin_matcher_command(matcher) is not None
    ]


def _devin_strip_matcher(parsed: dict[str, Any]) -> dict[str, Any]:
    indices = _devin_find_matchers(parsed)
    if not indices:
        return parsed
    session_start = parsed["hooks"]["SessionStart"]
    for index in reversed(indices):
        del session_start[index]
    if not session_start:
        del parsed["hooks"]["SessionStart"]
    if not parsed["hooks"]:
        del parsed["hooks"]
    return parsed


def _devin_validate_hooks_shape(parsed: dict[str, Any], label: str) -> None:
    hooks = parsed.get("hooks")
    if hooks is not None and not isinstance(hooks, dict):
        raise SyncError(f"hooks must be an object in {label}")
    if isinstance(hooks, dict):
        session_start = hooks.get("SessionStart")
        if session_start is not None and not isinstance(session_start, list):
            raise SyncError(f"hooks.SessionStart must be an array in {label}")


def _detect_codex_version() -> tuple[str, tuple[int, int, int]]:
    executable = shutil.which("codex")
    if executable is None:
        raise SyncError("Codex CLI is unavailable; cannot select a permission backend")
    try:
        completed = subprocess.run(
            [executable, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SyncError("Codex version detection failed") from exc
    output = completed.stdout.strip()
    match = re.search(r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?!\d)", output)
    if completed.returncode != 0 or match is None:
        raise SyncError("Codex returned an unsupported or unreadable version")
    version = tuple(int(part) for part in match.groups())
    return ".".join(match.groups()), version


def _permission_backend(version: tuple[int, int, int]) -> str:
    if version < GUARDIAN_MIN_VERSION:
        required = ".".join(str(part) for part in GUARDIAN_MIN_VERSION)
        current = ".".join(str(part) for part in version)
        raise SyncError(
            f"Codex {required} or later is required for Orchestra Guardian "
            f"permissions; found {current}"
        )
    return "profile"


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _validate_cache_root(home: Path, value: str) -> Path:
    if not value or "\n" in value or "\r" in value:
        raise SyncError("cache command returned an invalid path")
    candidate = Path(value)
    if not candidate.is_absolute():
        raise SyncError("cache command returned a non-absolute path")

    normalized_home = Path(os.path.abspath(home))
    normalized = Path(os.path.abspath(candidate))
    if normalized == Path("/"):
        raise SyncError("cache path is too broad")

    resolved_home = normalized_home.resolve(strict=False)
    resolved = normalized.resolve(strict=False)
    if resolved == resolved_home:
        raise SyncError("cache path is too broad")
    if not _is_within(resolved, resolved_home):
        raise SyncError("cache path resolves outside the user home")
    normalized = normalized_home / resolved.relative_to(resolved_home)

    blocked_trees = (
        normalized_home / ".ssh",
        normalized_home / ".codex",
        normalized_home / ".docker",
        normalized_home / ".config",
        normalized_home / "Library" / "Containers",
        normalized_home / "Library" / "Application Support",
    )
    if any(_is_within(normalized, blocked) for blocked in blocked_trees):
        raise SyncError("cache path is inside a sensitive directory")
    if normalized in {
        normalized_home / ".cache",
        normalized_home / "Library" / "Caches",
    }:
        raise SyncError("cache path is an overly broad cache parent")
    return normalized


def _discover_cache_roots(home: Path) -> tuple[dict[str, Path], dict[str, str]]:
    commands: dict[str, tuple[str | None, list[str]]] = {
        "poetry": ("poetry", ["poetry", "config", "cache-dir"]),
        "pip": (None, [sys.executable, "-m", "pip", "cache", "dir"]),
        "uv": ("uv", ["uv", "cache", "dir"]),
        "npm": ("npm", ["npm", "config", "get", "cache"]),
    }
    discovered: dict[str, Path] = {}
    omitted: dict[str, str] = {}

    with tempfile.TemporaryDirectory(prefix="orchestra-cache-discovery-") as temporary:
        temporary_root = Path(temporary).resolve()
        temporary_path = str(temporary_root)
        query_home = home
        if not home.exists():
            query_home = temporary_root / "home"
            query_home.mkdir()
        elif not home.is_dir():
            return (
                discovered,
                {tool: "home directory unavailable" for tool in CACHE_TOOLS},
            )
        environment = dict(os.environ)
        environment.update(
            {
                "HOME": str(query_home),
                "TMPDIR": temporary_path,
                "TEMP": temporary_path,
                "TMP": temporary_path,
            }
        )
        for tool in CACHE_TOOLS:
            executable, command = commands[tool]
            if executable is not None and shutil.which(executable) is None:
                omitted[tool] = "not installed"
                continue
            reported_home = query_home
            try:
                completed = subprocess.run(
                    command,
                    cwd=temporary_path,
                    env=environment,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            except (OSError, subprocess.TimeoutExpired):
                omitted[tool] = "cache query failed"
                continue
            lines = [
                line.strip()
                for line in completed.stdout.splitlines()
                if line.strip()
            ]
            if tool == "pip" and (
                completed.returncode != 0 or len(lines) != 1
            ):
                fallback_home = temporary_root / "pip-home"
                fallback_home.mkdir()
                fallback_environment = dict(environment)
                fallback_environment["HOME"] = str(fallback_home)
                try:
                    completed = subprocess.run(
                        command,
                        cwd=temporary_path,
                        env=fallback_environment,
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                except (OSError, subprocess.TimeoutExpired):
                    omitted[tool] = "cache query failed"
                    continue
                lines = [
                    line.strip()
                    for line in completed.stdout.splitlines()
                    if line.strip()
                ]
                reported_home = fallback_home
            if completed.returncode != 0 or len(lines) != 1:
                omitted[tool] = "cache query failed"
                continue
            try:
                reported = Path(lines[0])
                if reported_home != home:
                    try:
                        reported = home / reported.relative_to(reported_home)
                    except ValueError:
                        pass
                discovered[tool] = _validate_cache_root(home, str(reported))
            except SyncError:
                omitted[tool] = "unsafe or invalid cache path"
    return discovered, omitted


def _minimal_writable_roots(
    orchestra_root: Path,
    worktree_root: Path,
    cache_roots: dict[str, Path],
) -> list[Path]:
    candidates = [
        orchestra_root,
        worktree_root,
        *(cache_roots[tool] for tool in sorted(cache_roots)),
    ]
    result: list[Path] = []
    for candidate in candidates:
        if any(_is_within(candidate, existing) for existing in result):
            continue
        result = [
            existing for existing in result if not _is_within(existing, candidate)
        ]
        result.append(candidate)
    return result


def _resolve_worktree_root(home: Path, explicit: Path | str | None) -> Path:
    raw = explicit
    if raw is None:
        raw = os.environ.get("ORCHESTRA_WORKTREE_ROOT")
    if raw is None:
        return Path(os.path.abspath(home / ".orchestra" / "worktrees"))
    value = str(raw)
    if not value:
        raise SyncError("worktree root must not be empty")
    if value == "~":
        candidate = home
    elif value.startswith("~/"):
        candidate = home / value[2:]
    elif value.startswith("~"):
        raise SyncError("worktree root must not use another user's home")
    else:
        candidate = Path(value)
    if not candidate.is_absolute():
        raise SyncError("worktree root must be absolute")
    resolved = Path(os.path.abspath(candidate))
    if resolved == Path("/") or resolved == Path(os.path.abspath(home)):
        raise SyncError("worktree root must be a dedicated directory below the user home")
    if resolved.exists() and resolved.is_symlink():
        raise SyncError("worktree root must not be a symlink")
    return resolved


def _relative(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or path.as_posix() != value:
        raise SyncError(f"invalid relative path: {value!r}")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise SyncError(f"unsafe relative path: {value!r}")
    return path


def _safe_path(root: Path, relative: str, *, allow_missing: bool = True) -> Path:
    rel = _relative(relative)
    current = root
    if current.is_symlink():
        raise SyncError(f"destination root is a symlink: {root}")
    if current.exists() and not current.is_dir():
        raise SyncError(f"destination root is not a directory: {root}")
    for index, part in enumerate(rel.parts):
        current = current / part
        if current.is_symlink():
            raise SyncError(f"destination path uses a symlink: {relative}")
        if current.exists() and index < len(rel.parts) - 1 and not current.is_dir():
            raise SyncError(f"destination parent is not a directory: {relative}")
        if not current.exists():
            if allow_missing:
                continue
            raise SyncError(f"destination is missing: {relative}")
    return current


def _manifest_file(codex_home: Path, orchestra_home: Path, host: str = "all") -> Path:
    _ = codex_home, host
    return _safe_path(orchestra_home, ORCHESTRA_MANIFEST_PATH)


def _legacy_manifest_file(codex_home: Path) -> Path:
    return _safe_path(codex_home, MANIFEST_PATH)


def _read_file(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise SyncError(f"expected a regular file: {label}")
    return path.read_bytes()


def _walk_files(directory: Path) -> list[Path]:
    if directory.is_symlink() or not directory.is_dir():
        raise SyncError(f"expected a source directory: {directory}")
    files: list[Path] = []
    for child in sorted(directory.iterdir(), key=lambda item: item.name):
        if child.is_symlink():
            raise SyncError(f"source symlink is not allowed: {child}")
        if child.is_dir():
            files.extend(_walk_files(child))
        elif child.is_file():
            files.append(child)
        else:
            raise SyncError(f"source entry is not a regular file: {child}")
    return files


def _entry_scope(root: str, path: str) -> str:
    parts = _relative(path).parts
    if root == "codex_home":
        return "codex"
    if root == "home" and parts[:2] == (".cursor", "plugins"):
        return "cursor"
    if root == "home" and parts[:2] == (".config", "devin"):
        return "devin"
    if root == "orchestra_home" and parts[:2] == ("hosts", "cursor"):
        return "cursor"
    if root == "orchestra_home" and parts[:2] == ("hosts", "grok"):
        return "grok"
    if root == "orchestra_home" and parts[:2] == ("hosts", "devin"):
        return "devin"
    return "shared"


def _entry(root: str, path: str, kind: str, content: bytes) -> dict[str, Any]:
    return {
        "root": root,
        "path": path,
        "type": kind,
        "scope": _entry_scope(root, path),
        "content": content,
    }


def _roles_content(source_root: Path) -> bytes:
    source = source_root / "codex/config/roles.native.toml"
    return _read_file(source, str(source))


def _inventory(
    source_root: Path,
    modelconfig: str | None,
    checkout_mode: str,
    worktree_root: Path,
    host: str,
    orchestra_home: Path,
) -> dict[tuple[str, str], dict[str, Any]]:
    if host not in HOSTS:
        raise SyncError(f"unknown host: {host}")
    if checkout_mode not in CHECKOUT_MODES:
        raise SyncError(f"unknown checkout mode: {checkout_mode}")
    if _includes_codex(host) and modelconfig not in MODELCONFIGS:
        raise SyncError(f"unknown model configuration: {modelconfig}")
    entries: dict[tuple[str, str], dict[str, Any]] = {}
    skill_root = source_root / "codex" / "skills"
    if skill_root.is_symlink() or not skill_root.is_dir():
        raise SyncError(f"expected a source directory: {skill_root}")
    actual_skills = []
    for child in sorted(skill_root.iterdir(), key=lambda item: item.name):
        if child.is_symlink() or not child.is_dir():
            raise SyncError(f"unexpected skill source entry: {child}")
        actual_skills.append(child.name)
    if tuple(actual_skills) != tuple(sorted(SKILLS)):
        raise SyncError("skill source inventory does not match the supported skills")
    for skill in SKILLS:
        directory = skill_root / skill
        for source in _walk_files(directory):
            relative = source.relative_to(directory).as_posix()
            destination = f".agents/skills/{skill}/{relative}"
            entries[("home", destination)] = _entry(
                "home", destination, "file", _read_file(source, str(source))
            )

    for helper in HELPERS:
        source = source_root / "codex/scripts" / helper
        destination = f"scripts/{helper}"
        entries[("orchestra_home", destination)] = _entry(
            "orchestra_home", destination, "file", _read_file(source, str(source))
        )
    control_root = source_root / "codex" / "control"
    if control_root.is_symlink() or not control_root.is_dir():
        raise SyncError(f"expected a source directory: {control_root}")
    for source in _walk_files(control_root):
        relative = source.relative_to(control_root).as_posix()
        if "__pycache__" in source.relative_to(control_root).parts or source.suffix == ".pyc":
            continue
        destination = f"control/{relative}"
        entries[("orchestra_home", destination)] = _entry(
            "orchestra_home", destination, "file", _read_file(source, str(source))
        )
    workflow_source = source_root / "docs/WORKFLOW.md"
    preset_source = source_root / "codex/config/execution-presets.toml"
    preset_content = _read_file(preset_source, str(preset_source))
    entries[("orchestra_home", "execution-presets.toml")] = _entry(
        "orchestra_home", "execution-presets.toml", "file", preset_content
    )
    entries[("orchestra_home", "WORKFLOW.md")] = _entry(
        "orchestra_home",
        "WORKFLOW.md",
        "file",
        _read_file(workflow_source, str(workflow_source)),
    )
    entries[("orchestra_home", ORCHESTRA_WORKTREE_ROOT_PATH)] = _entry(
        "orchestra_home",
        ORCHESTRA_WORKTREE_ROOT_PATH,
        "file",
        f"{worktree_root}\n".encode(),
    )
    entries[("orchestra_home", ORCHESTRA_CHECKOUT_MODE_PATH)] = _entry(
        "orchestra_home",
        ORCHESTRA_CHECKOUT_MODE_PATH,
        "file",
        f"{checkout_mode}\n".encode(),
    )

    if _includes_codex(host):
        entries[("codex_home", "orchestra/execution-presets.toml")] = _entry(
            "codex_home", "orchestra/execution-presets.toml", "file", preset_content
        )
        agent_dir = source_root / "codex" / "agents"
        actual_agents = []
        if agent_dir.is_symlink() or not agent_dir.is_dir():
            raise SyncError(f"expected a source directory: {agent_dir}")
        for child in sorted(agent_dir.iterdir(), key=lambda item: item.name):
            if child.is_symlink() or not child.is_file() or child.suffix != ".toml":
                raise SyncError(f"unexpected agent source entry: {child}")
            actual_agents.append(child.stem)
        if tuple(actual_agents) != AGENTS:
            raise SyncError(
                "agent source inventory does not match the four supported profiles"
            )
        for name in AGENTS:
            source = agent_dir / f"{name}.toml"
            destination = f"agents/{name}.toml"
            entries[("codex_home", destination)] = _entry(
                "codex_home", destination, "file", _read_file(source, str(source))
            )

        assert modelconfig is not None
        entries[("codex_home", "orchestra/roles.toml")] = _entry(
            "codex_home",
            "orchestra/roles.toml",
            "file",
            _roles_content(source_root),
        )
        for helper in HELPERS:
            source = source_root / "codex/scripts" / helper
            destination = f"orchestra/scripts/{helper}"
            entries[("codex_home", destination)] = _entry(
                "codex_home", destination, "file", _read_file(source, str(source))
            )
        for source in _walk_files(control_root):
            relative = source.relative_to(control_root).as_posix()
            if "__pycache__" in source.relative_to(control_root).parts or source.suffix == ".pyc":
                continue
            destination = f"orchestra/control/{relative}"
            entries[("codex_home", destination)] = _entry(
                "codex_home", destination, "file", _read_file(source, str(source))
            )
        entries[("codex_home", WORKTREE_ROOT_PATH)] = _entry(
            "codex_home", WORKTREE_ROOT_PATH, "file", f"{worktree_root}\n".encode()
        )
        entries[("codex_home", CHECKOUT_MODE_PATH)] = _entry(
            "codex_home", CHECKOUT_MODE_PATH, "file", f"{checkout_mode}\n".encode()
        )

        block_source = source_root / "codex/runtime/AGENTS.orchestra.md"
        block = _read_file(block_source, str(block_source))
        span = _block_span(block)
        if span != (0, len(block)):
            raise SyncError("runtime AGENTS source must contain exactly the managed block")
        entries[("codex_home", "AGENTS.md")] = _entry(
            "codex_home", "AGENTS.md", "managed_block", block
        )

    if _includes_cursor(host):
        cursor_roles = source_root / "hosts/cursor/config/roles.cursor.toml"
        cursor_spawn = source_root / "hosts/cursor/references/spawn.md"
        plugin_root = source_root / "hosts/cursor/plugin"
        for source, destination in (
            (cursor_roles, "hosts/cursor/roles.toml"),
            (cursor_spawn, "hosts/cursor/spawn.md"),
        ):
            entries[("orchestra_home", destination)] = _entry(
                "orchestra_home",
                destination,
                "file",
                _read_file(source, str(source)),
            )
        for source in _walk_files(plugin_root):
            relative = source.relative_to(plugin_root).as_posix()
            destination = f"{CURSOR_PLUGIN_ROOT}/{relative}"
            entries[("home", destination)] = _entry(
                "home", destination, "file", _read_file(source, str(source))
            )
        mcp_destination = f"{CURSOR_PLUGIN_ROOT}/mcp.json"
        entries[("home", mcp_destination)] = _entry(
            "home",
            mcp_destination,
            "file",
            _cursor_mcp_json(orchestra_home),
        )
    if _includes_grok(host):
        grok_roles = source_root / "hosts/grok/config/roles.grok.toml"
        grok_spawn = source_root / "hosts/grok/references/spawn.md"
        for source, destination in (
            (grok_roles, "hosts/grok/roles.toml"),
            (grok_spawn, "hosts/grok/spawn.md"),
        ):
            entries[("orchestra_home", destination)] = _entry(
                "orchestra_home",
                destination,
                "file",
                _read_file(source, str(source)),
            )
    if _includes_devin(host):
        devin_roles = source_root / "hosts/devin/config/roles.devin.toml"
        devin_spawn = source_root / "hosts/devin/references/spawn.md"
        devin_identity = source_root / "hosts/devin/plugin/scripts/session_identity.py"
        for source, destination in (
            (devin_roles, "hosts/devin/roles.toml"),
            (devin_spawn, "hosts/devin/spawn.md"),
            (devin_identity, "hosts/devin/session_identity.py"),
        ):
            entries[("orchestra_home", destination)] = _entry(
                "orchestra_home",
                destination,
                "file",
                _read_file(source, str(source)),
            )
        devin_agents_dir = source_root / "hosts/devin/agents"
        if devin_agents_dir.is_symlink() or not devin_agents_dir.is_dir():
            raise SyncError(f"expected a source directory: {devin_agents_dir}")
        actual_devin_agents = []
        for child in sorted(devin_agents_dir.iterdir(), key=lambda item: item.name):
            if child.is_symlink() or not child.is_file() or child.suffix != ".md":
                raise SyncError(f"unexpected agent source entry: {child}")
            actual_devin_agents.append(child.stem)
        if tuple(actual_devin_agents) != AGENTS:
            raise SyncError(
                "Devin agent source inventory does not match the four supported profiles"
            )
        for name in AGENTS:
            source = devin_agents_dir / f"{name}.md"
            destination = f"{DEVIN_AGENTS_DIR}/{name}.md"
            entries[("home", destination)] = _entry(
                "home", destination, "file", _read_file(source, str(source))
            )
        for skill in SKILLS:
            directory = skill_root / skill
            for source in _walk_files(directory):
                relative = source.relative_to(directory).as_posix()
                destination = f"{DEVIN_SKILLS_DIR}/{skill}/{relative}"
                entries[("home", destination)] = _entry(
                    "home", destination, "file", _read_file(source, str(source))
                )
        entries[("home", DEVIN_CONFIG_PATH)] = _entry(
            "home",
            DEVIN_CONFIG_PATH,
            "managed_json",
            _devin_managed_content(orchestra_home),
        )
    return entries


def _allowed_entry(root: str, path: str, kind: str) -> bool:
    parts = _relative(path).parts
    if root == "home" and kind == "file":
        if len(parts) >= 4 and parts[:2] == (".agents", "skills") and parts[2] in SKILLS:
            return True
        if (
            len(parts) >= 4
            and parts[:3] == (".config", "devin", "skills")
            and parts[3] in SKILLS
        ):
            return True
        if (
            len(parts) == 4
            and parts[:3] == (".config", "devin", "agents")
            and parts[3].startswith("orchestra_")
            and parts[3].endswith(".md")
        ):
            return True
        plugin_parts = Path(CURSOR_PLUGIN_ROOT).parts
        return (
            len(parts) >= len(plugin_parts) + 1
            and parts[: len(plugin_parts)] == plugin_parts
        )
    if root == "home" and kind == "managed_json":
        return path == DEVIN_CONFIG_PATH
    if root == "orchestra_home" and kind == "file":
        return path in {
            ORCHESTRA_WORKTREE_ROOT_PATH,
            ORCHESTRA_CHECKOUT_MODE_PATH,
            "WORKFLOW.md",
            "execution-presets.toml",
            "hosts/cursor/roles.toml",
            "hosts/cursor/spawn.md",
            "hosts/grok/roles.toml",
            "hosts/grok/spawn.md",
            "hosts/devin/roles.toml",
            "hosts/devin/spawn.md",
            "hosts/devin/session_identity.py",
        } or path in {f"scripts/{name}" for name in (*HELPERS, *RETIRED_HELPERS)} or (
            len(parts) >= 2 and parts[0] == "control"
        )
    if root != "codex_home":
        return False
    if kind == "managed_block":
        return path == "AGENTS.md"
    if kind == "managed_config":
        return path == "config.toml"
    if kind != "file":
        return False
    if len(parts) == 2 and parts[0] == "agents":
        allowed_agents = {*AGENTS, *LEGACY_AGENTS}
        return parts[1] in {f"{name}.toml" for name in allowed_agents}
    return (
        path
        in {
            "orchestra/roles.toml",
            "orchestra/execution-presets.toml",
            WORKTREE_ROOT_PATH,
            CHECKOUT_MODE_PATH,
            *RETIRED_RULES_PATHS,
        }
        or path
        in {
            f"orchestra/scripts/{name}"
            for name in (*HELPERS, *RETIRED_HELPERS)
        }
        or (len(parts) >= 3 and parts[:2] == ("orchestra", "control"))
    )


def _backup_path(root: str, path: str) -> str:
    return f"orchestra/backups/{root}/{path}"


def _backup_root_name(entry: dict[str, Any]) -> str:
    configured = entry.get("backup_root")
    if configured in {"codex_home", "orchestra_home"}:
        return str(configured)
    return "codex_home" if entry["scope"] == "codex" else "orchestra_home"


def _manifest_entry(
    entry: dict[str, Any],
    backup: str | None = None,
    backup_root: str | None = None,
) -> dict[str, str]:
    result = {
        "digest": _digest(entry["content"]),
        "path": entry["path"],
        "root": entry["root"],
        "scope": entry["scope"],
        "type": entry["type"],
    }
    if backup is not None:
        result["backup"] = backup
        result["backup_root"] = backup_root or (
            "codex_home" if entry["scope"] == "codex" else "orchestra_home"
        )
    return result


def _read_manifest(
    path: Path,
    *,
    default_backup_root: str,
) -> dict[str, Any]:
    data = _read_file(path, str(path))

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise SyncError(f"duplicate install manifest field: {key}")
            result[key] = value
        return result

    try:
        payload = json.loads(data, object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SyncError(f"invalid install manifest: {exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("entries"), list):
        raise SyncError("invalid install manifest structure")
    modern = "schema_version" in payload
    allowed_fields = {
        "schema_version",
        "installed_hosts",
        "entries",
        "modelconfig",
        "checkout_mode",
        "permission_backend",
    }
    if set(payload) - allowed_fields:
        raise SyncError("invalid install manifest structure")
    if modern and payload.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise SyncError("unsupported install manifest schema version")
    if modern:
        raw_hosts = payload.get("installed_hosts")
        if (
            not isinstance(raw_hosts, list)
            or any(host not in HOST_SCOPES for host in raw_hosts)
            or len(set(raw_hosts)) != len(raw_hosts)
        ):
            raise SyncError("invalid install manifest installed_hosts")
        installed_hosts = set(raw_hosts)
    else:
        installed_hosts: set[str] = set()
    modelconfig = payload.get("modelconfig")
    if modelconfig is not None and modelconfig not in (*MODELCONFIGS, *LEGACY_MODELCONFIGS):
        raise SyncError("invalid install manifest modelconfig")
    checkout_mode = payload.get("checkout_mode")
    if checkout_mode is not None and checkout_mode not in CHECKOUT_MODES:
        raise SyncError("invalid install manifest checkout mode")
    permission_backend = payload.get("permission_backend")
    if permission_backend is not None and permission_backend not in PERMISSION_BACKENDS:
        raise SyncError("invalid install manifest permission backend")
    entries: dict[tuple[str, str], dict[str, str]] = {}
    for raw in payload["entries"]:
        if not isinstance(raw, dict):
            raise SyncError("invalid install manifest entry")
        required = {"digest", "path", "root", "type"}
        optional = {"backup"}
        if modern:
            required.add("scope")
            optional.add("backup_root")
        if not required <= set(raw) or set(raw) - (required | optional):
            raise SyncError("invalid install manifest entry fields")
        if any(not isinstance(raw[name], str) for name in raw):
            raise SyncError("install manifest values must be strings")
        if len(raw["digest"]) != 64 or any(
            char not in "0123456789abcdef" for char in raw["digest"]
        ):
            raise SyncError("invalid install manifest digest")
        if not _allowed_entry(raw["root"], raw["path"], raw["type"]):
            raise SyncError(
                f"install manifest contains an unauthorized destination: {raw['path']}"
            )
        entry = dict(raw)
        inferred_scope = _entry_scope(entry["root"], entry["path"])
        if modern and entry["scope"] != inferred_scope:
            raise SyncError(f"invalid install scope for {entry['path']}")
        entry["scope"] = inferred_scope
        if entry.get("backup"):
            expected = _backup_path(entry["root"], entry["path"])
            if entry["backup"] != expected:
                raise SyncError(f"invalid backup reference for {entry['path']}")
            entry["backup_root"] = entry.get("backup_root", default_backup_root)
            if entry["backup_root"] not in {"codex_home", "orchestra_home"}:
                raise SyncError(f"invalid backup root for {entry['path']}")
        elif "backup_root" in entry:
            raise SyncError(f"backup root without backup for {entry['path']}")
        key = (entry["root"], entry["path"])
        if key in entries:
            raise SyncError(f"duplicate install manifest destination: {entry['path']}")
        entries[key] = entry
        if entry["scope"] in HOST_SCOPES:
            installed_hosts.add(entry["scope"])
    if modern and any(
        entry["scope"] in HOST_SCOPES and entry["scope"] not in installed_hosts
        for entry in entries.values()
    ):
        raise SyncError("install manifest entries exceed installed_hosts")
    return {
        "entries": entries,
        "installed_hosts": installed_hosts,
        "modelconfig": modelconfig,
        "checkout_mode": checkout_mode,
        "permission_backend": permission_backend,
        "modern": modern,
    }


def _load_install_state(
    codex_home: Path,
    orchestra_home: Path,
) -> dict[str, Any]:
    canonical = _manifest_file(codex_home, orchestra_home)
    legacy = _legacy_manifest_file(codex_home)
    candidates: list[tuple[Path, str]] = []
    if canonical.exists():
        candidates.append((canonical, "orchestra_home"))
    if legacy != canonical and legacy.exists():
        candidates.append((legacy, "codex_home"))
    merged: dict[tuple[str, str], dict[str, str]] = {}
    installed_hosts: set[str] = set()
    auxiliary_drift: list[str] = []
    metadata: dict[str, str | None] = {
        "modelconfig": None,
        "checkout_mode": None,
        "permission_backend": None,
    }
    migration_pending = False
    for path, default_backup_root in candidates:
        parsed = _read_manifest(path, default_backup_root=default_backup_root)
        migration_pending = migration_pending or not parsed["modern"] or path == legacy
        installed_hosts.update(parsed["installed_hosts"])
        if not parsed["installed_hosts"] and parsed["entries"]:
            installed_hosts.add("codex" if path == legacy else "cursor")
        for name in metadata:
            value = parsed[name]
            if value is None:
                continue
            if metadata[name] is not None and metadata[name] != value:
                raise SyncError(f"conflicting install manifest {name}")
            metadata[name] = value
        for key, entry in parsed["entries"].items():
            existing = merged.get(key)
            if existing is not None and existing != entry:
                raise SyncError(
                    f"conflicting install manifest destination: {entry['path']}"
                )
            merged[key] = entry
    roots = {"codex_home": codex_home, "orchestra_home": orchestra_home}
    for entry in merged.values():
        backup_rel = entry.get("backup")
        if not backup_rel:
            continue
        backup = _safe_path(roots[entry["backup_root"]], backup_rel)
        if not backup.exists():
            auxiliary_drift.append(f"referenced backup is missing: {backup_rel}")
        elif not backup.is_file():
            raise SyncError(f"referenced backup is not a regular file: {backup_rel}")
    if migration_pending:
        auxiliary_drift.append("install manifest migration pending")
    return {
        "entries": merged,
        "present": bool(candidates),
        "auxiliary_drift": auxiliary_drift,
        "modelconfig": metadata["modelconfig"],
        "checkout_mode": metadata["checkout_mode"],
        "permission_backend": metadata["permission_backend"],
        "installed_hosts": installed_hosts,
        "migration_pending": migration_pending,
        "legacy_path": legacy if legacy != canonical and legacy.exists() else None,
    }


def _managed_span(
    data: bytes, start_marker: bytes, end_marker: bytes, label: str
) -> tuple[int, int] | None:
    starts = data.count(start_marker)
    ends = data.count(end_marker)
    if starts == 0 and ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise SyncError(f"managed {label} markers must appear exactly once")
    start = data.index(start_marker)
    end = data.index(end_marker)
    if start >= end:
        raise SyncError(f"managed {label} markers are misordered")
    if (start and data[start - 1 : start] != b"\n") or data[
        start + len(start_marker) : start + len(start_marker) + 1
    ] != b"\n":
        raise SyncError(f"managed {label} start marker must occupy its own line")
    if data[end - 1 : end] != b"\n":
        raise SyncError(f"managed {label} end marker must occupy its own line")
    end += len(end_marker)
    if data[end : end + 1] not in {b"", b"\n"}:
        raise SyncError(f"managed {label} end marker must occupy its own line")
    if data[end : end + 1] == b"\n":
        end += 1
    return start, end


def _block_span(data: bytes) -> tuple[int, int] | None:
    return _managed_span(data, START, END, "AGENTS")


def _config_span(data: bytes) -> tuple[int, int] | None:
    return _managed_span(
        _toml_structure_mask(data), CONFIG_START, CONFIG_END, "config"
    )


def _owned_config_parts(
    data: bytes, owner_digest: str
) -> tuple[bytes, bytes] | None:
    """Recognize an owned block plus MCP tables inserted before its end marker."""

    span = _config_span(data)
    if span is None:
        return None
    block = data[span[0] : span[1]]
    if _digest(block) == owner_digest:
        return block, b""
    marker = block.rfind(CONFIG_END)
    if marker < 0:
        return None
    for name, start, _ in _table_spans(block):
        if not name.startswith("mcp_servers.") or name == "mcp_servers.orchestra_tasks":
            continue
        prefix = block[:start].rstrip(b"\n") + b"\n"
        candidate = prefix + CONFIG_END + b"\n"
        if _digest(candidate) != owner_digest:
            continue
        extension = block[start:marker]
        normalized = data[: span[0]] + candidate + extension + data[span[1] :]
        _parse_config(normalized)
        return candidate, extension
    return None


def _normalize_owned_config(
    data: bytes, recovery: tuple[bytes, bytes] | None
) -> bytes:
    if recovery is None or not recovery[1]:
        return data
    span = _config_span(data)
    if span is None:
        raise SyncError("owned managed block is missing from config.toml")
    managed, extension = recovery
    normalized = data[: span[0]] + managed + extension + data[span[1] :]
    _parse_config(normalized)
    return normalized


def _entry_span(entry: dict[str, Any], data: bytes) -> tuple[int, int] | None:
    if entry["type"] == "managed_block":
        return _block_span(data)
    if entry["type"] == "managed_config":
        return _config_span(data)
    return None


def _parse_config(data: bytes) -> dict[str, Any]:
    try:
        parsed = tomllib.loads(data.decode()) if data else {}
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise SyncError(f"invalid Codex config.toml: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SyncError("invalid Codex config.toml structure")
    return parsed


def _config_block(
    writable_roots: list[Path],
    *,
    backend: str,
    parsed: dict[str, Any],
    codex_home: Path,
) -> bytes:
    _ = writable_roots, parsed
    lines = [CONFIG_START]
    if backend == "profile":
        command = json.dumps(sys.executable)
        wrapper = json.dumps(str(codex_home / "orchestra/scripts/task_mcp.py"))
        lines.extend(
            (
                b'approval_policy = "on-request"',
                b'approvals_reviewer = "auto_review"',
                f'default_permissions = "{PERMISSION_PROFILE}"'.encode(),
                (
                    "mcp_servers.orchestra_tasks = { "
                    f"command = {command}, args = [{wrapper}], required = false, "
                    "tool_timeout_sec = 3600, "
                    'default_tools_approval_mode = "writes" }'
                ).encode(),
            )
        )
    else:
        raise SyncError(f"unknown permission backend: {backend}")
    lines.append(CONFIG_END)
    block = b"\n".join(lines) + b"\n"
    _parse_config(block)
    return block


def _normalized_config_root(value: str, home: Path) -> Path:
    if value == "~":
        candidate = home
    elif value.startswith("~/"):
        candidate = home / value[2:]
    elif value.startswith("~"):
        raise SyncError("writable_roots must not use another user's home")
    else:
        candidate = Path(value)
    if not candidate.is_absolute():
        raise SyncError("writable_roots entries must be absolute or home-relative")
    return Path(os.path.abspath(candidate))


def _configured_writable_roots(data: bytes, home: Path) -> list[Path]:
    parsed = _parse_config(data)
    sandbox = parsed.get("sandbox_workspace_write")
    if sandbox is None:
        return []
    if not isinstance(sandbox, dict):
        raise SyncError("sandbox_workspace_write must be a TOML table")
    roots = sandbox.get("writable_roots", [])
    if not isinstance(roots, list) or any(not isinstance(item, str) for item in roots):
        raise SyncError("sandbox_workspace_write.writable_roots must be an array of strings")
    return [_normalized_config_root(item, home) for item in roots]


def _profile_is_configured(
    data: bytes,
    home: Path,
    desired_roots: list[Path],
    backend: str,
) -> bool:
    _ = home, desired_roots
    parsed = _parse_config(data)
    if backend == "legacy":
        return False
    permissions = parsed.get("permissions")
    return (
        parsed.get("approval_policy") == "on-request"
        and parsed.get("approvals_reviewer") == "auto_review"
        and parsed.get("sandbox_mode") is None
        and parsed.get("default_permissions") == PERMISSION_PROFILE
        and parsed.get("sandbox_workspace_write") is None
        and not (
            isinstance(permissions, dict)
            and RETIRED_PERMISSION_PROFILE in permissions
        )
    )


def _toml_structure_mask(data: bytes) -> bytes:
    """Mask TOML strings while preserving byte offsets, comments, and newlines."""
    masked = bytearray(data)
    index = 0
    state = "code"
    while index < len(data):
        if state == "code":
            if data[index : index + 3] == b'"""':
                masked[index : index + 3] = b"   "
                state = "multiline_basic"
                index += 3
                continue
            if data[index : index + 3] == b"'''":
                masked[index : index + 3] = b"   "
                state = "multiline_literal"
                index += 3
                continue
            if data[index : index + 1] == b'"':
                masked[index] = 0x20
                state = "basic"
            elif data[index : index + 1] == b"'":
                masked[index] = 0x20
                state = "literal"
            elif data[index : index + 1] == b"#":
                state = "comment"
            index += 1
            continue

        if state == "comment":
            if data[index : index + 1] == b"\n":
                state = "code"
            index += 1
            continue

        if state == "basic":
            if data[index : index + 1] == b"\n":
                state = "code"
                index += 1
                continue
            masked[index] = 0x20
            if data[index : index + 1] == b"\\" and index + 1 < len(data):
                index += 1
                if data[index : index + 1] != b"\n":
                    masked[index] = 0x20
            elif data[index : index + 1] == b'"':
                state = "code"
            index += 1
            continue

        if state == "literal":
            if data[index : index + 1] == b"\n":
                state = "code"
                index += 1
                continue
            masked[index] = 0x20
            if data[index : index + 1] == b"'":
                state = "code"
            index += 1
            continue

        if state == "multiline_basic":
            if data[index : index + 3] == b'"""':
                masked[index : index + 3] = b"   "
                state = "code"
                index += 3
                continue
            if data[index : index + 1] != b"\n":
                masked[index] = 0x20
            if data[index : index + 1] == b"\\" and index + 1 < len(data):
                index += 1
                if data[index : index + 1] != b"\n":
                    masked[index] = 0x20
            index += 1
            continue

        if data[index : index + 3] == b"'''":
            masked[index : index + 3] = b"   "
            state = "code"
            index += 3
            continue
        if data[index : index + 1] != b"\n":
            masked[index] = 0x20
        index += 1
    return bytes(masked)


def _table_spans(data: bytes) -> list[tuple[str, int, int]]:
    structure = _toml_structure_mask(data)
    headers = list(
        re.finditer(
            rb"(?m)^[ \t]*\[(?!\[)([^\]\n]+)\][ \t]*(?:#.*)?(?:\n|$)",
            structure,
        )
    )
    all_headers = list(
        re.finditer(rb"(?m)^[ \t]*\[\[?[^\n]+(?:\n|$)", structure)
    )
    result: list[tuple[str, int, int]] = []
    for header in headers:
        end = len(data)
        for candidate in all_headers:
            if candidate.start() > header.start():
                end = candidate.start()
                break
        try:
            name = header.group(1).decode().strip()
        except UnicodeDecodeError as exc:
            raise SyncError("invalid non-UTF-8 TOML table name") from exc
        result.append((name, header.start(), end))
    return result


def _top_level_assignment_span(data: bytes, key: str) -> tuple[int, int] | None:
    structure = _toml_structure_mask(data)
    first_table = min(
        (start for _, start, _ in _table_spans(data)),
        default=len(data),
    )
    matches = list(
        re.finditer(
            rb"(?m)^[ \t]*"
            + re.escape(key.encode())
            + rb"[ \t]*=[^\n]*(?:\n|$)",
            structure[:first_table],
        )
    )
    if len(matches) > 1:
        raise SyncError(f"duplicate top-level Codex config field: {key}")
    if not matches:
        return None
    return matches[0].start(), matches[0].end()


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(spans):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [(start, end) for start, end in merged]


def _permission_spans(data: bytes) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    marker = _config_span(data)
    if marker is not None:
        spans.append(marker)
    for key in (
        "approval_policy",
        "approvals_reviewer",
        "sandbox_mode",
        "default_permissions",
    ):
        assignment = _top_level_assignment_span(data, key)
        if assignment is not None:
            spans.append(assignment)
    profile_prefix = f"permissions.{RETIRED_PERMISSION_PROFILE}"
    for name, start, end in _table_spans(data):
        if name == "sandbox_workspace_write" or (
            name == profile_prefix or name.startswith(profile_prefix + ".")
        ):
            spans.append((start, end))
    return _merge_spans(spans)


def _remove_spans(data: bytes, spans: list[tuple[int, int]]) -> bytes:
    result = data
    for start, end in reversed(spans):
        result = result[:start] + result[end:]
    return result


def _strip_permission_config(data: bytes) -> bytes:
    return _remove_spans(data, _permission_spans(data))


def _validate_permission_transition(
    data: bytes,
    home: Path,
    desired_roots: list[Path],
    *,
    owned: bool,
) -> None:
    marker = _config_span(data) if owned else None
    user_data = _remove_spans(data, [marker]) if marker is not None else data
    user_parsed = _parse_config(user_data)
    if user_parsed.get("sandbox_mode") is not None:
        raise SyncError(
            "sandbox_mode is user-owned; remove it before enabling Orchestra "
            "permissions"
        )
    if user_parsed.get("default_permissions") is not None:
        raise SyncError(
            "default_permissions is user-owned; remove it or add Orchestra roots "
            "to the selected profile"
        )
    permissions = user_parsed.get("permissions")
    if (
        isinstance(permissions, dict)
        and RETIRED_PERMISSION_PROFILE in permissions
    ):
        raise SyncError(
            f"permissions.{RETIRED_PERMISSION_PROFILE} is user-owned"
        )
    sandbox = user_parsed.get("sandbox_workspace_write")
    if sandbox is not None and not isinstance(sandbox, dict):
        raise SyncError("sandbox_workspace_write must be a TOML table")
    if isinstance(sandbox, dict):
        unknown = set(sandbox) - KNOWN_LEGACY_SANDBOX_KEYS
        if unknown:
            raise SyncError(
                "sandbox_workspace_write contains unsupported user-owned fields: "
                + ", ".join(sorted(unknown))
            )
        if "network_access" in sandbox:
            raise SyncError(
                "sandbox_workspace_write.network_access is user-owned; remove it "
                "before enabling Orchestra permissions"
            )
        if "writable_roots" in sandbox:
            configured = _configured_writable_roots(user_data, home)
            if set(configured) != set(desired_roots):
                raise SyncError(
                    "user-owned writable_roots cannot be migrated without "
                    "changing their scope"
                )


def _insert_permission_block(data: bytes, block: bytes) -> bytes:
    first_table = min(
        (start for _, start, _ in _table_spans(data)),
        default=len(data),
    )
    prefix = data[:first_table]
    suffix = data[first_table:]
    separator = b"" if not prefix or prefix.endswith(b"\n") else b"\n"
    result = prefix + separator + block + suffix
    _parse_config(result)
    return result


def _render_managed_config(data: bytes, block: bytes) -> bytes:
    return _insert_permission_block(_strip_permission_config(data), block)


def _restore_permission_config(current: bytes, backup: bytes) -> bytes:
    marker = _config_span(current)
    if marker is not None:
        managed = current[marker[0] : marker[1]]
        expected = _insert_permission_block(
            _strip_permission_config(backup),
            managed,
        )
        if current == expected:
            return backup
    current_base = _strip_permission_config(current)
    backup_base = _strip_permission_config(backup)
    if current_base == backup_base:
        return backup
    fragments = b"".join(
        backup[start:end] for start, end in _permission_spans(backup)
    ).strip(b"\n")
    if not fragments:
        _parse_config(current_base)
        return current_base
    return _insert_permission_block(current_base, fragments + b"\n")


def _unconfigured_cache_tools(
    data: bytes,
    home: Path,
    cache_roots: dict[str, Path],
    backend: str,
) -> list[str]:
    _ = data, home, cache_roots, backend
    return []


def _desired_config_entry(
    home: Path,
    codex_home: Path,
    worktree_root: Path,
    orchestra_root: Path,
    cache_roots: dict[str, Path],
    installed: dict[tuple[str, str], dict[str, str]],
    backend: str,
) -> tuple[dict[str, Any], list[str]]:
    key = ("codex_home", "config.toml")
    path = _safe_path(codex_home, "config.toml")
    current = _read_file(path, "config.toml") if path.exists() else b""
    desired_roots = _minimal_writable_roots(
        orchestra_root, worktree_root, cache_roots
    )
    missing_cache_tools = _unconfigured_cache_tools(
        current, home, cache_roots, backend
    )
    owner = installed.get(key)
    parsed = _parse_config(current)
    _validate_permission_transition(
        current,
        home,
        desired_roots,
        owned=owner is not None,
    )
    desired_block = _config_block(
        desired_roots,
        backend=backend,
        parsed=parsed,
        codex_home=codex_home,
    )
    if owner is not None:
        if _owned_config_parts(current, owner["digest"]) is None:
            raise SyncError("owned managed block drift in config.toml")
        return (
            _entry(
                "codex_home",
                "config.toml",
                "managed_config",
                desired_block,
            ),
            missing_cache_tools,
        )
    if _config_span(current) is not None:
        raise SyncError("unmanaged Orchestra markers in config.toml")
    return (
        _entry(
            "codex_home",
            "config.toml",
            "managed_config",
            desired_block,
        ),
        missing_cache_tools,
    )


def _insert_config_block(data: bytes, block: bytes) -> bytes:
    return _render_managed_config(data, block)


def _roots(
    home: Path, codex_home: Path, orchestra_home: Path | None = None
) -> dict[str, Path]:
    return {
        "home": home,
        "codex_home": codex_home,
        "orchestra_home": orchestra_home or _orchestra_home(home),
    }


def _destination(roots: dict[str, Path], entry: dict[str, Any]) -> Path:
    return _safe_path(roots[entry["root"]], entry["path"])


def _operation(
    kind: str,
    entry: dict[str, Any],
    before: bytes | None,
    *,
    preserve_backup: bool = False,
) -> dict[str, Any]:
    return {
        "kind": kind,
        "entry": entry,
        "before": before,
        "preserve_backup": preserve_backup,
    }


def _analyze(
    source_root: Path,
    home: Path,
    codex_home: Path,
    modelconfig: str | None,
    checkout_mode: str,
    worktree_root: Path,
    orchestra_root: Path,
    orchestra_home: Path,
    cache_roots: dict[str, Path],
    installed: dict[tuple[str, str], dict[str, str]],
    auxiliary_drift: list[str],
    permission_backend: str | None,
    host: str,
) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    list[dict[str, Any]],
    list[str],
    list[str],
]:
    desired = _inventory(
        source_root,
        modelconfig,
        checkout_mode,
        worktree_root,
        host,
        orchestra_home,
    )
    missing_cache_tools: list[str] = []
    if _includes_codex(host):
        assert permission_backend is not None
        config_entry, missing_cache_tools = _desired_config_entry(
            home,
            codex_home,
            worktree_root,
            orchestra_root,
            cache_roots,
            installed,
            permission_backend,
        )
        desired[("codex_home", "config.toml")] = config_entry
    roots = _roots(home, codex_home, orchestra_home)
    operations: list[dict[str, Any]] = []

    for key in sorted(desired):
        entry = desired[key]
        path = _destination(roots, entry)
        owner = installed.get(key)
        if owner is not None and owner["scope"] != entry["scope"]:
            raise SyncError(f"owned destination scope drift: {entry['path']}")
        if entry["type"] == "file":
            if owner is None:
                if path.exists():
                    current = _read_file(path, entry["path"])
                    if (
                        entry["root"] == "orchestra_home"
                        and current == entry["content"]
                    ):
                        continue
                    raise SyncError(f"unmanaged destination collision: {entry['path']}")
                operations.append(_operation("create", entry, None))
                continue
            current = _read_file(path, entry["path"])
            if _digest(current) != owner["digest"]:
                raise SyncError(f"owned destination drift: {entry['path']}")
            if current != entry["content"]:
                operations.append(_operation("update", entry, current))
        else:
            current = _read_file(path, entry["path"]) if path.exists() else b""
            if entry["type"] == "managed_json":
                parsed_config = _devin_parse_config(current)
                matcher_indices = _devin_find_matchers(parsed_config)
                if owner is None:
                    if matcher_indices:
                        conflicting = _devin_matcher_command(
                            parsed_config["hooks"]["SessionStart"][
                                matcher_indices[0]
                            ]
                        )
                        raise SyncError(
                            f"unmanaged Orchestra hook in {entry['path']}: "
                            f"{conflicting}"
                        )
                    _devin_validate_hooks_shape(parsed_config, entry["path"])
                    operations.append(
                        _operation(
                            "insert_json_hook",
                            entry,
                            current if path.exists() else None,
                        )
                    )
                    continue
                if not matcher_indices:
                    raise SyncError(
                        f"owned Orchestra hook is missing from {entry['path']}"
                    )
                if len(matcher_indices) != 1:
                    raise SyncError(
                        f"owned Orchestra hook drift in {entry['path']}"
                    )
                found = parsed_config["hooks"]["SessionStart"][matcher_indices[0]]
                if (
                    _digest(_devin_canonical_matcher_bytes(found))
                    != owner["digest"]
                ):
                    raise SyncError(
                        f"owned Orchestra hook drift in {entry['path']}"
                    )
                if _devin_canonical_matcher_bytes(found) != entry["content"]:
                    operations.append(
                        _operation(
                            "update_json_hook",
                            entry,
                            current,
                            preserve_backup=True,
                        )
                    )
                continue
            span = _entry_span(entry, current)
            config_recovery = (
                _owned_config_parts(current, owner["digest"])
                if owner is not None and entry["type"] == "managed_config"
                else None
            )
            if owner is None:
                if span is not None:
                    raise SyncError(f"unmanaged Orchestra markers in {entry['path']}")
                kind = (
                    "insert_config_block"
                    if entry["type"] == "managed_config"
                    else "insert_block"
                )
                operations.append(_operation(kind, entry, current if path.exists() else None))
                continue
            if not path.exists() or span is None:
                raise SyncError(f"owned managed block is missing from {entry['path']}")
            if entry["type"] == "managed_config":
                matches = config_recovery is not None
            else:
                matches = _digest(current[span[0] : span[1]]) == owner["digest"]
            if not matches:
                raise SyncError(f"owned managed block drift in {entry['path']}")
            if current[span[0] : span[1]] != entry["content"]:
                kind = (
                    "update_config_block"
                    if entry["type"] == "managed_config"
                    else "update_block"
                )
                operation = _operation(kind, entry, current, preserve_backup=True)
                if config_recovery is not None and config_recovery[1]:
                    operation["config_recovery"] = config_recovery
                operations.append(operation)

    selected_scopes = {"shared"}
    selected_scopes.update(HOST_SCOPES if host == "all" else {host})
    for key in sorted(set(installed) - set(desired)):
        owner = installed[key]
        if owner["scope"] not in selected_scopes:
            continue
        path = _safe_path(roots[owner["root"]], owner["path"])
        current = _read_file(path, owner["path"])
        if owner["type"] == "managed_json":
            parsed_config = _devin_parse_config(current)
            matcher_indices = _devin_find_matchers(parsed_config)
            if not matcher_indices or any(
                _digest(
                    _devin_canonical_matcher_bytes(
                        parsed_config["hooks"]["SessionStart"][index]
                    )
                )
                != owner["digest"]
                for index in matcher_indices
            ):
                raise SyncError(f"owned destination drift: {owner['path']}")
        elif owner["type"] in {"managed_block", "managed_config"}:
            span = _entry_span(owner, current)
            if span is None or _digest(current[span[0] : span[1]]) != owner["digest"]:
                raise SyncError(f"owned destination drift: {owner['path']}")
        elif _digest(current) != owner["digest"]:
            raise SyncError(f"owned destination drift: {owner['path']}")
        stale = dict(owner)
        stale["content"] = b""
        operations.append(_operation("delete", stale, current))

    for operation in operations:
        if operation["before"] is None:
            continue
        entry = operation["entry"]
        backup_rel = _backup_path(entry["root"], entry["path"])
        backup = _safe_path(roots[_backup_root_name(entry)], backup_rel)
        owner = installed.get((entry["root"], entry["path"]))
        if backup.exists() and (
            owner is None
            or owner.get("backup") != backup_rel
            or owner.get("backup_root") != _backup_root_name(entry)
        ):
            raise SyncError(f"unmanaged backup collision: {backup_rel}")
    operations.sort(key=lambda item: (item["entry"]["root"], item["entry"]["path"], item["kind"]))
    return desired, operations, auxiliary_drift, missing_cache_tools


def _mkdir_parent(path: Path, root: Path) -> None:
    relative = path.relative_to(root)
    current = root
    if current.exists() and (current.is_symlink() or not current.is_dir()):
        raise SyncError(f"invalid destination root: {root}")
    if not current.exists():
        missing = []
        ancestor = current
        while not ancestor.exists():
            if ancestor.is_symlink():
                raise SyncError(f"destination root uses a symlink: {root}")
            missing.append(ancestor)
            ancestor = ancestor.parent
        if ancestor.is_symlink() or not ancestor.is_dir():
            raise SyncError(f"invalid destination root ancestor: {ancestor}")
        for directory in reversed(missing):
            directory.mkdir()
    for part in relative.parts[:-1]:
        current = current / part
        if current.exists():
            if current.is_symlink() or not current.is_dir():
                raise SyncError(f"invalid destination parent: {current}")
        else:
            current.mkdir()


def _atomic_write(path: Path, data: bytes, root: Path, *, new_mode: int = 0o644) -> None:
    _mkdir_parent(path, root)
    mode = new_mode
    if path.exists():
        if path.is_symlink() or not path.is_file():
            raise SyncError(f"expected a regular destination file: {path}")
        mode = stat.S_IMODE(path.stat().st_mode)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _write_manifest(
    orchestra_home: Path,
    entries: dict[tuple[str, str], dict[str, str]],
    installed_hosts: set[str],
    modelconfig: str | None,
    checkout_mode: str | None,
    permission_backend: str | None,
) -> None:
    root = orchestra_home
    path = _safe_path(orchestra_home, ORCHESTRA_MANIFEST_PATH)
    if not entries and not installed_hosts:
        if path.exists():
            path.unlink()
        return
    if any(host not in HOST_SCOPES for host in installed_hosts):
        raise SyncError("invalid installed host set")
    payload: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "installed_hosts": sorted(installed_hosts),
        "entries": [entries[key] for key in sorted(entries)]
    }
    if modelconfig is not None:
        if modelconfig not in (*MODELCONFIGS, *LEGACY_MODELCONFIGS):
            raise SyncError(f"unknown model configuration: {modelconfig}")
        payload["modelconfig"] = modelconfig
    if checkout_mode is not None:
        if checkout_mode not in CHECKOUT_MODES:
            raise SyncError(f"unknown checkout mode: {checkout_mode}")
        payload["checkout_mode"] = checkout_mode
    if permission_backend is not None:
        if permission_backend not in PERMISSION_BACKENDS:
            raise SyncError(f"unknown permission backend: {permission_backend}")
        payload["permission_backend"] = permission_backend
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    _atomic_write(path, data, root, new_mode=0o600)


def _preview(operations: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "operation": operation["kind"],
            "path": operation["entry"]["path"],
            "root": operation["entry"]["root"],
        }
        for operation in operations
    ]


def _restart_required(changes: list[dict[str, str]]) -> bool:
    return any(
        (
            change["root"] == "codex_home"
            and change["path"] in {"config.toml", *RETIRED_RULES_PATHS}
        )
        or (
            change["root"] == "home"
            and change["path"].startswith(f"{CURSOR_PLUGIN_ROOT}/")
        )
        or (
            change["root"] == "home"
            and change["path"].startswith(".config/devin/")
        )
        for change in changes
    )


def _check_before(path: Path, before: bytes | None) -> None:
    if before is None:
        if path.exists():
            raise SyncError(f"destination changed during synchronization: {path}")
        return
    if _read_file(path, str(path)) != before:
        raise SyncError(f"destination changed during synchronization: {path}")


def _apply_operation(
    operation: dict[str, Any], roots: dict[str, Path], backup_root: Path
) -> dict[str, Any]:
    entry = operation["entry"]
    path = _destination(roots, entry)
    before = operation["before"]
    _check_before(path, before)
    state: dict[str, Any] = {
        "path": path,
        "root": roots[entry["root"]],
        "before": before,
        "mode": stat.S_IMODE(path.stat().st_mode) if path.exists() else None,
        "backup": None,
        "backup_before": None,
        "backup_mode": None,
        "backup_rel": None,
    }
    backup_rel: str | None = None
    backup: Path | None = None
    try:
        if before is not None and not operation["preserve_backup"]:
            backup_rel = _backup_path(entry["root"], entry["path"])
            backup = _safe_path(backup_root, backup_rel)
            state["backup"] = backup
            state["backup_rel"] = backup_rel
            if backup.exists():
                state["backup_before"] = _read_file(backup, backup_rel)
                state["backup_mode"] = stat.S_IMODE(backup.stat().st_mode)
            _atomic_write(backup, before, backup_root, new_mode=0o600)

        kind = operation["kind"]
        if kind in {"create", "update"}:
            _atomic_write(path, entry["content"], roots[entry["root"]])
        elif kind == "insert_block":
            outside = before or b""
            content = entry["content"] + (b"\n" if outside else b"") + outside
            _atomic_write(path, content, roots[entry["root"]])
        elif kind == "update_block":
            span = _block_span(before)
            assert span is not None
            _atomic_write(path, before[: span[0]] + entry["content"] + before[span[1] :], roots[entry["root"]])
        elif kind == "insert_config_block":
            content = _insert_config_block(before or b"", entry["content"])
            _atomic_write(path, content, roots[entry["root"]])
        elif kind == "update_config_block":
            normalized = _normalize_owned_config(
                before, operation.get("config_recovery")
            )
            span = _config_span(normalized)
            assert span is not None
            content = _render_managed_config(normalized, entry["content"])
            _atomic_write(path, content, roots[entry["root"]])
        elif kind == "insert_json_hook":
            parsed_config = _devin_parse_config(before or b"")
            _devin_validate_hooks_shape(parsed_config, entry["path"])
            hooks = parsed_config.setdefault("hooks", {})
            session_start = hooks.setdefault("SessionStart", [])
            session_start.append(json.loads(entry["content"].decode()))
            _atomic_write(
                path,
                _devin_render(parsed_config),
                roots[entry["root"]],
                new_mode=0o600,
            )
        elif kind == "update_json_hook":
            parsed_config = _devin_parse_config(before or b"")
            matcher_indices = _devin_find_matchers(parsed_config)
            if len(matcher_indices) != 1:
                raise SyncError(
                    f"owned Orchestra hook is missing from {entry['path']}"
                )
            parsed_config["hooks"]["SessionStart"][matcher_indices[0]] = json.loads(
                entry["content"].decode()
            )
            _atomic_write(path, _devin_render(parsed_config), roots[entry["root"]])
        elif kind == "delete":
            if entry["type"] == "managed_json":
                parsed_config = _devin_parse_config(before or b"")
                _devin_strip_matcher(parsed_config)
                remaining = _devin_render(parsed_config) if parsed_config else b""
                if remaining.strip():
                    _atomic_write(path, remaining, roots[entry["root"]])
                else:
                    path.unlink()
            elif entry["type"] in {"managed_block", "managed_config"}:
                if entry["type"] == "managed_config":
                    normalized = _normalize_owned_config(
                        before, operation.get("config_recovery")
                    )
                    restore = operation.get("restore")
                    if restore is not None:
                        remaining = _restore_permission_config(normalized, restore)
                    else:
                        remaining = _strip_permission_config(normalized)
                    _parse_config(remaining)
                else:
                    span = _entry_span(entry, before)
                    assert span is not None
                    end = span[1]
                    if before[end : end + 1] == b"\n":
                        end += 1
                    remaining = before[: span[0]] + before[end:]
                if remaining or entry.get("_keep_empty", False):
                    _atomic_write(path, remaining, roots[entry["root"]])
                else:
                    path.unlink()
            else:
                path.unlink()
            _cleanup_operation_backup(state, backup_root)
        else:
            raise SyncError(f"unknown operation: {kind}")
    except Exception:
        _restore_operation(state, backup_root)
        raise
    return state


def _cleanup_operation_backup(state: dict[str, Any], backup_root: Path) -> None:
    """Remove the transient delete backup while local compensation is possible."""
    backup = state["backup"]
    if backup is not None and backup.exists():
        backup.unlink()
        _cleanup_empty(backup.parent, backup_root)


def _restore_operation(state: dict[str, Any], backup_root: Path) -> None:
    path = state["path"]
    before = state["before"]
    if before is None:
        if path.exists():
            if path.is_symlink() or not path.is_file():
                raise SyncError(f"cannot compensate unsafe destination: {path}")
            path.unlink()
        _cleanup_empty(path.parent, state["root"])
    else:
        _atomic_write(path, before, state["root"], new_mode=state["mode"] or 0o644)
        os.chmod(path, state["mode"])

    backup = state["backup"]
    if backup is None:
        return
    if state["backup_before"] is None:
        if backup.exists():
            if backup.is_symlink() or not backup.is_file():
                raise SyncError(f"cannot compensate unsafe backup: {backup}")
            backup.unlink()
        _cleanup_empty(backup.parent, backup_root)
    else:
        _atomic_write(
            backup,
            state["backup_before"],
            backup_root,
            new_mode=state["backup_mode"] or 0o600,
        )
        os.chmod(backup, state["backup_mode"])


def _cleanup_empty(path: Path, stop: Path) -> None:
    current = path
    while current != stop and current.exists() and current.is_dir():
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent


def _persist_manifest(
    host: str,
    codex_home: Path,
    orchestra_home: Path,
    entries: dict[tuple[str, str], dict[str, str]],
    installed_hosts: set[str],
    modelconfig: str | None,
    checkout_mode: str | None,
    permission_backend: str | None,
) -> None:
    _ = host, codex_home
    _write_manifest(
        orchestra_home,
        entries,
        installed_hosts,
        modelconfig,
        checkout_mode,
        permission_backend,
    )


def synchronize(
    source_root: Path,
    home: Path,
    codex_home: Path,
    action: str,
    *,
    dry_run: bool = False,
    modelconfig: str | None = None,
    checkout_mode: str | None = None,
    worktree_root: Path | str | None = None,
    host: str = "codex",
) -> dict[str, Any]:
    """Run one synchronization action against explicit destination roots."""
    source_root = Path(os.path.abspath(source_root))
    home = Path(os.path.abspath(home))
    codex_home = Path(os.path.abspath(codex_home))
    label = "apply --dry-run" if action == "apply" and dry_run else action
    orchestra_root = _orchestra_root(home)
    orchestra_home = _orchestra_home(home)
    if host not in HOSTS:
        return _result(
            "blocked",
            label,
            [],
            f"unknown host: {host}",
            sandbox_root=orchestra_root,
        )
    include_codex = _includes_codex(host)
    selected_hosts = set(HOST_SCOPES if host == "all" else (host,))
    permission_backend: str | None = None
    if include_codex:
        try:
            codex_version, parsed_codex_version = _detect_codex_version()
        except SyncError as exc:
            return _result(
                "blocked",
                label,
                [],
                str(exc),
                sandbox_root=orchestra_root,
                codex_version="unknown",
            )
        try:
            permission_backend = _permission_backend(parsed_codex_version)
        except SyncError as exc:
            return _result(
                "blocked",
                label,
                [],
                str(exc),
                sandbox_root=orchestra_root,
                codex_version=codex_version,
            )
        try:
            cache_roots, omitted_cache_tools = _discover_cache_roots(home)
        except OSError:
            cache_roots = {}
            omitted_cache_tools = {
                tool: "cache discovery unavailable" for tool in CACHE_TOOLS
            }
    else:
        codex_version = None
        cache_roots = {}
        omitted_cache_tools = {}
    result_context: dict[str, Any] = {
        "sandbox_root": orchestra_root,
        "cache_roots": cache_roots,
        "omitted_cache_tools": omitted_cache_tools,
        "codex_version": codex_version,
        "permission_backend": permission_backend,
        "permission_profile": (
            PERMISSION_PROFILE if permission_backend == "profile" else None
        ),
    }
    missing_cache_tools: list[str] = []
    try:
        effective_worktree_root = _resolve_worktree_root(home, worktree_root)
        install_state = _load_install_state(codex_home, orchestra_home)
        installed = install_state["entries"]
        manifest_present = install_state["present"]
        auxiliary_drift = list(install_state["auxiliary_drift"])
        installed_modelconfig = install_state["modelconfig"]
        installed_checkout_mode = install_state["checkout_mode"]
        installed_permission_backend = install_state["permission_backend"]
        installed_hosts = set(install_state["installed_hosts"])
        if modelconfig is not None and modelconfig not in MODELCONFIGS:
            raise SyncError(f"unknown model configuration: {modelconfig}")
        effective_modelconfig = "native" if include_codex else installed_modelconfig
        if checkout_mode is not None and checkout_mode not in CHECKOUT_MODES:
            raise SyncError(f"unknown checkout mode: {checkout_mode}")
        effective_checkout_mode = checkout_mode or installed_checkout_mode or "managed"
        desired, operations, auxiliary_drift, missing_cache_tools = _analyze(
            source_root,
            home,
            codex_home,
            effective_modelconfig,
            effective_checkout_mode,
            effective_worktree_root,
            orchestra_root,
            orchestra_home,
            cache_roots,
            installed,
            auxiliary_drift,
            permission_backend,
            host,
        )
    except (OSError, SyncError) as exc:
        return _result(
            "blocked",
            label,
            [],
            str(exc),
            unconfigured_cache_tools=missing_cache_tools,
            **result_context,
        )
    changes = _preview(operations)
    config_change_pending = any(
        change["path"] == "config.toml" and change["root"] == "codex_home"
        for change in changes
    )
    restart_change_pending = _restart_required(changes)
    if action == "status" or dry_run:
        detail = "; ".join(auxiliary_drift)
        try:
            profile_configured = False
            if include_codex:
                assert permission_backend is not None
                config_path = _safe_path(codex_home, "config.toml")
                current_config = (
                    _read_file(config_path, "config.toml")
                    if config_path.exists()
                    else b""
                )
                desired_roots = _minimal_writable_roots(
                    orchestra_root, effective_worktree_root, cache_roots
                )
                profile_configured = (
                    permission_backend == "profile"
                    and _profile_is_configured(
                        current_config,
                        home,
                        desired_roots,
                        permission_backend,
                    )
                    and not config_change_pending
                )
        except (OSError, SyncError) as exc:
            return _result(
                "blocked",
                label,
                changes,
                str(exc),
                modelconfig=effective_modelconfig,
                checkout_mode=effective_checkout_mode,
                worktree_root=effective_worktree_root,
                unconfigured_cache_tools=missing_cache_tools,
                restart_required=restart_change_pending,
                profile_configured=False,
                **result_context,
            )
        return _result(
            "partial" if operations or auxiliary_drift else "ok",
            label,
            changes,
            detail,
            modelconfig=effective_modelconfig,
            checkout_mode=effective_checkout_mode,
            worktree_root=effective_worktree_root,
            unconfigured_cache_tools=missing_cache_tools,
            restart_required=restart_change_pending,
            profile_configured=profile_configured,
            **result_context,
        )
    if action != "apply":
        return _result(
            "blocked",
            label,
            [],
            f"unsupported action: {action}",
            modelconfig=effective_modelconfig,
            checkout_mode=effective_checkout_mode,
            worktree_root=effective_worktree_root,
            unconfigured_cache_tools=missing_cache_tools,
            **result_context,
        )

    if install_state["migration_pending"]:
        try:
            _write_manifest(
                orchestra_home,
                installed,
                installed_hosts,
                installed_modelconfig,
                installed_checkout_mode,
                installed_permission_backend,
            )
            legacy_path = install_state.get("legacy_path")
            if legacy_path is not None and legacy_path.exists():
                legacy_path.unlink()
            auxiliary_drift = [
                item
                for item in auxiliary_drift
                if item != "install manifest migration pending"
            ]
        except (OSError, SyncError) as exc:
            return _result(
                "partial" if _manifest_file(codex_home, orchestra_home).exists() else "blocked",
                label,
                [],
                f"install manifest migration failed: {exc}",
                modelconfig=installed_modelconfig,
                checkout_mode=installed_checkout_mode,
                worktree_root=effective_worktree_root,
                unconfigured_cache_tools=missing_cache_tools,
                restart_required=False,
                profile_configured=False,
                **result_context,
            )

    roots = _roots(home, codex_home, orchestra_home)
    current = dict(installed)
    current_hosts = installed_hosts | selected_hosts
    current_modelconfig = installed_modelconfig
    current_checkout_mode = installed_checkout_mode
    effective_permission_backend = (
        permission_backend if include_codex else installed_permission_backend
    )
    current_permission_backend = installed_permission_backend
    completed: list[dict[str, str]] = []
    for operation in operations:
        entry = operation["entry"]
        key = (entry["root"], entry["path"])
        next_current = dict(current)
        operation_backup_root = roots[_backup_root_name(entry)]
        try:
            state = _apply_operation(operation, roots, operation_backup_root)
            if operation["kind"] == "delete":
                next_current.pop(key, None)
            else:
                current_owner = current.get(key, {})
                backup_rel = state["backup_rel"] or current_owner.get("backup")
                backup_root_name = (
                    _backup_root_name(entry)
                    if state["backup_rel"]
                    else current_owner.get("backup_root")
                )
                next_current[key] = _manifest_entry(
                    desired[key],
                    backup_rel,
                    backup_root_name,
                )
            next_modelconfig = current_modelconfig
            next_checkout_mode = current_checkout_mode
            next_permission_backend = current_permission_backend
            if key == ("codex_home", "orchestra/roles.toml"):
                next_modelconfig = effective_modelconfig
            if key == ("codex_home", "config.toml"):
                next_permission_backend = permission_backend
            if key in {
                ("codex_home", CHECKOUT_MODE_PATH),
                ("orchestra_home", ORCHESTRA_CHECKOUT_MODE_PATH),
            }:
                next_checkout_mode = effective_checkout_mode
            _persist_manifest(
                host,
                codex_home,
                orchestra_home,
                next_current,
                current_hosts,
                next_modelconfig,
                next_checkout_mode,
                next_permission_backend,
            )
        except (OSError, SyncError) as exc:
            if "state" in locals():
                try:
                    _restore_operation(state, operation_backup_root)
                except (OSError, SyncError) as restore_exc:
                    exc = SyncError(f"{exc}; local compensation failed: {restore_exc}")
                del state
            status = "partial" if completed else "blocked"
            return _result(
                status,
                label,
                completed,
                str(exc),
                modelconfig=current_modelconfig,
                checkout_mode=current_checkout_mode,
                worktree_root=effective_worktree_root,
                unconfigured_cache_tools=missing_cache_tools,
                restart_required=_restart_required(completed),
                profile_configured=False,
                **result_context,
            )
        current = next_current
        current_modelconfig = next_modelconfig
        current_checkout_mode = next_checkout_mode
        current_permission_backend = next_permission_backend
        completed.extend(_preview([operation]))
        del state

    claimed = False
    for key, entry in desired.items():
        if key in current or entry["type"] != "file":
            continue
        path = _destination(roots, entry)
        if path.exists() and _read_file(path, entry["path"]) == entry["content"]:
            if entry["root"] != "orchestra_home":
                continue
            current[key] = _manifest_entry(entry)
            claimed = True

    if current and (
        claimed
        or current_hosts != installed_hosts
        or current_modelconfig != effective_modelconfig
        or current_checkout_mode != effective_checkout_mode
        or current_permission_backend != effective_permission_backend
    ):
        try:
            _persist_manifest(
                host,
                codex_home,
                orchestra_home,
                current,
                current_hosts,
                effective_modelconfig,
                effective_checkout_mode,
                effective_permission_backend,
            )
        except (OSError, SyncError) as exc:
            return _result(
                "partial" if completed else "blocked",
                label,
                completed,
                str(exc),
                modelconfig=current_modelconfig,
                checkout_mode=current_checkout_mode,
                worktree_root=effective_worktree_root,
                unconfigured_cache_tools=missing_cache_tools,
                restart_required=_restart_required(completed),
                profile_configured=False,
                **result_context,
            )
        current_modelconfig = effective_modelconfig
        current_checkout_mode = effective_checkout_mode
        current_permission_backend = effective_permission_backend

    try:
        persisted_state = _load_install_state(codex_home, orchestra_home)
        remaining_drift = list(persisted_state["auxiliary_drift"])
        persisted_modelconfig = persisted_state["modelconfig"]
        persisted_checkout_mode = persisted_state["checkout_mode"]
        persisted_permission_backend = persisted_state["permission_backend"]
    except (OSError, SyncError) as exc:
        return _result(
            "partial",
            label,
            completed,
            str(exc),
            modelconfig=current_modelconfig,
            checkout_mode=current_checkout_mode,
            worktree_root=effective_worktree_root,
            unconfigured_cache_tools=missing_cache_tools,
            restart_required=_restart_required(completed),
            profile_configured=False,
            **result_context,
        )
    try:
        final_missing_cache_tools: list[str] = []
        profile_configured = False
        if include_codex and permission_backend is not None:
            config_path = _safe_path(codex_home, "config.toml")
            final_config = (
                _read_file(config_path, "config.toml") if config_path.exists() else b""
            )
            final_missing_cache_tools = _unconfigured_cache_tools(
                final_config, home, cache_roots, permission_backend
            )
            desired_roots = _minimal_writable_roots(
                orchestra_root, effective_worktree_root, cache_roots
            )
            profile_configured = (
                persisted_permission_backend == "profile"
                and _profile_is_configured(
                    final_config,
                    home,
                    desired_roots,
                    permission_backend,
                )
            )
    except (OSError, SyncError) as exc:
        return _result(
            "partial" if completed else "blocked",
            label,
            completed,
            str(exc),
            modelconfig=persisted_modelconfig,
            checkout_mode=persisted_checkout_mode,
            worktree_root=effective_worktree_root,
            unconfigured_cache_tools=missing_cache_tools,
            restart_required=_restart_required(completed),
            profile_configured=False,
            **result_context,
        )
    if final_missing_cache_tools:
        remaining_drift.append(
            "configured permission roots do not cover detected caches: "
            + ", ".join(final_missing_cache_tools)
        )
    detail = "; ".join(remaining_drift)
    return _result(
        "partial" if remaining_drift else "ok",
        label,
        completed,
        detail,
        modelconfig=persisted_modelconfig,
        checkout_mode=persisted_checkout_mode,
        worktree_root=effective_worktree_root,
        unconfigured_cache_tools=final_missing_cache_tools,
        restart_required=_restart_required(completed),
        profile_configured=profile_configured,
        **result_context,
    )


def uninstall(home: Path, codex_home: Path, *, host: str = "codex") -> dict[str, Any]:
    """Remove only destinations still matching the recorded ownership digests."""
    home = Path(os.path.abspath(home))
    codex_home = Path(os.path.abspath(codex_home))
    orchestra_home = _orchestra_home(home)
    if host not in HOSTS:
        return _result("blocked", "uninstall", [], f"unknown host: {host}")
    try:
        install_state = _load_install_state(codex_home, orchestra_home)
    except (OSError, SyncError) as exc:
        return _result("blocked", "uninstall", [], str(exc))
    installed = install_state["entries"]
    present = install_state["present"]
    auxiliary_drift = list(install_state["auxiliary_drift"])
    modelconfig = install_state["modelconfig"]
    checkout_mode = install_state["checkout_mode"]
    permission_backend = install_state["permission_backend"]
    installed_hosts = set(install_state["installed_hosts"])
    result_context = {
        "permission_backend": permission_backend,
        "permission_profile": (
            PERMISSION_PROFILE if permission_backend == "profile" else None
        ),
    }
    if not present:
        return _result("ok", "uninstall", [], **result_context)
    roots = _roots(home, codex_home, orchestra_home)
    if install_state["migration_pending"]:
        try:
            _write_manifest(
                orchestra_home,
                installed,
                installed_hosts,
                modelconfig,
                checkout_mode,
                permission_backend,
            )
            legacy_path = install_state.get("legacy_path")
            if legacy_path is not None and legacy_path.exists():
                legacy_path.unlink()
            auxiliary_drift = [
                item
                for item in auxiliary_drift
                if item != "install manifest migration pending"
            ]
        except (OSError, SyncError) as exc:
            return _result(
                "partial" if _manifest_file(codex_home, orchestra_home).exists() else "blocked",
                "uninstall",
                [],
                f"install manifest migration failed: {exc}",
                **result_context,
            )

    target_hosts = set(HOST_SCOPES if host == "all" else (host,))
    remaining_hosts = installed_hosts - target_hosts
    remove_scopes = set(target_hosts)
    if not remaining_hosts:
        remove_scopes.add("shared")
    target_entries = [
        (key, installed[key])
        for key in sorted(installed)
        if installed[key]["scope"] in remove_scopes
    ]
    if not target_entries:
        return _result("ok", "uninstall", [], **result_context)

    prepared: list[tuple[tuple[str, str], dict[str, str], dict[str, Any], Path, Path]] = []
    preflight_errors: list[str] = []
    for key, owner in target_entries:
        backup_root = roots[_backup_root_name(owner)]
        try:
            path = _safe_path(roots[owner["root"]], owner["path"])
            data = _read_file(path, owner["path"])
            recovery = None
            if owner["type"] == "managed_json":
                parsed_config = _devin_parse_config(data)
                matcher_indices = _devin_find_matchers(parsed_config)
                matches = bool(matcher_indices) and all(
                    _digest(
                        _devin_canonical_matcher_bytes(
                            parsed_config["hooks"]["SessionStart"][index]
                        )
                    )
                    == owner["digest"]
                    for index in matcher_indices
                )
            elif owner["type"] in {"managed_block", "managed_config"}:
                span = _entry_span(owner, data)
                recovery = (
                    _owned_config_parts(data, owner["digest"])
                    if owner["type"] == "managed_config"
                    else None
                )
                matches = (
                    recovery is not None
                    if owner["type"] == "managed_config"
                    else span is not None
                    and _digest(data[span[0] : span[1]]) == owner["digest"]
                )
            else:
                matches = _digest(data) == owner["digest"]
            if not matches:
                raise SyncError("owned content drift")
            backup_rel = _backup_path(owner["root"], owner["path"])
            backup = _safe_path(backup_root, backup_rel)
            if backup.exists() and (
                owner.get("backup") != backup_rel
                or owner.get("backup_root") != _backup_root_name(owner)
            ):
                raise SyncError("unmanaged backup collision")
            stale = dict(owner)
            stale["content"] = b""
            stale["_keep_empty"] = (
                owner["type"] in {"managed_block", "managed_config"}
                and "backup" in owner
            )
            operation = _operation(
                "delete",
                stale,
                data,
                preserve_backup=owner["type"] in {"managed_config", "managed_json"},
            )
            if owner["type"] == "managed_config" and recovery is not None and recovery[1]:
                operation["config_recovery"] = recovery
            if owner["type"] == "managed_config" and "backup" in owner:
                operation["restore"] = _read_file(backup, owner["backup"])
            prepared.append((key, owner, operation, path, backup_root))
        except (OSError, SyncError) as exc:
            preflight_errors.append(f"{owner['path']}: {exc}")
    current = dict(installed)
    changes: list[dict[str, str]] = []
    for key, owner, operation, path, backup_root in prepared:
        try:
            state = _apply_operation(operation, roots, backup_root)
            next_current = dict(current)
            next_current.pop(key)
            next_hosts = set(remaining_hosts)
            next_hosts.update(
                entry["scope"]
                for entry in next_current.values()
                if entry["scope"] in HOST_SCOPES
            )
            if not next_hosts and any(
                entry["scope"] == "shared" for entry in next_current.values()
            ):
                next_hosts.update(installed_hosts & target_hosts)
            try:
                next_permission_backend = (
                    permission_backend if "codex" in next_hosts else None
                )
                next_modelconfig = modelconfig if "codex" in next_hosts else None
                next_checkout_mode = checkout_mode if next_hosts else None
                _persist_manifest(
                    host,
                    codex_home,
                    orchestra_home,
                    next_current,
                    next_hosts,
                    next_modelconfig,
                    next_checkout_mode,
                    next_permission_backend,
                )
            except (OSError, SyncError) as exc:
                try:
                    _restore_operation(state, backup_root)
                except (OSError, SyncError) as restore_exc:
                    exc = SyncError(f"{exc}; local compensation failed: {restore_exc}")
                status = "partial" if changes else "blocked"
                detail = "; ".join([*preflight_errors, *auxiliary_drift, str(exc)])
                return _result(
                    status,
                    "uninstall",
                    changes,
                    detail,
                    restart_required=_restart_required(changes),
                    **result_context,
                )
            current = next_current
            modelconfig = next_modelconfig
            checkout_mode = next_checkout_mode
            permission_backend = next_permission_backend
            owned_backup = (
                _safe_path(backup_root, owner["backup"])
                if owner["type"] in {"managed_config", "managed_json"}
                and "backup" in owner
                else None
            )
            if owned_backup is not None and owned_backup.exists():
                owned_backup.unlink()
                _cleanup_empty(owned_backup.parent, backup_root)
            changes.extend(_preview([operation]))
            _cleanup_empty(path.parent, roots[owner["root"]])
        except (OSError, SyncError) as exc:
            status = "partial" if changes else "blocked"
            detail = "; ".join(
                [*preflight_errors, *auxiliary_drift, f"{owner['path']}: {exc}"]
            )
            return _result(
                status,
                "uninstall",
                changes,
                detail,
                restart_required=_restart_required(changes),
                **result_context,
            )
    try:
        remaining_state = _load_install_state(codex_home, orchestra_home)
        remaining_auxiliary = list(remaining_state["auxiliary_drift"])
        for root in (codex_home, orchestra_home):
            _cleanup_empty((root / "orchestra/backups"), root)
        _cleanup_empty((codex_home / "orchestra"), codex_home)
    except (OSError, SyncError) as exc:
        manifest_drift = [f"manifest: {exc}"]
        remaining_auxiliary = auxiliary_drift
    else:
        manifest_drift = []
    result_context["permission_backend"] = permission_backend
    result_context["permission_profile"] = (
        PERMISSION_PROFILE if permission_backend == "profile" else None
    )
    detail = "; ".join([*preflight_errors, *manifest_drift, *remaining_auxiliary])
    return _result(
        "partial"
        if preflight_errors or manifest_drift or remaining_auxiliary
        else "ok",
        "uninstall",
        changes,
        detail,
        restart_required=_restart_required(changes),
        **result_context,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--modelconfig", choices=MODELCONFIGS)
    status_parser.add_argument("--checkout-mode", choices=CHECKOUT_MODES)
    status_parser.add_argument("--worktree-root", type=Path)
    status_parser.add_argument("--host", choices=HOSTS, default="codex")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--dry-run", action="store_true")
    apply_parser.add_argument("--modelconfig", choices=MODELCONFIGS)
    apply_parser.add_argument("--checkout-mode", choices=CHECKOUT_MODES)
    apply_parser.add_argument("--worktree-root", type=Path)
    apply_parser.add_argument("--host", choices=HOSTS, default="codex")
    uninstall_parser = subparsers.add_parser("uninstall")
    uninstall_parser.add_argument("--host", choices=HOSTS, default="codex")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source_root = Path(__file__).resolve().parents[2]
    home = Path(os.environ["HOME"])
    codex_home = Path(os.environ.get("CODEX_HOME", str(home / ".codex")))
    host = getattr(args, "host", "codex")
    if args.command == "uninstall":
        payload = uninstall(home, codex_home, host=host)
    else:
        payload = synchronize(
            source_root,
            home,
            codex_home,
            args.command,
            dry_run=getattr(args, "dry_run", False),
            modelconfig=getattr(args, "modelconfig", None),
            checkout_mode=getattr(args, "checkout_mode", None),
            worktree_root=getattr(args, "worktree_root", None),
            host=host,
        )
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 2 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
