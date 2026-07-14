#!/usr/bin/env python3
"""Synchronize the repository-owned Orchestra runtime into Codex user paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import tempfile
from typing import Any


SKILLS = (
    "orchestra",
    "orchestra-phase-commit",
    "orchestra-delivery-policy",
    "orchestra-pr-open",
    "orchestra-pr-review",
    "orchestra-pr-merge",
    "orchestra-local-integrate",
)
AGENTS = (
    "browser_acceptance_tester",
    "debugging_investigator",
    "implementation_worker",
    "phase_committer",
    "plan_scope_auditor",
    "planner",
    "pr_polling_specialist",
    "pr_triage_specialist",
    "repo_context_explorer",
    "reviewer",
    "web_researcher",
)
HELPERS = ("commit_phase.py", "policy.py", "pr.py", "integrate_local.py")
START = b"<!-- orchestra:start -->"
END = b"<!-- orchestra:end -->"
MANIFEST_PATH = "orchestra/install-manifest.json"


class SyncError(Exception):
    """An unsafe or invalid synchronization state."""


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _result(status: str, action: str, changes: list[dict[str, str]], detail: str = "") -> dict[str, Any]:
    payload: dict[str, Any] = {"action": action, "changes": changes, "status": status}
    if detail:
        payload["detail"] = detail
    return payload


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


def _entry(root: str, path: str, kind: str, content: bytes) -> dict[str, Any]:
    return {"root": root, "path": path, "type": kind, "content": content}


def _inventory(source_root: Path) -> dict[tuple[str, str], dict[str, Any]]:
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
        raise SyncError("skill source inventory does not match the seven supported skills")
    for skill in SKILLS:
        directory = skill_root / skill
        for source in _walk_files(directory):
            relative = source.relative_to(directory).as_posix()
            destination = f".agents/skills/{skill}/{relative}"
            entries[("home", destination)] = _entry(
                "home", destination, "file", _read_file(source, str(source))
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
        raise SyncError("agent source inventory does not match the eleven supported profiles")
    for name in AGENTS:
        source = agent_dir / f"{name}.toml"
        destination = f"agents/{name}.toml"
        entries[("codex_home", destination)] = _entry(
            "codex_home", destination, "file", _read_file(source, str(source))
        )

    fixed = (
        (source_root / "codex/config/roles.toml", "orchestra/roles.toml"),
        *(
            (source_root / "codex/scripts" / helper, f"orchestra/scripts/{helper}")
            for helper in HELPERS
        ),
    )
    for source, destination in fixed:
        entries[("codex_home", destination)] = _entry(
            "codex_home", destination, "file", _read_file(source, str(source))
        )

    block_source = source_root / "codex/runtime/AGENTS.orchestra.md"
    block = _read_file(block_source, str(block_source))
    span = _block_span(block)
    if span != (0, len(block)):
        raise SyncError("runtime AGENTS source must contain exactly the managed block")
    entries[("codex_home", "AGENTS.md")] = _entry(
        "codex_home", "AGENTS.md", "managed_block", block
    )
    return entries


def _allowed_entry(root: str, path: str, kind: str) -> bool:
    parts = _relative(path).parts
    if root == "home" and kind == "file" and len(parts) >= 4:
        return parts[:2] == (".agents", "skills") and parts[2] in SKILLS
    if root != "codex_home":
        return False
    if kind == "managed_block":
        return path == "AGENTS.md"
    if kind != "file":
        return False
    if len(parts) == 2 and parts[0] == "agents":
        return parts[1] in {f"{name}.toml" for name in AGENTS}
    return path == "orchestra/roles.toml" or path in {
        f"orchestra/scripts/{name}" for name in HELPERS
    }


def _backup_path(root: str, path: str) -> str:
    return f"orchestra/backups/{root}/{path}"


def _manifest_entry(entry: dict[str, Any], backup: str | None = None) -> dict[str, str]:
    result = {
        "digest": _digest(entry["content"]),
        "path": entry["path"],
        "root": entry["root"],
        "type": entry["type"],
    }
    if backup is not None:
        result["backup"] = backup
    return result


def _load_manifest(
    codex_home: Path,
) -> tuple[dict[tuple[str, str], dict[str, str]], bool, list[str]]:
    path = _safe_path(codex_home, MANIFEST_PATH)
    if not path.exists():
        return {}, False, []
    data = _read_file(path, MANIFEST_PATH)
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
    if not isinstance(payload, dict) or set(payload) != {"entries"} or not isinstance(payload["entries"], list):
        raise SyncError("invalid install manifest structure")
    result: dict[tuple[str, str], dict[str, str]] = {}
    auxiliary_drift: list[str] = []
    for raw in payload["entries"]:
        if not isinstance(raw, dict):
            raise SyncError("invalid install manifest entry")
        required = {"digest", "path", "root", "type"}
        if not required <= set(raw) or set(raw) - (required | {"backup"}):
            raise SyncError("invalid install manifest entry fields")
        if any(not isinstance(raw[name], str) for name in raw):
            raise SyncError("install manifest values must be strings")
        if len(raw["digest"]) != 64 or any(char not in "0123456789abcdef" for char in raw["digest"]):
            raise SyncError("invalid install manifest digest")
        if not _allowed_entry(raw["root"], raw["path"], raw["type"]):
            raise SyncError(f"install manifest contains an unauthorized destination: {raw['path']}")
        key = (raw["root"], raw["path"])
        if key in result:
            raise SyncError(f"duplicate install manifest destination: {raw['path']}")
        if "backup" in raw:
            expected = _backup_path(raw["root"], raw["path"])
            if raw["backup"] != expected:
                raise SyncError(f"invalid backup reference for {raw['path']}")
            backup = _safe_path(codex_home, raw["backup"])
            if not backup.exists():
                auxiliary_drift.append(f"referenced backup is missing: {raw['backup']}")
            elif not backup.is_file():
                raise SyncError(f"referenced backup is not a regular file: {raw['backup']}")
        result[key] = dict(raw)
    return result, True, auxiliary_drift


def _block_span(data: bytes) -> tuple[int, int] | None:
    starts = data.count(START)
    ends = data.count(END)
    if starts == 0 and ends == 0:
        return None
    if starts != 1 or ends != 1:
        raise SyncError("managed AGENTS markers must appear exactly once")
    start = data.index(START)
    end = data.index(END)
    if start >= end:
        raise SyncError("managed AGENTS markers are misordered")
    if (start and data[start - 1 : start] != b"\n") or data[
        start + len(START) : start + len(START) + 1
    ] != b"\n":
        raise SyncError("managed AGENTS start marker must occupy its own line")
    if data[end - 1 : end] != b"\n":
        raise SyncError("managed AGENTS end marker must occupy its own line")
    end += len(END)
    if data[end : end + 1] not in {b"", b"\n"}:
        raise SyncError("managed AGENTS end marker must occupy its own line")
    if data[end : end + 1] == b"\n":
        end += 1
    return start, end


def _roots(home: Path, codex_home: Path) -> dict[str, Path]:
    return {"home": home, "codex_home": codex_home}


def _destination(roots: dict[str, Path], entry: dict[str, Any]) -> Path:
    return _safe_path(roots[entry["root"]], entry["path"])


def _operation(kind: str, entry: dict[str, Any], before: bytes | None) -> dict[str, Any]:
    return {"kind": kind, "entry": entry, "before": before}


def _analyze(source_root: Path, home: Path, codex_home: Path) -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    dict[tuple[str, str], dict[str, str]],
    list[dict[str, Any]],
    list[str],
]:
    desired = _inventory(source_root)
    installed, _, auxiliary_drift = _load_manifest(codex_home)
    roots = _roots(home, codex_home)
    operations: list[dict[str, Any]] = []

    for key in sorted(desired):
        entry = desired[key]
        path = _destination(roots, entry)
        owner = installed.get(key)
        if entry["type"] == "file":
            if owner is None:
                if path.exists():
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
            span = _block_span(current)
            if owner is None:
                if span is not None:
                    raise SyncError("unmanaged Orchestra markers in AGENTS.md")
                operations.append(_operation("insert_block", entry, current if path.exists() else None))
                continue
            if not path.exists() or span is None:
                raise SyncError("owned managed block is missing from AGENTS.md")
            if _digest(current[span[0] : span[1]]) != owner["digest"]:
                raise SyncError("owned managed block drift in AGENTS.md")
            if current[span[0] : span[1]] != entry["content"]:
                operations.append(_operation("update_block", entry, current))

    for key in sorted(set(installed) - set(desired)):
        owner = installed[key]
        path = _safe_path(roots[owner["root"]], owner["path"])
        current = _read_file(path, owner["path"])
        if owner["type"] == "managed_block":
            span = _block_span(current)
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
        backup = _safe_path(codex_home, backup_rel)
        owner = installed.get((entry["root"], entry["path"]))
        if backup.exists() and (owner is None or owner.get("backup") != backup_rel):
            raise SyncError(f"unmanaged backup collision: {backup_rel}")
    operations.sort(key=lambda item: (item["entry"]["root"], item["entry"]["path"], item["kind"]))
    return desired, installed, operations, auxiliary_drift


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


def _write_manifest(codex_home: Path, entries: dict[tuple[str, str], dict[str, str]]) -> None:
    path = _safe_path(codex_home, MANIFEST_PATH)
    if not entries:
        if path.exists():
            path.unlink()
        return
    payload = {"entries": [entries[key] for key in sorted(entries)]}
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    _atomic_write(path, data, codex_home, new_mode=0o600)


def _preview(operations: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "operation": operation["kind"],
            "path": operation["entry"]["path"],
            "root": operation["entry"]["root"],
        }
        for operation in operations
    ]


def _check_before(path: Path, before: bytes | None) -> None:
    if before is None:
        if path.exists():
            raise SyncError(f"destination changed during synchronization: {path}")
        return
    if _read_file(path, str(path)) != before:
        raise SyncError(f"destination changed during synchronization: {path}")


def _apply_operation(
    operation: dict[str, Any], roots: dict[str, Path], codex_home: Path
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
        if before is not None:
            backup_rel = _backup_path(entry["root"], entry["path"])
            backup = _safe_path(codex_home, backup_rel)
            state["backup"] = backup
            state["backup_rel"] = backup_rel
            if backup.exists():
                state["backup_before"] = _read_file(backup, backup_rel)
                state["backup_mode"] = stat.S_IMODE(backup.stat().st_mode)
            _atomic_write(backup, before, codex_home, new_mode=0o600)

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
        elif kind == "delete":
            if entry["type"] == "managed_block":
                span = _block_span(before)
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
            _cleanup_operation_backup(state, codex_home)
        else:
            raise SyncError(f"unknown operation: {kind}")
    except Exception:
        _restore_operation(state, codex_home)
        raise
    return state


def _cleanup_operation_backup(state: dict[str, Any], codex_home: Path) -> None:
    """Remove the transient delete backup while local compensation is possible."""
    backup = state["backup"]
    if backup is not None and backup.exists():
        backup.unlink()
        _cleanup_empty(backup.parent, codex_home)


def _restore_operation(state: dict[str, Any], codex_home: Path) -> None:
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
        _cleanup_empty(backup.parent, codex_home)
    else:
        _atomic_write(
            backup,
            state["backup_before"],
            codex_home,
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


def synchronize(source_root: Path, home: Path, codex_home: Path, action: str, *, dry_run: bool = False) -> dict[str, Any]:
    """Run one synchronization action against explicit destination roots."""
    source_root = Path(os.path.abspath(source_root))
    home = Path(os.path.abspath(home))
    codex_home = Path(os.path.abspath(codex_home))
    label = "apply --dry-run" if action == "apply" and dry_run else action
    try:
        desired, installed, operations, auxiliary_drift = _analyze(
            source_root, home, codex_home
        )
    except (OSError, SyncError) as exc:
        return _result("blocked", label, [], str(exc))
    changes = _preview(operations)
    if action == "status" or dry_run:
        detail = "; ".join(auxiliary_drift)
        return _result("partial" if operations or auxiliary_drift else "ok", label, changes, detail)
    if action != "apply":
        return _result("blocked", label, [], f"unsupported action: {action}")

    roots = _roots(home, codex_home)
    current = dict(installed)
    completed: list[dict[str, str]] = []
    for operation in operations:
        entry = operation["entry"]
        key = (entry["root"], entry["path"])
        next_current = dict(current)
        try:
            state = _apply_operation(operation, roots, codex_home)
            if operation["kind"] == "delete":
                next_current.pop(key, None)
            else:
                next_current[key] = _manifest_entry(
                    desired[key],
                    state["backup_rel"] or current.get(key, {}).get("backup"),
                )
            _write_manifest(codex_home, next_current)
        except (OSError, SyncError) as exc:
            if "state" in locals():
                try:
                    _restore_operation(state, codex_home)
                except (OSError, SyncError) as restore_exc:
                    exc = SyncError(f"{exc}; local compensation failed: {restore_exc}")
                del state
            status = "partial" if completed else "blocked"
            return _result(status, label, completed, str(exc))
        current = next_current
        completed.extend(_preview([operation]))
        del state

    try:
        _, _, remaining_drift = _load_manifest(codex_home)
    except (OSError, SyncError) as exc:
        return _result("partial", label, completed, str(exc))
    detail = "; ".join(remaining_drift)
    return _result("partial" if remaining_drift else "ok", label, completed, detail)


def uninstall(home: Path, codex_home: Path) -> dict[str, Any]:
    """Remove only destinations still matching the recorded ownership digests."""
    home = Path(os.path.abspath(home))
    codex_home = Path(os.path.abspath(codex_home))
    try:
        installed, present, auxiliary_drift = _load_manifest(codex_home)
    except (OSError, SyncError) as exc:
        return _result("blocked", "uninstall", [], str(exc))
    if not present:
        return _result("ok", "uninstall", [])
    roots = _roots(home, codex_home)
    current = dict(installed)
    changes: list[dict[str, str]] = []
    drift: list[str] = []
    for key in sorted(installed):
        owner = installed[key]
        try:
            path = _safe_path(roots[owner["root"]], owner["path"])
            data = _read_file(path, owner["path"])
            if owner["type"] == "managed_block":
                span = _block_span(data)
                matches = span is not None and _digest(data[span[0] : span[1]]) == owner["digest"]
            else:
                matches = _digest(data) == owner["digest"]
            if not matches:
                drift.append(f"{owner['path']}: owned content drift")
                continue
            backup_rel = _backup_path(owner["root"], owner["path"])
            backup = _safe_path(codex_home, backup_rel)
            if backup.exists() and owner.get("backup") != backup_rel:
                drift.append(f"{owner['path']}: unmanaged backup collision")
                continue
        except (OSError, SyncError) as exc:
            drift.append(f"{owner['path']}: {exc}")
            continue

        try:
            stale = dict(owner)
            stale["content"] = b""
            stale["_keep_empty"] = owner["type"] == "managed_block" and "backup" in owner
            operation = _operation("delete", stale, data)
            state = _apply_operation(operation, roots, codex_home)
            next_current = dict(current)
            next_current.pop(key)
            try:
                _write_manifest(codex_home, next_current)
            except (OSError, SyncError) as exc:
                try:
                    _restore_operation(state, codex_home)
                except (OSError, SyncError) as restore_exc:
                    exc = SyncError(f"{exc}; local compensation failed: {restore_exc}")
                status = "partial" if changes else "blocked"
                detail = "; ".join([*drift, *auxiliary_drift, str(exc)])
                return _result(status, "uninstall", changes, detail)
            current = next_current
            changes.extend(_preview([operation]))
            _cleanup_empty(path.parent, roots[owner["root"]])
        except (OSError, SyncError) as exc:
            status = "partial" if changes else "blocked"
            detail = "; ".join([*drift, *auxiliary_drift, f"{owner['path']}: {exc}"])
            return _result(status, "uninstall", changes, detail)
    try:
        _, _, remaining_auxiliary = _load_manifest(codex_home)
        _cleanup_empty((codex_home / "orchestra/backups"), codex_home)
        _cleanup_empty((codex_home / "orchestra"), codex_home)
    except (OSError, SyncError) as exc:
        drift.append(f"manifest: {exc}")
        remaining_auxiliary = auxiliary_drift
    detail = "; ".join([*drift, *remaining_auxiliary])
    return _result("partial" if drift or remaining_auxiliary else "ok", "uninstall", changes, detail)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--dry-run", action="store_true")
    subparsers.add_parser("uninstall")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source_root = Path(__file__).resolve().parents[2]
    home = Path(os.environ["HOME"])
    codex_home = Path(os.environ.get("CODEX_HOME", str(home / ".codex")))
    if args.command == "uninstall":
        payload = uninstall(home, codex_home)
    else:
        payload = synchronize(source_root, home, codex_home, args.command, dry_run=getattr(args, "dry_run", False))
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 2 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
