"""Textual dashboard for the Orchestra Hub (layout and wiring only)."""
from __future__ import annotations

from datetime import datetime, timezone

from rich.markup import escape
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import DataTable, Footer, Static, Tree

from .client import FetchResult, HubClient, read_port
from .viewmodel import attention_flags, build_tree, snapshot_age, task_rows

POLL_SECONDS = 5


class HubTuiApp(App):
    TITLE = "Orchestra Hub"

    CSS = """
    #hubstatus {
        dock: top;
        height: 1;
        padding: 0 1;
        background: $panel;
        color: $text;
    }
    #hubstatus.degraded { background: $error 30%; }
    #body { height: 1fr; }
    #body.degraded { opacity: 0.6; }
    #repos { width: 42; border-right: solid $panel; }
    #detail-scroll { padding: 0 1; }
    #detail { margin-bottom: 1; }
    .table-title { text-style: bold; margin-top: 1; }
    DataTable { height: auto; max-height: 12; }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, client: HubClient | None = None) -> None:
        super().__init__()
        self.client = client or HubClient(f"http://127.0.0.1:{read_port()}")
        self.summary: dict | None = None
        self.selected_task_id: str | None = None
        self.fingerprints: dict[str, str] = {}
        self.last_success: datetime | None = None
        self.connection = "starting"

    def compose(self) -> ComposeResult:
        yield Static(id="hubstatus")
        with Horizontal(id="body"):
            yield Tree("Repositories", id="repos")
            with VerticalScroll(id="detail-scroll"):
                yield Static("Select a task.", id="detail")
                yield Static("Activities", classes="table-title")
                yield DataTable(id="activities")
                yield Static("Artifacts", classes="table-title")
                yield DataTable(id="artifacts")
        yield Footer()

    def on_mount(self) -> None:
        tree = self.query_one("#repos", Tree)
        tree.show_root = False
        self.query_one("#activities", DataTable).add_columns(
            "agent", "capability", "state", "summary", "updated"
        )
        self.query_one("#artifacts", DataTable).add_columns(
            "kind", "phase", "producer", "available"
        )
        self.set_interval(POLL_SECONDS, self.action_refresh)
        self.action_refresh()

    def action_refresh(self) -> None:
        self.run_worker(
            self._poll_summary, thread=True, exclusive=True, group="summary"
        )

    def _poll_summary(self) -> None:
        result = self.client.fetch("/v1/summary")
        self.call_from_thread(self._apply_summary, result)

    def _apply_summary(self, result: FetchResult) -> None:
        if result.kind == "ok" and result.payload is not None:
            self.connection = "ok"
            self.last_success = datetime.now(timezone.utc)
            self.summary = result.payload
            fingerprints = {
                str(task.get("id")): str(task.get("material_fingerprint", ""))
                for task in result.payload.get("tasks", ())
            }
            selected = self.selected_task_id
            changed = (
                selected is not None
                and fingerprints.get(selected) != self.fingerprints.get(selected)
            )
            self.fingerprints = fingerprints
            self._rebuild_tree()
            if changed:
                self._load_detail(selected)
        elif result.kind == "not_modified":
            self.connection = "ok"
            self.last_success = datetime.now(timezone.utc)
        elif result.kind == "degraded":
            self.connection = f"degraded ({result.detail or 'database'})"
        else:
            self.connection = "unreachable"
        self._render_status()

    def _render_status(self) -> None:
        status = self.query_one("#hubstatus", Static)
        body = self.query_one("#body")
        healthy = self.connection == "ok"
        status.set_class(not healthy, "degraded")
        body.set_class(not healthy, "degraded")
        active = blockers = 0
        for task in (self.summary or {}).get("tasks", ()):
            if task.get("status") != "completed":
                active += 1
                if str(task.get("blocker", "")):
                    blockers += 1
        if self.last_success is None:
            age = "never"
        else:
            age = snapshot_age(
                self.last_success.isoformat().replace("+00:00", "Z"),
                datetime.now(timezone.utc),
            )
        if healthy:
            text = f"Hub: ok · active {active} · blockers {blockers} · poll {age}"
        else:
            text = (
                f"Hub: {escape(self.connection)} (retrying) · "
                f"showing last data · last poll {age}"
            )
        status.update(text)

    def _rebuild_tree(self) -> None:
        tree = self.query_one("#repos", Tree)
        tree.clear()
        if self.summary is None:
            return
        for node in build_tree(self.summary):
            label = (
                f"{escape(node.name)} "
                f"[dim]({node.active} active / {node.completed} done)[/dim]"
            )
            branch = tree.root.add(label, expand=node.active > 0)
            for task in node.tasks:
                branch.add_leaf(self._task_label(task), data=str(task.get("id")))
        tree.root.expand()

    def _task_label(self, task: dict) -> str:
        flags = attention_flags(task)
        marks = ""
        if "blocker" in flags:
            marks += " [red]⛔[/red]"
        if "stale" in flags:
            marks += " [yellow]stale[/yellow]"
        text = (
            f"{escape(str(task.get('label', '')))} — "
            f"{escape(str(task.get('stage', '')))}/"
            f"{escape(str(task.get('status', '')))}"
        )
        if task.get("status") == "completed":
            return f"[dim]{text}[/dim]"
        return text + marks

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        task_id = event.node.data
        if isinstance(task_id, str):
            self.selected_task_id = task_id
            self._load_detail(task_id)

    def _load_detail(self, task_id: str) -> None:
        self.run_worker(
            lambda: self._poll_detail(task_id),
            thread=True,
            exclusive=True,
            group="detail",
        )

    def _poll_detail(self, task_id: str) -> None:
        result = self.client.fetch(f"/v1/tasks/{task_id}")
        self.call_from_thread(self._apply_detail, task_id, result)

    def _apply_detail(self, task_id: str, result: FetchResult) -> None:
        if task_id != self.selected_task_id:
            return
        detail = self.query_one("#detail", Static)
        if result.kind == "not_modified":
            return
        if result.kind != "ok" or result.payload is None:
            detail.update(
                f"[dim]Task detail unavailable ({escape(result.kind)}).[/dim]"
            )
            return
        payload = result.payload
        task = payload.get("task", {})
        now = datetime.now(timezone.utc)
        lines = []
        for key, value in task_rows(task):
            rendered = escape(value)
            if key == "blocker" and value:
                rendered = f"[bold red]{rendered}[/bold red]"
            if key == "updated_at" and value:
                rendered = f"{rendered} [dim]({escape(snapshot_age(value, now))})[/dim]"
            lines.append(f"[bold]{key:>12}[/bold]  {rendered}")
        detail.update("\n".join(lines))
        activities = self.query_one("#activities", DataTable)
        activities.clear()
        for activity in payload.get("activities", ()):
            activities.add_row(
                str(activity.get("agent_id", "")),
                str(activity.get("capability", "")),
                str(activity.get("state", "")),
                str(activity.get("summary", "")),
                snapshot_age(str(activity.get("updated_at", "")), now),
            )
        artifacts = self.query_one("#artifacts", DataTable)
        artifacts.clear()
        for artifact in payload.get("artifacts", ()):
            artifacts.add_row(
                str(artifact.get("kind", "")),
                str(artifact.get("phase", "")),
                str(artifact.get("producer", "")),
                "yes" if artifact.get("available") else "no",
            )
