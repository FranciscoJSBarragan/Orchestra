"""Server-rendered HTML panel (SPEC §9, §11)."""
from __future__ import annotations

import html
from datetime import datetime

from orchestra_hub.api import parse_timestamp

_MAIN_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="30">
  <title>Orchestra Hub</title>
  <style>
    body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 0.85rem; margin: 1.5rem; color: #d0d7de;
            background: #0d1117; }}
    h1 {{ font-size: 1.25rem; color: #e6edf3; letter-spacing: 0.02em; }}
    h2 {{ font-size: 0.95rem; margin-top: 1.75rem; color: #8b949e;
          text-transform: uppercase; letter-spacing: 0.08em; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 0.5rem; }}
    th, td {{ border: 1px solid #21262d; padding: 0.4rem 0.6rem;
              text-align: left; vertical-align: top; }}
    th {{ background: #161b22; color: #8b949e; font-weight: 600; }}
    tbody tr:hover {{ background: #161b22; }}
    .empty {{ font-style: italic; color: #8b949e; }}
    .attention {{ margin: 0.5rem 0 1rem; padding: 0.6rem 0.85rem;
                  background: #161b22; border: 1px solid #21262d;
                  border-left: 3px solid #f85149; }}
    .attention strong {{ color: #f85149; }}
  </style>
</head>
<body>
  <h1>Orchestra Hub</h1>
  {body}
</body>
</html>
"""

_DEGRADED_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="30">
  <title>Orchestra Hub — degraded</title>
  <style>
    body {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 0.85rem; margin: 1.5rem; color: #d0d7de;
            background: #0d1117; }}
    h1 {{ font-size: 1.25rem; color: #e6edf3; }}
    strong {{ color: #d29922; }}
    code {{ color: #f85149; }}
  </style>
</head>
<body>
  <h1>Orchestra Hub</h1>
  <p><strong>Degraded</strong>: database condition
    <code>{condition}</code>.</p>
  <p>{detail}</p>
  <p>Orchestra itself is unaffected.</p>
</body>
</html>
"""


def _age(updated_at: object, now: datetime) -> str:
    stamp = parse_timestamp(str(updated_at))
    minutes = int((now - stamp).total_seconds() // 60)
    return f"{minutes} min ago"


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_degraded(condition: str, detail: str) -> str:
    return _DEGRADED_TEMPLATE.format(
        condition=_escape(condition),
        detail=_escape(detail),
    )


def render_panel(summary: dict, now: datetime) -> str:
    attention = list(summary.get("attention") or [])
    repositories = list(summary.get("repositories") or [])
    tasks = list(summary.get("tasks") or [])

    parts: list[str] = []
    parts.append(f"<h2>Possible attention ({len(attention)})</h2>")
    if not attention:
        parts.append('<p class="empty">No attention items.</p>')
    else:
        for entry in attention:
            label = _escape(entry.get("label", ""))
            reasons = _escape(", ".join(str(r) for r in entry.get("reasons") or []))
            blocker = entry.get("blocker") or ""
            next_action = entry.get("next_action") or ""
            action_text = blocker if blocker else next_action
            repository = _escape(entry.get("repository", ""))
            age = _escape(_age(entry.get("updated_at", ""), now))
            parts.append(
                '<div class="attention">'
                f"<div><strong>{label}</strong> [{reasons}]</div>"
                f"<div>{_escape(action_text)}</div>"
                f"<div>{repository}</div>"
                f"<div>last snapshot {age}</div>"
                "</div>"
            )

    parts.append("<h2>Repositories</h2>")
    if not repositories:
        parts.append('<p class="empty">No repositories.</p>')
    else:
        rows = []
        for repo in repositories:
            flags = []
            if repo.get("pinned"):
                flags.append("pinned")
            if repo.get("observed"):
                flags.append("observed")
            rows.append(
                "<tr>"
                f"<td>{_escape(repo.get('name', ''))}</td>"
                f"<td>{_escape(repo.get('path', ''))}</td>"
                f"<td>{_escape(repo.get('active_tasks', 0))}</td>"
                f"<td>{_escape(repo.get('completed_tasks', 0))}</td>"
                f"<td>{_escape(', '.join(flags))}</td>"
                "</tr>"
            )
        parts.append(
            "<table><thead><tr>"
            "<th>Name</th><th>Path</th><th>Active</th><th>Completed</th>"
            "<th>Flags</th></tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )

    parts.append("<h2>Tasks</h2>")
    if not tasks:
        parts.append('<p class="empty">No tasks.</p>')
    else:
        rows = []
        for task in tasks:
            age = _age(task.get("updated_at", ""), now)
            if task.get("stale"):
                age = f"{age} · stale"
            rows.append(
                "<tr>"
                f"<td>{_escape(task.get('label', ''))}</td>"
                f"<td>{_escape(task.get('repository', ''))}</td>"
                f"<td>{_escape(task.get('stage', ''))}</td>"
                f"<td>{_escape(task.get('status', ''))}</td>"
                f"<td>{_escape(task.get('summary', ''))}</td>"
                f"<td>last snapshot {_escape(age)}</td>"
                "</tr>"
            )
        parts.append(
            "<table><thead><tr>"
            "<th>Label</th><th>Repository</th><th>Stage</th><th>Status</th>"
            "<th>Summary</th><th>Age</th></tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table>"
        )

    return _MAIN_TEMPLATE.format(body="\n".join(parts))
