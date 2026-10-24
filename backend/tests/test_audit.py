import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from dinky.audit import AuditStore


class AuditChainTests(unittest.TestCase):
    def test_changed_record_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            db_path = Path(folder) / "test.sqlite3"
            audit = AuditStore(db_path)

            audit.record("system.status", "cli", "succeeded")
            audit.record("system.status", "api", "succeeded")
            self.assertTrue(audit.verify())

            # Change only the temporary test database.
            with closing(sqlite3.connect(db_path)) as db:
                with db:
                    db.execute(
                        "UPDATE audit_events SET outcome = 'failed' WHERE id = 1"
                    )

            self.assertFalse(audit.verify())


if __name__ == "__main__":
    unittest.main()