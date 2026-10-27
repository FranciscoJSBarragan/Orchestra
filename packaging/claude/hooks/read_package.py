#!/usr/bin/env python3
import json
import os
import sys


def main() -> int:
    try:
        event = json.load(sys.stdin)
        arguments = event.get("tool_input") or {}
        target = arguments.get("file_path") or arguments.get("path")
        root = os.path.realpath(os.environ["CLAUDE_PLUGIN_ROOT"])
        if not isinstance(target, str) or not os.path.isabs(target):
            return 0
        if os.path.commonpath([root, os.path.realpath(target)]) != root:
            return 0
    except (KeyError, ValueError, AttributeError):
        return 0
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "read-only Orchestra package instructions",
    }}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
