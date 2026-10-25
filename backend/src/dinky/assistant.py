from typing import Iterator

from dinky.ollama_client import OllamaClient
from dinky.storage import ConversationStore

SYSTEM_PROMPT = (
    "You are D.I.N.K.Y., James's local AI assistant. "
    "Address James as sir when it sounds natural. "
    "You run locally through Ollama on his computer. "
    "You can receive transcribed speech and speak replies when voice mode is active. "
    "Do not claim you are accessible remotely. "
    "You can answer questions using the conversation, but you cannot see "
    "his screen, inspect files, browse the web, or directly observe his "
    "computer through this chat. "
    "The application has separate commands for reading live CPU, memory, "
    "and battery status and for opening File Explorer. Do not invent "
    "readings or claim that you ran those commands. "
    "There is no 'Ollama OS'; Ollama runs the AI model and is not the "
    "computer's operating system. "
    "Do not invent hardware specifications, dates, network status, screen "
    "contents, or actions you performed. If you lack the information, "
    "say so briefly and explain what information you would need. "
    "Earlier assistant messages may contain mistakes; do not treat their "
    "claims about your capabilities or the computer as verified facts."
)
class Assistant:
    def __init__(self, client: OllamaClient, store: ConversationStore) -> None:
        self.client = client
        self.store = store

    def reply(self, text: str, chat_id: int) -> str:
        return "".join(self.stream_reply(text, chat_id))

    def stream_reply(self, text: str, chat_id: int) -> Iterator[str]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
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