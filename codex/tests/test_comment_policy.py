from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from comment_policy import CommentPolicyError, check_repository


class CommentPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.invalid")
        self.git("config", "user.name", "Test")
        self.git("config", "core.hooksPath", "/dev/null")
        self.git("config", "commit.gpgsign", "false")
        self.write("app.py", "value = 1\n")
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True).stdout

    def write(self, name, source):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source)

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")

    def test_functional_tokens_and_fixture_strings(self):
        self.write("app.py", '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Example Authors
value = "# not a comment"
sample = """# explanatory negative fixture
with more sample content"""
value = 2  # noqa: F841
value = 3  # type: ignore[assignment]
# fmt: off
# pylint: disable=invalid-name
# pragma: no cover
''')
        self.assertEqual(check_repository(self.root), [])

    def test_directive_trailing_narrative_is_new(self):
        for text in ("noqa: F841 - because it is needed", "fmt: off arbitrary explanation", "type: ignore[assignment] because reasons", "type: int because this is important", "SPDX-License-Identifier: MIT explanatory words"):
            with self.subTest(text=text):
                self.write("app.py", f"value = 1  # {text}\n")
                self.assertEqual(len(check_repository(self.root)), 1)

    def test_functional_declarations_require_consumed_positions(self):
        self.write("app.py", "value = 1  # type: int\n")
        self.assertEqual(check_repository(self.root), [])
        for source in ("# type: unsupported narration\nvalue = 1\n", "value = 1  # coding: utf-8\n", "value = 1\n# coding: utf-8\n"):
            with self.subTest(source=source):
                self.write("app.py", source)
                self.assertEqual(len(check_repository(self.root)), 1)

    def test_function_type_directive_requires_valid_grammar(self):
        self.write("app.py", "def identity(value):  # type: (int) -> int\n    return value\n")
        self.assertEqual(check_repository(self.root), [])
        self.write("app.py", "def identity(value):  # type: (int) -> int because reasons\n    return value\n")
        self.assertEqual(len(check_repository(self.root)), 1)

    def test_parenthesized_spdx_requires_complete_expression(self):
        for expression in ("(MIT OR Apache-2.0) AND BSD-3-Clause", "GPL-2.0-only WITH Classpath-exception-2.0", "MIT OR (Apache-2.0 AND (BSD-3-Clause OR ISC))"):
            with self.subTest(expression=expression):
                self.write("app.py", f"# SPDX-License-Identifier: {expression}\n")
                self.assertEqual(check_repository(self.root), [])
        for expression in ("(MIT OR Apache-2.0) explanatory words", "(MIT OR)", "(MIT", "MIT)", "MIT WITH", "MIT AND OR BSD-3-Clause", "(MIT) WITH exception"):
            with self.subTest(expression=expression):
                self.write("app.py", f"# SPDX-License-Identifier: {expression}\n")
                self.assertEqual(len(check_repository(self.root)), 1)

    def test_ordinary_docstrings_and_cli_consumed_module(self):
        self.write("app.py", '\"\"\"Module narrative.\"\"\"\ndef run():\n    \"\"\"Function narrative.\"\"\"\n    return 1\n')
        self.assertEqual(len(check_repository(self.root)), 2)
        self.write("app.py", '\"\"\"CLI usage.\"\"\"\nimport argparse\nparser = argparse.ArgumentParser(description=__doc__)\n')
        self.assertEqual(check_repository(self.root), [])
        self.write("app.py", '\"\"\"Narrative.\"\"\"\nprint(__doc__)\n')
        self.assertEqual(len(check_repository(self.root)), 1)

    def test_cli_docstring_requires_unshadowed_argparse_consumer(self):
        self.write("app.py", '\"\"\"Narrative.\"\"\"\nimport argparse\nargparse = object()\nargparse.ArgumentParser(description=__doc__)\n')
        self.assertEqual(len(check_repository(self.root)), 1)
        self.write("app.py", '\"\"\"Narrative.\"\"\"\nimport argparse\n__doc__ = "replacement"\nargparse.ArgumentParser(description=__doc__)\n')
        self.assertEqual(len(check_repository(self.root)), 1)

    def test_moved_and_reindented_legacy_is_not_new(self):
        self.write("app.py", '# legacy note\ndef run():\n    \"\"\"Legacy description.\"\"\"\n    return 1\n')
        self.commit()
        self.write("app.py", 'def outer():\n    # legacy note\n    def run():\n        \"\"\"Legacy description.\"\"\"\n        return 1\n')
        self.assertEqual(check_repository(self.root), [])

    def test_edited_and_duplicate_content_cannot_replace_old_debt(self):
        self.write("app.py", "# old note\n# second note\nvalue = 1\n")
        self.commit()
        self.write("app.py", "# edited note\n# old note\n# old note\nvalue = 1\n")
        self.assertEqual(len(check_repository(self.root)), 2)

    def test_git_and_untracked_whole_file_renames_keep_legacy(self):
        self.write("app.py", "# legacy note\nvalue = 1\n")
        self.commit()
        self.git("mv", "app.py", "moved.py")
        self.assertEqual(check_repository(self.root, target="staged"), [])
        self.assertEqual(check_repository(self.root), [])
        self.write("moved.py", "# legacy note\nvalue = 1\n# new note\n")
        self.git("add", "moved.py")
        self.assertEqual(len(check_repository(self.root, target="staged")), 1)
        self.git("reset", "--hard", "-q", "HEAD")
        (self.root / "app.py").rename(self.root / "moved.py")
        self.assertEqual(check_repository(self.root), [])

    def test_copy_preserves_multiplicity_across_files(self):
        self.write("app.py", "# legacy note\nvalue = 1\n")
        self.commit()
        self.write("copy.py", (self.root / "app.py").read_text())
        self.assertEqual(len(check_repository(self.root)), 1)

    def test_staged_snapshot_excludes_unstaged_changes(self):
        self.write("app.py", "value = 2\n")
        self.git("add", "app.py")
        self.write("app.py", "# unstaged note\nvalue = 2\n")
        self.assertEqual(check_repository(self.root, target="staged"), [])
        self.assertEqual(len(check_repository(self.root)), 1)
        self.git("add", "app.py")
        self.write("app.py", "value = 2\n")
        self.assertEqual(len(check_repository(self.root, target="staged")), 1)
        self.assertEqual(check_repository(self.root), [])

    def test_untracked_nonignored_python_is_checked(self):
        self.write(".gitignore", "ignored.py\n")
        self.write("ignored.py", "# ignored note\n")
        self.write("new.py", "# new note\n")
        findings = check_repository(self.root)
        self.assertEqual(len(findings), 1)
        self.assertIn("new.py:", findings[0])
        self.assertEqual(check_repository(self.root, target="staged"), [])

    def test_missing_bases_never_skip_gate(self):
        for base in ("missing-revision", "0" * 40, "--help"):
            with self.subTest(base=base), self.assertRaises(CommentPolicyError):
                check_repository(self.root, base=base)

    def test_explicit_initial_empty_base(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "new.py").write_text("# new note\n")
            self.assertEqual(len(check_repository(root, base="EMPTY")), 1)
            with self.assertRaises(CommentPolicyError):
                check_repository(root)

    def test_empty_base_accepts_committed_root_but_not_later_history(self):
        self.write("app.py", "# initial note\nvalue = 1\n")
        self.git("add", "app.py")
        self.git("commit", "--amend", "--no-edit", "-q")
        self.assertEqual(len(check_repository(self.root, base="EMPTY")), 1)
        self.assertEqual(len(check_repository(self.root, base="EMPTY", target="staged")), 1)
        self.write("app.py", "# later note\nvalue = 2\n")
        self.commit()
        with self.assertRaises(CommentPolicyError):
            check_repository(self.root, base="EMPTY")

    def test_full_scan_without_git_is_diagnostic_and_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = b"# legacy note\r\nvalue = 1\r\n"
            (root / "app.py").write_bytes(data)
            (root / ".venv").mkdir()
            (root / ".venv" / "noise.py").write_text("# cache note\n")
            findings = check_repository(root, full_scan=True)
            self.assertEqual(len(findings), 1)
            self.assertIn("existing", findings[0])
            self.assertEqual((root / "app.py").read_bytes(), data)
            with self.assertRaises(CommentPolicyError):
                check_repository(root)

    def test_non_python_and_non_docstring_multiline_strings_are_unaffected(self):
        self.write("notes.md", "# Heading\n")
        self.write("app.py", 'fixture = \"\"\"This is fixture text, not documentation.\n# negative sample\n\"\"\"\n')
        self.assertEqual(check_repository(self.root), [])

    def test_invalid_python_is_actionable_not_silently_skipped(self):
        self.write("app.py", "def broken(:\n")
        with self.assertRaises(CommentPolicyError) as raised:
            check_repository(self.root)
        self.assertIn("app.py", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
