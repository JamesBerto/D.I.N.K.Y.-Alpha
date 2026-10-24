from dinky.voice.phrase_recorder import PhraseRecorder
from dinky.voice.transcriber import SpeechTranscriber
from dinky.voice.wake import request_after_wake_word


class WakeListener:
    def __init__(self) -> None:
        self.recorder = PhraseRecorder()
        self.transcriber = SpeechTranscriber()

    def _hear(self) -> str:
        audio = self.recorder.record()
        if not audio:
            return ""

        return self.transcriber.transcribe(audio).strip()

    def wait_for_request(self) -> str:
        print("Listening for Dinky. Press Ctrl+C to stop.")

        while True:
            text = self._hear()
            if not text:
                continue

            print(f"Heard: {text}")
            request = request_after_wake_word(text)
            if request is None:
                continue

            if request:
                return request

            print("Yes, sir? Speak your request now.")
            return self._hear()