#!/usr/bin/env python3
"""SwiftBar plugin: Orchestra Hub attention monitor (read-only)."""
from __future__ import annotations

import json
import subprocess
import urllib.request
from pathlib import Path

HUB = "http://127.0.0.1:7343"
STATE_PATH = Path.home() / ".orchestra" / "hub-monitor.json"


def load_state() -> dict | None:
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if (
            isinstance(state, dict)
            and "material_fingerprint_version" in state
            and isinstance(state.get("fingerprints"), dict)
        ):
            return state
    except (OSError, ValueError):
        pass
    return None


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")


def notify(title: str, message: str) -> None:
    script = 'display notification "{}" with title "{}"'.format(
        message.replace("\\", "\\\\").replace('"', '\\"'),
        title.replace("\\", "\\\\").replace('"', '\\"'),
    )
    subprocess.run(["osascript", "-e", script], check=False,
                   capture_output=True)


def fetch_summary() -> dict | None:
    try:
        with urllib.request.urlopen(f"{HUB}/v1/summary", timeout=5) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def swiftbar_text(value: object) -> str:
    return str(value).replace("|", "¦").replace("\r", " ").replace("\n", " ")


def main() -> None:
    summary = fetch_summary()
    if summary is None or summary.get("status") != "ok":
        print("Hub ?")
        print("---")
        print("Hub unreachable or degraded | color=red")
        print(f"Open panel | href={HUB}/")
        return

    state = load_state()
    version = summary["material_fingerprint_version"]
    current = {
        task["id"]: task["material_fingerprint"]
        for task in summary["tasks"]
    }
    attention = summary["attention"]
    blockers = [
        entry for entry in attention
        if "blocker" in entry["reasons"]
    ]
    baseline = (
        state is None
        or state["material_fingerprint_version"] != version
    )
    if baseline:
        if blockers:
            notify(
                "Orchestra Hub",
                f"{len(blockers)} task(s) may need attention",
            )
    else:
        changed = [
            task for task in summary["tasks"]
            if state["fingerprints"].get(task["id"])
            != task["material_fingerprint"]
        ]
        for task in changed:
            if task["blocker"]:
                notify("Orchestra: blocked", f"{task['label']}: {task['blocker']}")
            elif task["status"] == "completed":
                notify("Orchestra: completed", task["label"])
            else:
                notify("Orchestra: updated", f"{task['label']} — {task['status']}")

    save_state({
        "material_fingerprint_version": version,
        "fingerprints": current,
    })

    count = len(attention)
    print(f"O {count}" if count else "O")
    print("---")
    for entry in attention:
        label = swiftbar_text(entry["label"])
        reasons = swiftbar_text(",".join(entry["reasons"]))
        detail = swiftbar_text(
            entry["blocker"] or entry["next_action"] or ""
        )
        print(f"{label} ({reasons}) | color=red")
        if detail:
            print(f"-- {detail[:80]}")
    if not attention:
        print("Nothing needs attention")
    print("---")
    for task in summary["tasks"]:
        if task["status"] != "completed":
            label = swiftbar_text(task["label"])
            stage = swiftbar_text(task["stage"])
            status = swiftbar_text(task["status"])
            print(f"{label} — {stage}/{status}")
    print("---")
    print(f"Open panel | href={HUB}/")


if __name__ == "__main__":
    main()
