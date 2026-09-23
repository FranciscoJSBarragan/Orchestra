from __future__ import annotations

import ast
import io
import os
import re
import subprocess
import tokenize
from collections import Counter
from collections.abc import Mapping
from pathlib import Path


class CommentPolicyError(ValueError):
    pass


def _git(root: Path, *args: str, required: bool = True) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if required and result.returncode:
        raise CommentPolicyError(
            f"Git context unavailable for {' '.join(args[:2])}: "
            f"{result.stderr.decode(errors='replace').strip()}. "
            "Fetch the required base objects or pass a valid commit base; "
            "use explicit full-scan mode for source exports."
        )
    return result.stdout if result.returncode == 0 else b""


def _paths(data: bytes) -> list[str]:
    return [os.fsdecode(path) for path in data.split(b"\0") if path]


def _snapshot(root: Path, revision: str | None, target: str) -> dict[str, bytes]:
    if revision is not None:
        paths = _paths(_git(root, "ls-tree", "-rz", "--name-only", revision))
    else:
        args = ["ls-files", "-z", "--cached"]
        if target == "worktree":
            args.extend(["--others", "--exclude-standard"])
        paths = _paths(_git(root, *args))
    result = {}
    for name in sorted(set(paths)):
        if not name.endswith(".py"):
            continue
        if revision is not None:
            result[name] = _git(root, "show", f"{revision}:{name}")
        elif target == "staged":
            result[name] = _git(root, "show", f":{name}")
        else:
            path = root / name
            if path.is_symlink():
                raise CommentPolicyError(f"{name}: Python symlink requires explicit consumer review.")
            if path.is_file():
                result[name] = path.read_bytes()
    return result


def _export_snapshot(root: Path) -> dict[str, bytes]:
    skipped = {".git", ".venv", "venv", "__pycache__", "node_modules", "vendor", "third_party", ".mypy_cache", ".pytest_cache"}
    result = {}
    for parent, folders, files in os.walk(root):
        folders[:] = [name for name in folders if name not in skipped and not (Path(parent) / name).is_symlink()]
        for name in files:
            path = Path(parent) / name
            if path.suffix == ".py" and not path.is_symlink():
                result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def _normalized(text: str) -> str:
    return "\n".join(line.strip() for line in text.strip().splitlines())


def _spdx_expression(expression: str) -> bool:
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9.+:-]*|[()]", expression)
    if "".join(tokens) != re.sub(r"\s+", "", expression):
        return False
    cursor = 0

    def identifier() -> bool:
        nonlocal cursor
        if cursor == len(tokens) or tokens[cursor] in {"AND", "OR", "WITH", "(", ")"}:
            return False
        cursor += 1
        return True

    def term() -> bool:
        nonlocal cursor
        if cursor < len(tokens) and tokens[cursor] == "(":
            cursor += 1
            if not compound() or cursor == len(tokens) or tokens[cursor] != ")":
                return False
            cursor += 1
            return True
        if not identifier():
            return False
        if cursor < len(tokens) and tokens[cursor] == "WITH":
            cursor += 1
            return identifier()
        return True

    def compound() -> bool:
        nonlocal cursor
        if not term():
            return False
        while cursor < len(tokens) and tokens[cursor] in {"AND", "OR"}:
            cursor += 1
            if not term():
                return False
        return True

    return compound() and cursor == len(tokens)


def _functional_comment(token: tokenize.TokenInfo, source: str, type_comments: set[tuple[int, str]]) -> bool:
    value = token.string
    if token.start == (1, 0) and value.startswith("#!"):
        return True
    if token.start[0] <= 2 and not token.line[:token.start[1]].strip() and (token.start[0] == 1 or not source.splitlines()[0].strip() or source.splitlines()[0].lstrip().startswith("#")) and re.fullmatch(r"#\s*(?:-\*-\s*)?coding[:=]\s*[-\w.]+\s*(?:-\*-)?\s*", value):
        try:
            tokenize.detect_encoding(io.BytesIO(source.encode("utf-8")).readline)
        except SyntaxError:
            return False
        return True
    text = value.removeprefix("#").strip()
    if text.startswith("SPDX-License-Identifier: "):
        return _spdx_expression(text.removeprefix("SPDX-License-Identifier: "))
    patterns = (
        r"SPDX-FileCopyrightText: \S.*",
        r"Copyright (?:\([cC]\) )?\d{4}(?:[-, ]\d{4})* \S.*",
        r"noqa(?::\s*[A-Z]+\d+(?:\s*,\s*[A-Z]+\d+)*)?",
        r"type:\s*ignore(?:\[[a-z0-9_-]+(?:\s*,\s*[a-z0-9_-]+)*\])?",
        r"(?:fmt|isort):\s*(?:off|on|skip)",
        r"pylint:\s*(?:disable|enable|disable-next)=[a-zA-Z0-9_-]+(?:,[a-zA-Z0-9_-]+)*",
        r"pragma:\s*no (?:cover|branch)",
        r"ruff:\s*noqa(?::\s*[A-Z]+\d+(?:\s*,\s*[A-Z]+\d+)*)?",
    )
    if any(re.fullmatch(pattern, text) for pattern in patterns):
        return True
    if (token.start[0], text) in type_comments:
        return True
    return False


