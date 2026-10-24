from io import BytesIO
import time
import wave

import numpy as np
import sounddevice as sd


class MicrophoneRecorder:
    def __init__(self) -> None:
        self._stream = None
        self._chunks: list[np.ndarray] = []
        self._sample_rate = 0

    def _on_audio(self, indata, frames, time_info, status) -> None:
        self._chunks.append(indata.copy())

    def start(self) -> None:
        if self._stream is not None:
            raise RuntimeError("Microphone is already recording.")

        self._chunks = []
        self._sample_rate = int(
            sd.query_devices(kind="input")["default_samplerate"]
        )

        stream = sd.InputStream(
            samplerate=self._sample_rate,
            channels=1,
            dtype="int16",
            callback=self._on_audio,
        )

        try:
            stream.start()
        except Exception:
            stream.close()
            raise

        self._stream = stream

    def stop(self) -> bytes:
        if self._stream is None:
            raise RuntimeError("Microphone is not recording.")

        stream = self._stream
        self._stream = None

        try:
            stream.stop()
        finally:
            stream.close()

        if not self._chunks:
            return b""

        audio = np.concatenate(self._chunks)
        recording = BytesIO()

        with wave.open(recording, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self._sample_rate)
            wav.writeframes(audio.tobytes())

        return recording.getvalue()

    def record_for(self, seconds: float) -> bytes:
        if seconds <= 0 or seconds > 30:
            raise ValueError("Recording duration must be between 0 and 30 seconds.")

        self.start()
        try:
            time.sleep(seconds)
        finally:
            audio = self.stop()

        return audio