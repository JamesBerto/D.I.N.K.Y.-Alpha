from io import BytesIO
from threading import Lock

from faster_whisper import WhisperModel


class SpeechTranscriber:
    def __init__(self) -> None:
        self.model: WhisperModel | None = None
        self.lock = Lock()

    def transcribe(self, audio: bytes) -> str:
        with self.lock:
            if self.model is None:
                self.model = WhisperModel(
                    "base.en", device="cpu", compute_type="int8"
                )

            segments, _ = self.model.transcribe(
                BytesIO(audio), language="en"
            )
            return " ".join(
                segment.text.strip() for segment in segments
            ).strip()