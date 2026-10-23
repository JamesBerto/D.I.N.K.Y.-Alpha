import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class ConversationStore:
    def __init__(self) -> None:
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home())
        data_dir = base / "DINKY"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / "dinky.sqlite3"

        with self._db() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL
                )
            """)
            db.execute(
                "INSERT OR IGNORE INTO conversations (id, title) "
                "VALUES (1, 'Original chat')"
            )

            db.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    conversation_id INTEGER NOT NULL DEFAULT 1
                )
            """)

            # Upgrade the database created in Step 3 without deleting its messages.
            columns = {
                row[1] for row in db.execute("PRAGMA table_info(messages)")
            }
            if "conversation_id" not in columns:
                db.execute(
                    "ALTER TABLE messages "
                    "ADD COLUMN conversation_id INTEGER NOT NULL DEFAULT 1"
                )

            db.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages (conversation_id, id)
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            db.execute(
                "INSERT OR IGNORE INTO settings (key, value) "
                "VALUES ('active_conversation', '1')"
            )

    @contextmanager
    def _db(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def active_conversation(self) -> int:
        with self._db() as db:
            row = db.execute(
                "SELECT value FROM settings WHERE key = 'active_conversation'"
            ).fetchone()
        return int(row[0])

    def list_conversations(self) -> list[tuple[int, str]]:
        with self._db() as db:
            return db.execute(
                "SELECT id, title FROM conversations ORDER BY id"
            ).fetchall()

    def new_conversation(self, activate: bool = True) -> int:
        with self._db() as db:
            cursor = db.execute(
                "INSERT INTO conversations (title) VALUES ('New chat')"
            )
            chat_id = int(cursor.lastrowid)

            db.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (f"Chat {chat_id}", chat_id),
            )

            if activate:
                db.execute(
                    "UPDATE settings SET value = ? "
                    "WHERE key = 'active_conversation'",
                    (str(chat_id),),
                )

        return chat_id

    def select_conversation(self, chat_id: int) -> bool:
        with self._db() as db:
            exists = db.execute(
                "SELECT 1 FROM conversations WHERE id = ?", (chat_id,)
            ).fetchone()
            if not exists:
                return False

            db.execute(
                "UPDATE settings SET value = ? "
                "WHERE key = 'active_conversation'",
                (str(chat_id),),
            )
        return True

    def recent(
        self, chat_id: int, limit: int = 20
    ) -> list[dict[str, str]]:
        with self._db() as db:
            rows = db.execute(
                """
                SELECT role, content
                FROM (
                    SELECT id, role, content
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC
                """,
                (chat_id, limit),
            ).fetchall()

        return [{"role": role, "content": content} for role, content in rows]

    def add_pair(
        self, chat_id: int, user_text: str, assistant_text: str
    ) -> None:
        with self._db() as db:
            db.execute(
                "INSERT INTO messages (conversation_id, role, content) "
                "VALUES (?, 'user', ?)",
                (chat_id, user_text),
            )
            db.execute(
                "INSERT INTO messages (conversation_id, role, content) "
                "VALUES (?, 'assistant', ?)",
                (chat_id, assistant_text),
            )