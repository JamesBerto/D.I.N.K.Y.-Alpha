import tempfile
import unittest
from pathlib import Path

from dinky.audit import AuditStore
from dinky.tools.router import ToolRouter


class ToolPolicyTests(unittest.TestCase):
    def test_unknown_tool_is_denied_and_logged(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            audit = AuditStore(Path(folder) / "test.sqlite3")
            router = ToolRouter(audit)

            with self.assertRaises(PermissionError):
                router.execute("system.delete_file", "test")

            events = audit.recent()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0]["outcome"], "denied")
            self.assertEqual(events[0]["tool_name"], "system.delete_file")
            self.assertTrue(audit.verify())


if __name__ == "__main__":
    unittest.main()