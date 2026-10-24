import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


def event_hash(
    event_id: int,
    tool_name: str,
    source: str,
    outcome: str,
    created_at: str,
    previous_hash: str,
) -> str:
    data = {
        "id": event_id,
        "tool_name": tool_name,
        "source": source,
        "outcome": outcome,
        "created_at": created_at,
        "previous_hash": previous_hash,
    }
    encoded = json.dumps(
        data, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class AuditStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

        with closing(sqlite3.connect(self.db_path)) as db:
            with db:
                db.execute("""
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tool_name TEXT NOT NULL,
                        source TEXT NOT NULL,
                        outcome TEXT NOT NULL
                            CHECK (outcome IN ('succeeded', 'failed', 'denied')),
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        previous_hash TEXT NOT NULL DEFAULT '',
                        entry_hash TEXT NOT NULL DEFAULT ''
                    )
                """)

                columns = {
                    row[1]
                    for row in db.execute("PRAGMA table_info(audit_events)")
                }
                needs_migration = (
                    "previous_hash" not in columns
                    or "entry_hash" not in columns
                )

                if "previous_hash" not in columns:
                    db.execute(
                        "ALTER TABLE audit_events "
                        "ADD COLUMN previous_hash TEXT NOT NULL DEFAULT ''"
                    )
                if "entry_hash" not in columns:
                    db.execute(
                        "ALTER TABLE audit_events "
                        "ADD COLUMN entry_hash TEXT NOT NULL DEFAULT ''"
                    )

                # Seal the records created before hashes were introduced.
                if needs_migration:
                    rows = db.execute(
                        """
                        SELECT id, tool_name, source, outcome, created_at
                        FROM audit_events
                        ORDER BY id
                        """
                    ).fetchall()

                    previous = ""
                    for event_id, tool, source, outcome, created_at in rows:
                        digest = event_hash(
                            event_id, tool, source, outcome,
                            created_at, previous
                        )
                        db.execute(
                            """
                            UPDATE audit_events
                            SET previous_hash = ?, entry_hash = ?
                            WHERE id = ?
                            """,
                            (previous, digest, event_id),
                        )
                        previous = digest

    def record(self, tool_name: str, source: str, outcome: str) -> None:
        if outcome not in ("succeeded", "failed", "denied"):
            raise ValueError(f"Invalid audit outcome: {outcome}")

        created_at = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with closing(sqlite3.connect(self.db_path, timeout=10)) as db:
            with db:
                db.execute("BEGIN IMMEDIATE")

                last = db.execute(
                    "SELECT entry_hash FROM audit_events ORDER BY id DESC LIMIT 1"
                ).fetchone()
                previous = last[0] if last else ""

                cursor = db.execute(
                    """
                    INSERT INTO audit_events
                        (tool_name, source, outcome, created_at, previous_hash)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (tool_name, source, outcome, created_at, previous),
                )
                event_id = int(cursor.lastrowid)
                digest = event_hash(
                    event_id, tool_name, source, outcome,
                    created_at, previous
                )

                db.execute(
                    "UPDATE audit_events SET entry_hash = ? WHERE id = ?",
                    (digest, event_id),
                )

    def verify(self) -> bool:
        with closing(sqlite3.connect(self.db_path)) as db:
            rows = db.execute(
                """
                SELECT id, tool_name, source, outcome, created_at,
                       previous_hash, entry_hash
                FROM audit_events
                ORDER BY id
                """
            ).fetchall()

        previous = ""
        for event_id, tool, source, outcome, created_at, linked, saved in rows:
            if linked != previous:
                return False

            expected = event_hash(
                event_id, tool, source, outcome,
                created_at, previous
            )
            if saved != expected:
                return False

            previous = saved

        return True

    def recent(self, limit: int = 10) -> list[dict]:
        with closing(sqlite3.connect(self.db_path)) as db:
            rows = db.execute(
                """
                SELECT id, tool_name, source, outcome, created_at
                FROM audit_events
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "id": event_id,
                "tool_name": tool_name,
                "source": source,
                "outcome": outcome,
                "created_at": created_at,
            }
            for event_id, tool_name, source, outcome, created_at in rows
        ]