#!/usr/bin/env python3
"""Run one bounded delegation through the Codex, Cursor, or Grok CLI.

This helper intentionally owns only the process boundary.  It does not create
worktrees, keep task state, or decide whether an implementation is acceptable.
Git remains the authority for the checkout binding and the caller remains the
authority for delivery.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time
import tomllib
from typing import Any, Iterable
import uuid


CAPABILITIES = (
    "repository_context",
    "web_research",
    "technical_planning",
    "architecture_analysis",
    "difficult_debugging",
    "general_implementation",
    "frontend_implementation",
    "independent_review",
    "browser_acceptance",
    "runtime_verification",
)
EXECUTORS = ("cursor", "grok", "codex")
PERMISSIONS = ("default", "trusted")
IMPLEMENTATION_CAPABILITIES = frozenset(
    {"general_implementation", "frontend_implementation"}
)
READONLY_CAPABILITIES = frozenset(CAPABILITIES) - IMPLEMENTATION_CAPABILITIES
VERIFICATION_CAPABILITIES = frozenset(
    {"browser_acceptance", "runtime_verification"}
)
DEFAULT_TIMEOUT = 1800.0
MAX_STDERR_BYTES = 32 * 1024
MAX_RESULT_CHARS = 100_000
SHA_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")


class DelegateInputError(ValueError):
    """A command-line value is malformed or unsafe for this adapter."""


class DelegateUnavailable(RuntimeError):
    """A required local resource is unavailable."""


class JsonArgumentParser(argparse.ArgumentParser):
    """Report usage errors in the same JSON channel as execution results."""

    def error(self, message: str) -> None:
        _emit(
            {
                "status": "invalid",
                "reason": _compact(message, limit=500),
            }
        )
        raise SystemExit(2)


def _compact(value: str, *, limit: int = 2_000) -> str:
    return " ".join(value.split())[:limit]


def _emit(payload: dict[str, Any]) -> None:
    print(
        json.dumps(
            payload,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


def _positive_timeout(value: str) -> float:
    try:
        timeout = float(value)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError("timeout must be a positive number") from error
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive number")
    return timeout


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(
        prog=Path(sys.argv[0]).name,
        allow_abbrev=False,
        description="Run one bounded Cursor, Grok, or Codex delegation.",
    )
    parser.add_argument("--repo", help="Git worktree root (required for execution)")
    parser.add_argument("--executor", choices=EXECUTORS)
    parser.add_argument("--capability", required=True, choices=CAPABILITIES)
    parser.add_argument("--model")
    parser.add_argument(
        "--effort",
        help="Codex or Grok reasoning effort (Cursor uses its model alias)",
    )
    parser.add_argument("--preset", help="Explicitly selected execution preset")
    parser.add_argument("--presets-file", type=Path, help="Explicit alternative to the managed preset file")
    parser.add_argument("--host", choices=("codex", "cursor", "grok"))
    parser.add_argument("--tier", default="standard")
    parser.add_argument("--root-model", help="Observed root model; permits planning reuse without changing its effort")
    parser.add_argument("--independent-planning", action="store_true")
    parser.add_argument("--attempt", type=int, default=1, help="Root-selected attempt, never an automatic retry")
    parser.add_argument("--resolve-only", action="store_true", help="Return the preset assignment without starting a process")
    parser.add_argument("--prompt-file")
    parser.add_argument("--log-file")
    parser.add_argument("--expected-head")
    parser.add_argument("--resume")
    parser.add_argument("--permissions", choices=PERMISSIONS, default="default")
    parser.add_argument(
        "--output-path",
        action="append",
        default=[],
        help="Expected repo-relative output path for verification capabilities (repeatable)",
    )
    parser.add_argument("--timeout", type=_positive_timeout, default=DEFAULT_TIMEOUT)
    return parser


def default_presets_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    source = root / "config/execution-presets.toml"
    return source if source.is_file() else root / "execution-presets.toml"


def load_presets(path: Path) -> dict[str, Any]:
    """Read the one assignment source; reject typos instead of inventing routes."""
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise DelegateInputError(f"cannot read execution presets at {path}: {error}") from error
    presets = document.get("presets")
    if set(document) != {"presets"} or not isinstance(presets, dict) or not presets:
        raise DelegateInputError("execution presets must contain a non-empty presets table")
    for name, preset in presets.items():
        if not isinstance(preset, dict) or set(preset) != {"tier", "capabilities", "hosts", "escalation"}:
            raise DelegateInputError(f"invalid preset structure: {name}")
        if preset["tier"] != "standard":
            raise DelegateInputError("delegated presets currently support only the standard tier")
        rows = preset["capabilities"]
        if not isinstance(rows, dict) or set(rows) != set(CAPABILITIES):
            raise DelegateInputError(f"preset {name} must assign every capability exactly once")
        for capability, row in rows.items():
            _validate_preset_row(row, capability)
            if row["executor"] == "native":
                raise DelegateInputError("native assignments require an explicit Codex host override")
        hosts = preset["hosts"]
        if not isinstance(hosts, dict) or set(hosts) - {"codex", "cursor", "grok"}:
            raise DelegateInputError(f"invalid preset hosts: {name}")
        for host, overrides in hosts.items():
            if not isinstance(overrides, dict) or set(overrides) - set(CAPABILITIES):
                raise DelegateInputError(f"invalid capability overrides for {host}")
            for capability, row in overrides.items():
                _validate_preset_row(row, capability)
                if row["executor"] == "native" and host != "codex":
                    raise DelegateInputError("explicit native model overrides currently require Codex")
        ladder = preset["escalation"]
        eligible = IMPLEMENTATION_CAPABILITIES | {"difficult_debugging"}
        if not isinstance(ladder, dict) or set(ladder) != {"capabilities", "attempts"}:
            raise DelegateInputError("invalid escalation structure")
        capabilities = ladder["capabilities"]
        if (not isinstance(capabilities, list) or not capabilities
                or any(not isinstance(item, str) or item not in eligible for item in capabilities)
                or len(set(capabilities)) != len(capabilities)):
            raise DelegateInputError("escalation is limited to implementation and difficult debugging")
        attempts = ladder["attempts"]
        if not isinstance(attempts, list) or len(attempts) != 2:
            raise DelegateInputError("escalation requires exactly two recovery assignments")
        for row in attempts:
            for capability in capabilities:
                _validate_preset_row(row, capability)
            if row["executor"] not in EXECUTORS:
                raise DelegateInputError("recovery assignments must identify an executor and model")
    return presets


def _validate_preset_row(row: Any, capability: str) -> None:
    allowed = {"executor", "model", "reasoning_effort", "prefer_native", "reuse_root"}
    if not isinstance(row, dict) or set(row) - allowed:
        raise DelegateInputError(f"invalid preset assignment for {capability}")
    executor = row.get("executor")
    if executor not in (*EXECUTORS, "native", "host"):
        raise DelegateInputError(f"invalid preset executor for {capability}")
    if executor == "host":
        if set(row) != {"executor"}:
            raise DelegateInputError("host assignments use the host matrix without model overrides")
    else:
        if not isinstance(row.get("model"), str):
            raise DelegateInputError(f"preset model is missing for {capability}")
        _validate_model(row["model"])
        effort = row.get("reasoning_effort")
        if effort is not None and (not isinstance(effort, str) or effort not in {
            "none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"
        }):
            raise DelegateInputError(f"invalid preset effort for {capability}")
        if executor == "cursor" and effort is not None:
            raise DelegateInputError("Cursor preset effort must be encoded in its exact model alias")
    for key in ("prefer_native", "reuse_root"):
        if key in row and type(row[key]) is not bool:
            raise DelegateInputError(f"{key} must be boolean")
    if row.get("prefer_native") and executor != "codex":
        raise DelegateInputError("prefer_native requires the Codex executor")
    if row.get("reuse_root") and capability not in {"technical_planning", "architecture_analysis"}:
        raise DelegateInputError("only planning and architecture may reuse the root")
    if capability == "browser_acceptance" and executor not in {"host", "native"}:
        raise DelegateInputError("preset browser acceptance must stay in the owning host")


def resolve_preset(args: argparse.Namespace) -> dict[str, Any]:
    """Resolve one user-selected attempt; no history, launches, or retries."""
    if args.host is None:
        raise DelegateInputError("--host is required with --preset")
    if any(value is not None for value in (args.executor, args.model, args.effort)):
        raise DelegateInputError("use either --preset or explicit executor/model/effort")
    presets = load_presets(args.presets_file or default_presets_path())
    if args.preset not in presets:
        raise DelegateInputError(f"unknown execution preset: {args.preset}")
    preset = presets[args.preset]
    if args.tier != preset["tier"]:
        raise DelegateInputError("execution preset does not support the selected tier")
    ladder = preset["escalation"]
    limit = 3 if args.capability in ladder["capabilities"] else 1
    if args.attempt < 1 or args.attempt > limit:
        raise DelegateInputError(f"{args.capability} accepts attempts 1..{limit}; no further automatic escalation")
    row = preset["hosts"].get(args.host, {}).get(
        args.capability, preset["capabilities"][args.capability]
    )
    if args.attempt > 1:
        row = ladder["attempts"][args.attempt - 2]
    executor = row["executor"]
    effort = row.get("reasoning_effort")
    if row.get("reuse_root") and args.root_model == row.get("model") and not args.independent_planning:
        executor, effort = "root", None  # The launcher, not Orchestra, owns root effort.
    elif row.get("prefer_native") and args.host == "codex":
        executor = "native"
    profile = (
        "orchestra_implementation_worker" if args.capability in IMPLEMENTATION_CAPABILITIES
        else "orchestra_verifier" if args.capability in VERIFICATION_CAPABILITIES
        else "orchestra_reviewer" if args.capability == "independent_review"
        else "orchestra_analyst"
    )
    return {
        "status": "ok", "preset": args.preset, "tier": args.tier,
        "host": args.host, "capability": args.capability, "attempt": args.attempt,
        "executor": executor, "model": row.get("model"),
        "reasoning_effort": effort, "profile": profile,
    }


def _contains_control(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def _safe_argument(value: str, label: str) -> str:
    if not value or "\x00" in value or _contains_control(value):
        raise DelegateInputError(f"{label} must be a non-empty safe value")
    if value.startswith("-"):
        raise DelegateInputError(f"{label} cannot start with '-'")
    return value


_SYSTEM_PATH_ALIASES = frozenset({Path("/tmp"), Path("/var")})


def _path_has_symlink(path: Path) -> bool:
    """Return whether a user-controlled path component is a symbolic link.

    macOS exposes /tmp and /var as symlinks into /private.  Those aliases are
    safe to canonicalize and must remain usable for private prompt/log files;
    a symlink at any other component is rejected to avoid path redirection.
    """
    absolute = Path(os.path.abspath(path))
    current = Path(absolute.anchor)
    for component in absolute.parts[1:]:
        current /= component
        try:
            if current.is_symlink():
                if current not in _SYSTEM_PATH_ALIASES:
                    return True
        except OSError:
            return True
    return False


def _absolute_path(raw: str, label: str) -> Path:
    _safe_argument(raw, label)
    path = Path(raw)
    if not path.is_absolute():
        path = Path.cwd() / path
    path = Path(os.path.abspath(path))
    if _path_has_symlink(path):
        raise DelegateInputError(f"{label} cannot use a symbolic-link path")
    try:
        return Path(os.path.realpath(path))
    except OSError as error:
        raise DelegateInputError(f"cannot resolve {label}: {error}") from error


def _inside(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def _run_git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            ["git", "-C", os.fspath(repo), *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as error:
        raise DelegateUnavailable(f"cannot run git: {error}") from error


def _git_worktree_and_head(repo: Path) -> tuple[Path, str]:
    if not repo.exists() or not repo.is_dir() or repo.is_symlink():
        raise DelegateInputError("repo must be an existing regular directory")
    root_result = _run_git(repo, "rev-parse", "--show-toplevel")
    if root_result.returncode:
        raise DelegateUnavailable(
            f"repo is not a Git worktree: {_compact(root_result.stderr.decode(errors='replace'))}"
        )
    try:
        actual_root = Path(os.fsdecode(root_result.stdout).strip()).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise DelegateUnavailable(f"cannot resolve Git worktree root: {error}") from error
    if actual_root != repo:
        raise DelegateInputError("repo must be the Git worktree root")
    head_result = _run_git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    head = os.fsdecode(head_result.stdout).strip()
    if head_result.returncode or SHA_RE.fullmatch(head) is None:
        detail = _compact(
            os.fsdecode(head_result.stderr).strip()
            or os.fsdecode(head_result.stdout).strip()
            or "HEAD is unavailable"
        )
        raise DelegateUnavailable(f"cannot resolve Git HEAD: {detail}")
    return actual_root, head


@dataclass(frozen=True)
class WorktreeSnapshot:
    """Worktree content and index state at one point in time."""

    fingerprints: dict[str, str]
    tracked_paths: frozenset[str]
    index_entries: dict[str, tuple[bytes, ...]]


def _git_paths(repo: Path, *, tracked: bool) -> list[str]:
    if tracked:
        arguments = ("ls-files", "--cached", "-z")
    else:
        arguments = ("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    result = _run_git(repo, *arguments)
    if result.returncode:
        raise DelegateUnavailable(
            f"cannot inspect Git worktree: {_compact(os.fsdecode(result.stderr))}"
        )
    raw_paths = result.stdout.split(b"\0")
    if raw_paths and raw_paths[-1] == b"":
        raw_paths.pop()
    return [os.fsdecode(raw_path) for raw_path in raw_paths]


def _git_index_entries(repo: Path) -> dict[str, tuple[bytes, ...]]:
    """Return the complete staged entry set, including unmerged stages."""
    result = _run_git(repo, "ls-files", "--stage", "-z")
    if result.returncode:
        raise DelegateUnavailable(
            f"cannot inspect Git index: {_compact(os.fsdecode(result.stderr))}"
        )
    entries: dict[str, list[bytes]] = {}
    for raw_entry in result.stdout.split(b"\0"):
        if not raw_entry:
            continue
        try:
            metadata, raw_path = raw_entry.split(b"\t", 1)
        except ValueError:
            raise DelegateUnavailable("cannot parse Git index entries")
        entries.setdefault(os.fsdecode(raw_path), []).append(metadata)
    return {path: tuple(values) for path, values in entries.items()}


def _path_fingerprint(repo: Path, relative: str) -> str:
    """Hash path kind, mode, and content without following a symlink."""
    candidate = repo / Path(relative)
    hasher = hashlib.sha256()
    hasher.update(relative.encode("utf-8", "surrogateescape"))
    try:
        info = os.lstat(candidate)
    except FileNotFoundError:
        hasher.update(b"\\0missing")
        return hasher.hexdigest()
    except OSError as error:
        hasher.update(f"\\0error:{error.errno}".encode())
        return hasher.hexdigest()

    hasher.update(f"\\0mode:{stat.S_IFMT(info.st_mode)}:{stat.S_IMODE(info.st_mode)}".encode())
    if stat.S_ISREG(info.st_mode):
        try:
            descriptor = os.open(
                candidate,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            )
            with os.fdopen(descriptor, "rb") as stream:
                while True:
                    chunk = stream.read(1024 * 1024)
                    if not chunk:
                        break
                    hasher.update(chunk)
        except OSError as error:
            hasher.update(f"\\0error:{error.errno}".encode())
    elif stat.S_ISLNK(info.st_mode):
        try:
            hasher.update(os.fsencode(os.readlink(candidate)))
        except OSError as error:
            hasher.update(f"\\0error:{error.errno}".encode())
    else:
        hasher.update(f"\\0size:{info.st_size}".encode())
    return hasher.hexdigest()


def snapshot_worktree(repo: Path) -> WorktreeSnapshot:
    """Capture a content fingerprint for tracked and non-ignored paths."""
    all_paths = _git_paths(repo, tracked=False)
    tracked_paths = frozenset(_git_paths(repo, tracked=True))
    index_entries = _git_index_entries(repo)
    fingerprints = {
        relative: _path_fingerprint(repo, relative)
        for relative in sorted(set(all_paths))
    }
    return WorktreeSnapshot(fingerprints, tracked_paths, index_entries)


def changed_paths(before: WorktreeSnapshot, after: WorktreeSnapshot) -> list[str]:
    paths = set(before.fingerprints) | set(after.fingerprints)
    return sorted(
        path
        for path in paths
        if before.fingerprints.get(path) != after.fingerprints.get(path)
    )


def index_changed_paths(before: WorktreeSnapshot, after: WorktreeSnapshot) -> list[str]:
    paths = set(before.index_entries) | set(after.index_entries)
    return sorted(
        path
        for path in paths
        if before.index_entries.get(path) != after.index_entries.get(path)
    )


def _read_prompt(path: Path) -> str:
    if not path.exists() or not path.is_file() or path.is_symlink():
        raise DelegateInputError("prompt-file must be an existing regular file")
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise DelegateInputError(f"cannot read prompt-file: {error}") from error


def _prepare_log(path: Path, repo: Path) -> Any:
    """Create one private diagnostic log without following or overwriting it."""
    if _inside(path, repo):
        raise DelegateInputError("log-file must be outside the repository")
    parent = path.parent
    if _path_has_symlink(parent):
        raise DelegateInputError("log-file parent cannot use a symbolic-link path")
    if not parent.exists() or not parent.is_dir() or parent.is_symlink():
        raise DelegateInputError("log-file parent must be an existing regular directory")
    try:
        descriptor = os.open(
            path,
            os.O_WRONLY
            | os.O_APPEND
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except FileExistsError as error:
        raise DelegateInputError("log-file must name a new private file") from error
    except OSError as error:
        raise DelegateInputError(f"cannot open log-file: {error}") from error
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise DelegateInputError("log-file must be a regular file")
        os.fchmod(descriptor, 0o600)
        return os.fdopen(descriptor, "ab", buffering=0)
    except Exception:
        os.close(descriptor)
        raise


def _boundary_prompt(repo: Path, capability: str, prompt: str) -> str:
    return (
        "You are a delegated scoped role operating in the repository at "
        f"{repo}. Your assigned capability is {capability}.\n"
        "Work only within the requested scope and report concrete evidence, "
        "blockers, and any unresolved uncertainty. Do not use memory, omem, "
        "or further agents. Do not commit, push, merge, create worktrees, "
        "change production systems, or expand the requested scope. These are "
        "task instructions; process permissions and checkout checks are "
        "enforced separately by the adapter. Runtime and browser verification "
        "may execute checks, but remain source-read-only; declare any expected "
        "new report path explicitly.\n\n"
        "Delegated request:\n"
        f"{prompt}"
    )


def _validate_resume(value: str | None) -> str | None:
    if value is None:
        return None
    return _safe_argument(value, "resume session ID")


def _validate_model(value: str, label: str = "model") -> str:
    return _safe_argument(value, label)


def _validate_output_paths(
    repo: Path, capability: str, values: Iterable[str] | None
) -> tuple[str, ...]:
    raw_values = tuple(values or ())
    if raw_values and capability not in VERIFICATION_CAPABILITIES:
        raise DelegateInputError("--output-path is only valid for verification capabilities")
    normalized: list[str] = []
    for raw_value in raw_values:
        value = _safe_argument(raw_value, "output-path")
        relative = Path(value)
        if relative.is_absolute() or not relative.parts or any(
            part in {"", ".", ".."} for part in relative.parts
        ):
            raise DelegateInputError("output-path must be a repo-relative file path")
        candidate = repo / relative
        if _path_has_symlink(candidate):
            raise DelegateInputError("output-path cannot use a symbolic-link path")
        normalized_value = relative.as_posix()
        if normalized_value not in normalized:
            normalized.append(normalized_value)
    return tuple(normalized)


def _write_prompt_file(content: str) -> Path:
    try:
        descriptor, raw_path = tempfile.mkstemp(
            prefix="orchestra-delegate-",
            suffix=".prompt",
        )
        path = Path(raw_path)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
        os.chmod(path, 0o600)
        return path
    except OSError as error:
        raise DelegateUnavailable(f"cannot prepare delegated prompt: {error}") from error


def build_command(
    *,
    executor: str,
    repo: Path,
    model: str,
    capability: str,
    permissions: str,
    prompt: str,
    resume: str | None = None,
    effort: str | None = None,
    grok_prompt_file: Path | None = None,
    session_id: str | None = None,
) -> list[str]:
    """Build argv without invoking a shell or implicit continuation."""
    if executor not in EXECUTORS:
        raise DelegateInputError(f"unsupported executor: {executor}")
    if capability not in CAPABILITIES:
        raise DelegateInputError(f"unsupported capability: {capability}")
    if permissions not in PERMISSIONS:
        raise DelegateInputError(f"unsupported permissions: {permissions}")
    model = _validate_model(model)
    resume = _validate_resume(resume)
    if effort is not None:
        effort = _safe_argument(effort, "effort")
    if executor == "cursor" and effort is not None:
        raise DelegateInputError("effort is only supported for codex or grok")

    if executor == "codex":
        if capability == "browser_acceptance":
            raise DelegateInputError("Codex CLI delegation does not provide the owning host's browser")
        if resume is not None:
            try:
                uuid.UUID(resume)
            except ValueError as error:
                raise DelegateInputError("Codex resume requires an exact session UUID") from error
        command = ["codex", "exec"]
        # Exec-level flags precede resume; its subcommand has no --cd/--sandbox.
        # Explicit permissions are reapplied on resume, never inherited from
        # an implementation session when requesting a read-only capability.
        readonly = capability in READONLY_CAPABILITIES and capability not in VERIFICATION_CAPABILITIES
        if readonly:
            command.extend(("--sandbox", "read-only", "-c", 'approval_policy="never"'))
        elif permissions == "trusted":
            command.extend(("--sandbox", "danger-full-access", "-c", 'approval_policy="never"'))
        command.extend(("--cd", os.fspath(repo)))
        if resume is not None:
            command.extend(("resume", resume))
        command.extend(("--json", "--model", model))
        if effort is not None:
            command.extend(("-c", "model_reasoning_effort=" + json.dumps(effort)))
        command.append(prompt)
        return command

    if executor == "cursor":
        command = [
            "cursor-agent",
            "--print",
            "--output-format",
            "stream-json",
            "--model",
            model,
            "--workspace",
            os.fspath(repo),
        ]
        if permissions == "trusted":
            command.extend(("--trust",))
        if capability in READONLY_CAPABILITIES and capability not in VERIFICATION_CAPABILITIES:
            command.extend(("--mode", "ask"))
        elif permissions == "trusted" and (
            capability in IMPLEMENTATION_CAPABILITIES
            or capability in VERIFICATION_CAPABILITIES
        ):
            command.extend(("--force",))
        if resume is not None:
            command.extend(("--resume", resume))
        command.append(prompt)
        return command

    command = [
        "grok",
        "--output-format",
        "streaming-json",
        "--model",
        model,
        "--cwd",
        os.fspath(repo),
    ]
    if effort is not None:
        command.extend(("--reasoning-effort", effort))
    if resume is not None:
        command.extend(("--resume", resume))
    if capability in VERIFICATION_CAPABILITIES:
        if permissions == "trusted":
            command.extend(("--permission-mode", "bypassPermissions", "--no-subagents"))
        else:
            command.extend(("--permission-mode", "default", "--no-subagents"))
    elif capability in READONLY_CAPABILITIES:
        # Analysis and review stay in Grok's source-read-only plan mode.
        command.extend(("--permission-mode", "plan", "--no-subagents"))
    elif permissions == "trusted":
        command.extend(("--permission-mode", "bypassPermissions", "--no-subagents"))
    else:
        command.extend(("--permission-mode", "default", "--no-subagents"))
    if session_id is not None:
        if resume is not None:
            raise DelegateInputError("new Grok session cannot combine resume and session-id")
        command.extend(("--session-id", _safe_argument(session_id, "session ID")))
    if grok_prompt_file is None:
        raise DelegateInputError("Grok requires a prepared prompt file")
    command.extend(("--prompt-file", os.fspath(grok_prompt_file)))
    return command


@dataclass
class ProtocolCapture:
    executor: str
    requested_model: str
    session_id: str | None = None
    observed_model: str | None = None
    final_result: str | None = None
    final_seen: bool = False
    terminal_seen: bool = False
    failure_detail: str | None = None
    stop_reason: str | None = None
    _pending: bytes = b""
    _text_parts: list[str] | None = None
    _metadata_sent: tuple[str | None, str | None] | None = None

    def __post_init__(self) -> None:
        self._text_parts = []

    def _metadata(self) -> None:
        current = (self.session_id, self.observed_model)
        if current == self._metadata_sent or current == (None, None):
            return
        self._metadata_sent = current
        values = []
        if self.session_id is not None:
            values.append(f"session_id={_compact(self.session_id, limit=200)}")
        if self.observed_model is not None:
            values.append(f"model={_compact(self.observed_model, limit=200)}")
        print(f"delegate: executor={self.executor} {' '.join(values)}", file=sys.stderr, flush=True)

    @staticmethod
    def _string_value(value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        try:
            return json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        except (TypeError, ValueError):
            return str(value)

    def _cursor_event(self, event: dict[str, Any]) -> None:
        session = event.get("session_id")
        if isinstance(session, str) and session:
            self.session_id = session
        model = event.get("model")
        if isinstance(model, str) and model:
            self.observed_model = model
        self._metadata()

        if event.get("type") == "result":
            self.terminal_seen = True
            result = self._string_value(event.get("result"))
            valid_result = bool(result and result.strip())
            if (
                event.get("subtype") == "success"
                and event.get("is_error") is False
                and valid_result
            ):
                self.final_seen = True
                self.final_result = result
            else:
                self.failure_detail = (
                    result
                    or self._string_value(event.get("subtype"))
                    or "invalid Cursor terminal result"
                )

    def _grok_event(self, event: dict[str, Any]) -> None:
        session = event.get("sessionId") or event.get("session_id")
        if isinstance(session, str) and session:
            self.session_id = session

        model_usage = event.get("modelUsage")
        if isinstance(model_usage, dict) and model_usage:
            model_names = [str(name) for name in model_usage]
            self.observed_model = model_names[0]
        model = event.get("model")
        if isinstance(model, str) and model:
            self.observed_model = model
        self._metadata()

        event_type = event.get("type")
        if event_type == "text":
            data = event.get("data")
            if isinstance(data, str):
                assert self._text_parts is not None
                self._text_parts.append(data)
        elif event_type == "end":
            self.terminal_seen = True
            self.stop_reason = str(event.get("stopReason")) if event.get("stopReason") else None
            result = self._string_value(event.get("result"))
            if not result and self._text_parts:
                result = "".join(self._text_parts)
            if self.stop_reason == "end_turn" and result and result.strip():
                self.final_seen = True
                self.final_result = result
            else:
                self.failure_detail = self.stop_reason or "invalid Grok terminal result"
        elif event_type in {"error", "failure"}:
            self.failure_detail = self._string_value(
                event.get("message") or event.get("data") or event.get("error")
            )

    def _codex_event(self, event: dict[str, Any]) -> None:
        event_type = event.get("type")
        if event_type == "thread.started":
            session = event.get("thread_id")
            if isinstance(session, str) and session:
                self.session_id = session
            self._metadata()
        elif event_type == "turn.started":
            self.final_result = None
            self.final_seen = False
        elif event_type == "item.completed":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message":
                message = item.get("text")
                if isinstance(message, str) and message.strip():
                    self.final_result = message
        elif event_type == "turn.completed":
            self.terminal_seen = True
            self.stop_reason = "completed"
            self.final_seen = bool(self.final_result and self.final_result.strip())
            if not self.final_seen:
                self.failure_detail = "Codex turn completed without an agent result"
        elif event_type in {"turn.failed", "error"}:
            self.terminal_seen = event_type == "turn.failed"
            self.failure_detail = self._string_value(event.get("error") or event.get("message")) or "Codex execution failed"

    def _event(self, event: object) -> None:
        if not isinstance(event, dict):
            return
        if self.executor == "cursor":
            self._cursor_event(event)
        elif self.executor == "codex":
            self._codex_event(event)
        else:
            self._grok_event(event)

    def feed(self, data: bytes) -> None:
        self._pending += data
        while b"\n" in self._pending:
            line, self._pending = self._pending.split(b"\n", 1)
            self._line(line)

    def finish(self) -> None:
        if self._pending:
            self._line(self._pending)
            self._pending = b""

    def _line(self, line: bytes) -> None:
        try:
            value = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        self._event(value)


@dataclass
class ProcessCapture:
    protocol: ProtocolCapture
    exit_code: int | None
    stderr: str
    timed_out: bool = False
    cancelled: bool = False
    transport_error: str | None = None


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    """Terminate only the process group created for this one delegation."""
    if os.name != "posix":
        if process.poll() is None:
            try:
                process.terminate()
            except (OSError, ProcessLookupError):
                pass
        return

    def group_exists() -> bool:
        process.poll()
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return False
        except OSError:
            return True
        return True

    # The leader can already have exited while a descendant keeps the pipes
    # open.  Always signal the owned process group before checking its leader.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except OSError:
        pass
    deadline = time.monotonic() + 1.0
    while group_exists() and time.monotonic() < deadline:
        time.sleep(0.02)
    if group_exists():
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            pass


def _read_ready(
    selector: selectors.BaseSelector,
    key: selectors.SelectorKey,
    protocol: ProtocolCapture,
    log_stream: Any,
    stderr_buffer: bytearray,
) -> None:
    stream = key.fileobj
    try:
        data = os.read(stream.fileno(), 64 * 1024)
    except OSError:
        # A read error is transport failure, not an orderly EOF.  Let the
        # process runner capture it and still complete group cleanup/snapshot.
        raise
    if not data:
        try:
            selector.unregister(stream)
        except Exception:
            pass
        try:
            stream.close()
        except OSError:
            pass
        return
    if key.data == "stdout":
        log_stream.write(data)
        log_stream.flush()
        protocol.feed(data)
    else:
        remaining = MAX_STDERR_BYTES - len(stderr_buffer)
        if remaining > 0:
            stderr_buffer.extend(data[:remaining])


def _run_process(
    command: list[str],
    repo: Path,
    executor: str,
    model: str,
    log_stream: Any,
    timeout: float,
) -> ProcessCapture:
    protocol = ProtocolCapture(executor=executor, requested_model=model)
    stderr_buffer = bytearray()
    try:
        process = subprocess.Popen(
            command,
            cwd=repo,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            close_fds=True,
        )
    except OSError as error:
        raise DelegateUnavailable(f"cannot launch {executor}: {error}") from error

    assert process.stdout is not None and process.stderr is not None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, "stdout")
    selector.register(process.stderr, selectors.EVENT_READ, "stderr")
    timed_out = False
    cancelled = False
    transport_error: str | None = None
    deadline = time.monotonic() + timeout
    previous_handlers: dict[int, Any] = {}

    def interrupt_handler(signum: int, _frame: Any) -> None:
        nonlocal cancelled
        cancelled = True
        raise KeyboardInterrupt

    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, interrupt_handler)
        except (AttributeError, OSError, ValueError):
            pass
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                _terminate_process_group(process)
                break
            events = selector.select(min(remaining, 0.25))
            if not events and process.poll() is not None:
                continue
            for key, _ in events:
                _read_ready(selector, key, protocol, log_stream, stderr_buffer)
    except KeyboardInterrupt:
        cancelled = True
    except BaseException as error:
        transport_error = f"{type(error).__name__}: {_compact(str(error), limit=500)}"
    finally:
        if timed_out or cancelled or transport_error is not None:
            try:
                _terminate_process_group(process)
            except BaseException as error:
                if transport_error is None:
                    transport_error = (
                        f"{type(error).__name__}: {_compact(str(error), limit=500)}"
                    )

        # Drain already-written events after interruption while bounding cleanup
        # of a child that retained a pipe.  Diagnostics must not prevent group
        # cleanup or the post-execution checkout snapshot.
        try:
            drain_deadline = time.monotonic() + 1.0
            while selector.get_map() and time.monotonic() < drain_deadline:
                events = selector.select(0.05)
                for key, _ in events:
                    try:
                        _read_ready(selector, key, protocol, log_stream, stderr_buffer)
                    except BaseException as error:
                        if transport_error is None:
                            transport_error = (
                                f"{type(error).__name__}: {_compact(str(error), limit=500)}"
                            )
                        try:
                            _terminate_process_group(process)
                        except BaseException:
                            pass
                        break
        except BaseException as error:
            if transport_error is None:
                transport_error = f"{type(error).__name__}: {_compact(str(error), limit=500)}"
        for key in list(selector.get_map().values()):
            try:
                selector.unregister(key.fileobj)
            except BaseException:
                pass
            try:
                key.fileobj.close()
            except BaseException:
                pass
        try:
            selector.close()
        except BaseException:
            pass
        # Always reap the owned process group: a normal leader exit can leave a
        # descendant alive with inherited stdout/stderr descriptors.
        try:
            _terminate_process_group(process)
        except BaseException as error:
            if transport_error is None:
                transport_error = f"{type(error).__name__}: {_compact(str(error), limit=500)}"
        try:
            process.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            try:
                _terminate_process_group(process)
            except BaseException:
                pass
            try:
                process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                pass
        except BaseException as error:
            if transport_error is None:
                transport_error = f"{type(error).__name__}: {_compact(str(error), limit=500)}"
        try:
            protocol.finish()
        except BaseException as error:
            if transport_error is None:
                transport_error = f"{type(error).__name__}: {_compact(str(error), limit=500)}"
        for signum, previous in previous_handlers.items():
            try:
                signal.signal(signum, previous)
            except (AttributeError, OSError, ValueError):
                pass
    return ProcessCapture(
        protocol=protocol,
        exit_code=process.returncode,
        stderr=bytes(stderr_buffer).decode("utf-8", errors="replace"),
        timed_out=timed_out,
        cancelled=cancelled,
        transport_error=transport_error,
    )


AUTH_FAILURE_MARKERS = (
    "authentication",
    "unauthorized",
    "not authenticated",
    "login required",
    "api key",
    "credential",
    "sign in",
)
PERMISSION_FAILURE_MARKERS = (
    "permission denied",
    "approval denied",
    "access denied",
    "not permitted",
)
QUOTA_FAILURE_MARKERS = (
    "quota",
    "rate limit",
    "usage limit",
    "billing",
    "too many requests",
    "capacity exceeded",
)


def _blocked_failure(text: str) -> bool:
    lowered = text.casefold()
    return any(
        marker in lowered
        for marker in AUTH_FAILURE_MARKERS
        + PERMISSION_FAILURE_MARKERS
        + QUOTA_FAILURE_MARKERS
    )


def _reason_append(reasons: list[str], value: str) -> None:
    compacted = _compact(value, limit=500)
    if compacted and compacted not in reasons:
        reasons.append(compacted)


def _result_payload(
    *,
    args: argparse.Namespace,
    before_head: str | None,
    after_head: str | None,
    before_snapshot: WorktreeSnapshot | None,
    after_snapshot: WorktreeSnapshot | None,
    process_capture: ProcessCapture | None,
    allocated_session_id: str | None,
    status: str,
    reasons: Iterable[str] = (),
    failure: str | None = None,
) -> dict[str, Any]:
    protocol = process_capture.protocol if process_capture is not None else None
    paths: list[str] = []
    source_paths: list[str] = []
    staged_paths: list[str] = []
    if before_snapshot is not None and after_snapshot is not None:
        paths = changed_paths(before_snapshot, after_snapshot)
        tracked = before_snapshot.tracked_paths | after_snapshot.tracked_paths
        source_paths = sorted(path for path in paths if path in tracked)
        staged_paths = index_changed_paths(before_snapshot, after_snapshot)
    result = protocol.final_result if protocol is not None else None
    if result is not None:
        result = result[:MAX_RESULT_CHARS]
    observed_model = protocol.observed_model if protocol is not None else None
    payload: dict[str, Any] = {
        "status": status,
        "executor": args.executor,
        "capability": args.capability,
        "permissions": args.permissions,
        "requested_model": args.model,
        "observed_model": observed_model,
        "session_id": protocol.session_id if protocol is not None else None,
        "allocated_session_id": allocated_session_id,
        "log_file": args.log_file,
        "exit_code": process_capture.exit_code if process_capture is not None else None,
        "before_head": before_head,
        "after_head": after_head,
        "expected_head": args.expected_head,
        "changed_paths": paths,
        "source_changed_paths": source_paths,
        "index_changed_paths": staged_paths,
        "index_changed": bool(staged_paths),
        "output_paths": list(getattr(args, "output_paths", ()) or ()),
        "result": result,
        "terminal_seen": bool(protocol and protocol.terminal_seen),
        "final_seen": bool(protocol and protocol.final_seen),
        "stop_reason": protocol.stop_reason if protocol is not None else None,
        "timed_out": bool(process_capture and process_capture.timed_out),
        "cancelled": bool(process_capture and process_capture.cancelled),
        "transport_error": process_capture.transport_error if process_capture else None,
    }
    all_reasons = list(reasons)
    if failure:
        payload["failure"] = failure[:2_000]
        _reason_append(all_reasons, failure)
    if all_reasons:
        payload["reason"] = "; ".join(all_reasons)[:2_000]
    if process_capture is not None and process_capture.stderr and status != "ok":
        payload["stderr"] = process_capture.stderr[:MAX_STDERR_BYTES]
    return payload


def execute(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    """Validate, run, and summarize one delegation."""
    repo = _absolute_path(args.repo, "repo")
    prompt_path = _absolute_path(args.prompt_file, "prompt-file")
    log_path = _absolute_path(args.log_file, "log-file")
    args.log_file = os.fspath(log_path)
    args.model = _validate_model(args.model)
    if args.effort is not None:
        args.effort = _safe_argument(args.effort, "effort")
    args.resume = _validate_resume(args.resume)
    if args.executor == "cursor" and args.effort is not None:
        raise DelegateInputError("effort is only supported for codex or grok")
    if SHA_RE.fullmatch(args.expected_head) is None:
        raise DelegateInputError("expected-head must be a full commit SHA")

    repo, before_head = _git_worktree_and_head(repo)
    args.output_paths = _validate_output_paths(
        repo,
        args.capability,
        getattr(args, "output_path", ()),
    )
    if before_head != args.expected_head:
        payload = _result_payload(
            args=args,
            before_head=before_head,
            after_head=before_head,
            before_snapshot=None,
            after_snapshot=None,
            process_capture=None,
            allocated_session_id=None,
            status="blocked",
            reasons=("HEAD does not match expected-head; delegation was not started",),
        )
        return payload, 1
    if _inside(log_path, repo):
        raise DelegateInputError("log-file must be outside the repository")
    prompt = _boundary_prompt(repo, args.capability, _read_prompt(prompt_path))
    before_snapshot = snapshot_worktree(repo)
    if args.output_paths:
        existing_output_paths = sorted(
            path
            for path in args.output_paths
            if path in before_snapshot.tracked_paths or path in before_snapshot.fingerprints
        )
        if existing_output_paths:
            raise DelegateInputError(
                "--output-path must name a new untracked output file: "
                + ", ".join(existing_output_paths)
            )

    allocated_session_id: str | None = None
    temporary_prompt: Path | None = None
    process_capture: ProcessCapture | None = None
    log_stream: Any | None = None
    reasons: list[str] = []
    status = "ok"
    failure: str | None = None
    try:
        if args.executor == "grok" and args.resume is None:
            allocated_session_id = str(uuid.uuid4())
            temporary_prompt = _write_prompt_file(prompt)
        elif args.executor == "grok":
            temporary_prompt = _write_prompt_file(prompt)
        command = build_command(
            executor=args.executor,
            repo=repo,
            model=args.model,
            capability=args.capability,
            permissions=args.permissions,
            prompt=prompt,
            resume=args.resume,
            effort=args.effort,
            grok_prompt_file=temporary_prompt,
            session_id=allocated_session_id,
        )
        if allocated_session_id is not None:
            print(
                f"delegate: executor=grok allocated_session_id={_compact(allocated_session_id, limit=200)}",
                file=sys.stderr,
                flush=True,
            )
        log_stream = _prepare_log(log_path, repo)
        process_capture = _run_process(
            command,
            repo,
            args.executor,
            args.model,
            log_stream,
            args.timeout,
        )
    except DelegateUnavailable as error:
        status = "blocked"
        failure = str(error)
    finally:
        if log_stream is not None:
            try:
                log_stream.close()
            except OSError as error:
                status = "partial" if status == "ok" else status
                _reason_append(reasons, f"cannot close delegation log: {error}")
        if temporary_prompt is not None:
            try:
                temporary_prompt.unlink()
            except FileNotFoundError:
                pass
            except OSError:
                # The temporary prompt is disposable; preserve execution result.
                pass

    after_head: str | None
    after_snapshot: WorktreeSnapshot | None
    try:
        _, after_head = _git_worktree_and_head(repo)
        after_snapshot = snapshot_worktree(repo)
    except (DelegateInputError, DelegateUnavailable) as error:
        after_head = None
        after_snapshot = None
        _reason_append(reasons, f"cannot inspect checkout after delegation: {error}")
        status = "blocked"

    if process_capture is not None:
        protocol = process_capture.protocol
        failure_text = " ".join(
            value
            for value in (process_capture.stderr, protocol.failure_detail)
            if value
        )
        if process_capture.cancelled:
            status = "partial" if status == "ok" else status
            _reason_append(reasons, "delegation cancelled")
        if process_capture.transport_error:
            status = "partial" if status == "ok" else status
            _reason_append(reasons, "delegation transport failed: " + process_capture.transport_error)
        elif process_capture.timed_out:
            status = "partial" if status == "ok" else status
            _reason_append(reasons, f"delegation timed out after {args.timeout:g} seconds")
        elif process_capture.exit_code != 0:
            if _blocked_failure(failure_text):
                status = "blocked"
                _reason_append(reasons, "executor reported an authentication, permission, or quota failure")
            else:
                status = "partial" if status == "ok" else status
                _reason_append(reasons, f"executor exited with code {process_capture.exit_code}")
        elif not protocol.final_seen:
            status = "partial" if status == "ok" else status
            _reason_append(
                reasons,
                "executor exited without a final result (terminal evidence missing or invalid)",
            )
        elif protocol.failure_detail:
            if _blocked_failure(protocol.failure_detail + " " + process_capture.stderr):
                status = "blocked"
                _reason_append(reasons, "executor reported an authentication, permission, or quota failure")
            else:
                status = "partial" if status == "ok" else status
                failure = protocol.failure_detail
        if failure is None and protocol.failure_detail:
            failure = protocol.failure_detail

    if before_snapshot is not None and after_snapshot is not None:
        paths = changed_paths(before_snapshot, after_snapshot)
        staged_paths = index_changed_paths(before_snapshot, after_snapshot)
        tracked = before_snapshot.tracked_paths | after_snapshot.tracked_paths
        source_paths = [path for path in paths if path in tracked]
        unauthorized: list[str] = []
        if args.capability in READONLY_CAPABILITIES:
            allowed = set(args.output_paths) if args.capability in VERIFICATION_CAPABILITIES else set()
            unauthorized = [path for path in paths if path not in allowed]
        if unauthorized:
            status = "blocked"
            _reason_append(
                reasons,
                (
                    "read-only delegation changed non-output paths: "
                    if args.capability in VERIFICATION_CAPABILITIES
                    else "read-only delegation changed paths: "
                )
                + ", ".join(unauthorized[:20]),
            )
        if args.capability in READONLY_CAPABILITIES and staged_paths:
            status = "blocked"
            _reason_append(
                reasons,
                "read-only delegation changed index paths: "
                + ", ".join(staged_paths[:20]),
            )
    if after_head is not None and after_head != args.expected_head:
        status = "blocked"
        _reason_append(reasons, "HEAD changed during delegation")

    payload = _result_payload(
        args=args,
        before_head=before_head,
        after_head=after_head,
        before_snapshot=before_snapshot,
        after_snapshot=after_snapshot,
        process_capture=process_capture,
        allocated_session_id=allocated_session_id,
        status=status,
        reasons=reasons,
        failure=failure,
    )
    return payload, 0 if status == "ok" else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        route = None
        if args.preset:
            route = resolve_preset(args)
            if args.resolve_only:
                _emit(route)
                return 0
            if route["executor"] not in EXECUTORS:
                raise DelegateInputError("resolved assignment requires root/native host execution; use --resolve-only and the host adapter")
            if args.resume and args.attempt == 3:
                raise DelegateInputError("the rescue assignment requires a fresh session, never a previous executor's resume ID")
            args.executor, args.model, args.effort = (
                route["executor"], route["model"], route["reasoning_effort"]
            )
        elif (args.resolve_only or args.presets_file or args.host or args.root_model
              or args.independent_planning or args.attempt != 1 or args.tier != "standard"):
            raise DelegateInputError("preset routing options require --preset")
        for field in ("repo", "executor", "model", "prompt_file", "log_file", "expected_head"):
            if not getattr(args, field):
                raise DelegateInputError(f"--{field.replace('_', '-')} is required for execution")
        payload, exit_code = execute(args)
        if route is not None:
            payload["assignment"] = route
    except DelegateInputError as error:
        _emit({"status": "invalid", "reason": _compact(str(error), limit=500)})
        return 2
    except DelegateUnavailable as error:
        _emit({"status": "blocked", "reason": _compact(str(error), limit=500)})
        return 1
    _emit(payload)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
