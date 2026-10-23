import json
from typing import Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaClient:
    def __init__(self, model: str) -> None:
        self.model = model
        self.url = "http://127.0.0.1:11434/api/chat"

    def chat(self, messages: list[dict[str, str]]) -> str:
        return "".join(self.stream_chat(messages))

    def stream_chat(
        self, messages: list[dict[str, str]]
    ) -> Iterator[str]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        request = Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                finished = False

                for line in response:
                    if not line.strip():
                        continue

                    chunk = json.loads(line)

                    if chunk.get("error"):
                        raise RuntimeError(
                            f"Ollama error: {chunk['error']}"
                        )

                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content

                    if chunk.get("done"):
                        finished = True
                        break

                if not finished:
                    raise RuntimeError(
                        "Ollama ended its response before completion."
                    )

        except HTTPError as error:
            raise RuntimeError(
                f"Ollama rejected the request (HTTP {error.code}). "
                "Check your model name."
            ) from error
        except URLError as error:
            raise RuntimeError(
                "Cannot connect to Ollama. Make sure Ollama is running."
            ) from error
        except ValueError as error:
            raise RuntimeError(
                "Ollama sent an invalid response."
            ) from error