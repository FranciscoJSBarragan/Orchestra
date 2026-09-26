from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / "hosts/cursor/plugin"
SPAWN = ROOT / "hosts/cursor/references/spawn.md"


class CursorHostTests(unittest.TestCase):




    def test_spawn_maps_browser_routes_to_browser_use(self) -> None:
        spawn = SPAWN.read_text(encoding="utf-8")
        self.assertIn("`auto` and `chrome` map to Browser Use", spawn)
        self.assertIn("plugin-browser-use-browser-use", spawn)
        self.assertIn("new_tab", spawn)
        self.assertNotIn("maps to Playwright", spawn)
        self.assertNotIn("map to Playwright", spawn)


if __name__ == "__main__":
    unittest.main()