def _module_cli_doc(tree: ast.Module) -> bool:
    modules = set()
    constructors = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            modules.update(alias.asname or alias.name for alias in node.names if alias.name == "argparse")
        elif isinstance(node, ast.ImportFrom) and node.module == "argparse":
            constructors.update(alias.asname or alias.name for alias in node.names if alias.name == "ArgumentParser")
    rebound = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)}
    rebound.update(node.arg for node in ast.walk(tree) if isinstance(node, ast.arg))
    if "__doc__" in rebound:
        return False
    modules -= rebound
    constructors -= rebound
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        matches = isinstance(func, ast.Name) and func.id in constructors
        matches |= isinstance(func, ast.Attribute) and func.attr == "ArgumentParser" and isinstance(func.value, ast.Name) and func.value.id in modules
        if matches and any(keyword.arg in {"description", "epilog"} and isinstance(keyword.value, ast.Name) and keyword.value.id == "__doc__" for keyword in node.keywords):
            return True
    return False


def _violations(data: bytes, name: str) -> list[tuple[str, str, int]]:
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
        source = data.decode(encoding)
        tree = ast.parse(source, filename=name)
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except (SyntaxError, UnicodeError, LookupError, tokenize.TokenError) as error:
        raise CommentPolicyError(f"{name}: cannot establish Python comment policy: {error}") from error
    type_comments = set()
    try:
        typed_tree = ast.parse(source, filename=name, type_comments=True)
    except SyntaxError:
        typed_tree = None
    if typed_tree is not None:
        for node in ast.walk(typed_tree):
            annotation = getattr(node, "type_comment", None)
            if annotation is None:
                continue
            try:
                ast.parse(annotation, mode="func_type" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "eval")
            except SyntaxError:
                continue
            for token in tokens:
                if token.type == tokenize.COMMENT and node.lineno <= token.start[0] <= node.end_lineno and token.string.removeprefix("#").strip() == f"type: {annotation}" and "#" not in annotation:
                    type_comments.add((token.start[0], f"type: {annotation}"))
    result = [
        ("comment", _normalized(token.string.removeprefix("#")), token.start[0])
        for token in tokens
        if token.type == tokenize.COMMENT and not _functional_comment(token, source, type_comments)
    ]

    def visit(node: ast.AST) -> None:
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            doc = ast.get_docstring(node, clean=False)
            allowed = isinstance(node, ast.Module) and _module_cli_doc(tree)
            if doc is not None and not allowed:
                result.append(("docstring", _normalized(doc), node.body[0].lineno))
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return sorted(result, key=lambda item: item[2])


def _renames(root: Path, base: str, target: str, before: Mapping[str, bytes], after: Mapping[str, bytes]) -> dict[str, str]:
    args = ["diff", "--no-ext-diff", "--no-color", "--name-status", "-z", "--find-renames"]
    if target == "staged":
        args.append("--cached")
    args.extend([base, "--"])
    entries = _paths(_git(root, *args))
    result = {}
    cursor = 0
    while cursor < len(entries):
        status = entries[cursor]
        cursor += 1
        old = entries[cursor]
        cursor += 1
        if status.startswith(("R", "C")):
            new = entries[cursor]
            cursor += 1
            if status.startswith("R") and old in before and new in after:
                result[new] = old
    removed = set(before) - set(after) - set(result.values())
    for new in sorted(set(after) - set(before) - set(result)):
        old = next((name for name in sorted(removed) if before[name] == after[new]), None)
        if old is not None:
            result[new] = old
            removed.remove(old)
    return result


def check_repository(
    root: Path,
    *,
    base: str = "HEAD",
    target: str = "worktree",
    full_scan: bool = False,
) -> list[str]:
    root = root.resolve()
    if not root.is_dir():
        raise CommentPolicyError(f"Source root does not exist: {root}")
    if target not in {"worktree", "staged"}:
        raise CommentPolicyError("Comment target must be 'worktree' or 'staged'.")
    git_root = _git(root, "rev-parse", "--show-toplevel", required=False)
    if git_root and Path(os.fsdecode(git_root).strip()).resolve() != root:
        raise CommentPolicyError("Pass the repository root, not a nested source directory.")
    if full_scan:
        if target == "staged" and not git_root:
            raise CommentPolicyError("A staged scan requires a Git index.")
        before = {}
        after = _snapshot(root, None, target) if git_root else _export_snapshot(root)
        renames = {}
    else:
        if not git_root:
            raise CommentPolicyError("Git context required for delta checks; use explicit full-scan mode for source exports.")
        if base == "EMPTY":
            if _git(root, "rev-parse", "--verify", "--end-of-options", "HEAD", required=False):
                headers = _git(root, "cat-file", "-p", "HEAD").split(b"\n\n", 1)[0]
                if any(line.startswith(b"parent ") for line in headers.splitlines()):
                    raise CommentPolicyError("EMPTY base is reserved for an initial commit or an unborn HEAD.")
            before = {}
        else:
            if base and set(base) == {"0"}:
                raise CommentPolicyError("An all-zero event SHA is not a Git base; select EMPTY for an initial commit or resolve the default-branch merge-base.")
            revision = _git(root, "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}").decode().strip()
            before = _snapshot(root, revision, target)
        after = _snapshot(root, None, target)
        renames = {} if base == "EMPTY" else _renames(root, revision, target, before, after)
    diagnostics = []
    for name, data in sorted(after.items()):
        original = renames.get(name, name)
        if original in before and before[original] == data:
            continue
        legacy = Counter((kind, text) for kind, text, _ in _violations(before[original], original)) if original in before else Counter()
        for kind, text, line in _violations(data, name):
            key = (kind, text)
            if legacy[key]:
                legacy[key] -= 1
            else:
                diagnostics.append(f"{name}:{line}: {'existing' if full_scan else 'new'} explanatory {kind}; express the constraint in code/tests or maintained documentation.")
    return diagnostics
