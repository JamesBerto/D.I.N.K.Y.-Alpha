from io import BytesIO
import wave

import numpy as np

from dinky.voice.recorder import MicrophoneRecorder
from dinky.voice.transcriber import SpeechTranscriber
from dinky.voice.wake import request_after_wake_word


class WakeListener:
    def __init__(self) -> None:
        self.recorder = MicrophoneRecorder()
        self.transcriber = SpeechTranscriber()
        self.minimum_rms = 0.002
        self.recording_seconds = 4

    def _rms(self, audio: bytes) -> float:
        with wave.open(BytesIO(audio), "rb") as wav:
            samples = np.frombuffer(
                wav.readframes(wav.getnframes()), dtype=np.int16
            ).astype(np.float32) / 32768

        if samples.size == 0:
            return 0.0

        return float(np.sqrt(np.mean(samples * samples)))

    def _hear(self) -> str:
        audio = self.recorder.record_for(self.recording_seconds)
        if not audio or self._rms(audio) < self.minimum_rms:
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