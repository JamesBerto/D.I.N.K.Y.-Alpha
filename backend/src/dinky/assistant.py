from typing import Iterator

from dinky.ollama_client import OllamaClient
from dinky.storage import ConversationStore


class Assistant:
    def __init__(self, client: OllamaClient, store: ConversationStore) -> None:
        self.client = client
        self.store = store

    def reply(self, text: str, chat_id: int) -> str:
        return "".join(self.stream_reply(text, chat_id))

    def stream_reply(self, text: str, chat_id: int) -> Iterator[str]:
        messages = [
            {
                "role": "system",
                "content": (
                "You are D.I.N.K.Y., James's local AI assistant. "
                "Address James as sir when it sounds natural. "
                "You run through Ollama on his computer. "
                "Do not claim you are accessible remotely or that you have "
                "performed actions unless the application actually provides "
                "that capability. If you do not know something, say so."
),
            },
            *self.store.recent(chat_id),
            {"role": "user", "content": text},
        ]

        pieces = []
        for piece in self.client.stream_chat(messages):
            pieces.append(piece)
            yield piece

        answer = "".join(pieces)
        if not answer.strip():
            raise RuntimeError("Ollama returned an empty reply.")

        self.store.add_pair(chat_id, text, answer)