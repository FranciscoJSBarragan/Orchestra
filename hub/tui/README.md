# Orchestra Hub TUI

Terminal dashboard for the Orchestra Hub (read-only). See
`../SPEC-CLIENTS.md` for the frozen design.

## Setup

```sh
cd hub/tui
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Requires Python 3.11+ and a running Hub (`python3 -m orchestra_hub`).

## Run

```sh
cd hub/tui
.venv/bin/python -m orchestra_hub_tui
```

Keys: arrows/`j`/`k` navigate, `r` refresh, `q` quit.

## Tests

The client and view-model tests are stdlib-only (no venv needed):

```sh
python3 -m unittest discover -s hub/tui/tests -v   # from the repo root
```
