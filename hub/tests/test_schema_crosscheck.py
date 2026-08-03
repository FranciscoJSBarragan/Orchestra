import unittest

import support  # noqa: F401  (sys.path setup)
import coordination
from orchestra_hub.db import SUPPORTED_SCHEMA_VERSIONS


class SchemaCrossCheckTest(unittest.TestCase):
    def test_hub_supports_installed_coordination_schema(self) -> None:
        self.assertIn(
            coordination.SCHEMA_VERSION, SUPPORTED_SCHEMA_VERSIONS,
            "coordination.SCHEMA_VERSION changed. Review Hub compatibility "
            "(fields, queries, fingerprint), then update "
            "SUPPORTED_SCHEMA_VERSIONS deliberately.",
        )
