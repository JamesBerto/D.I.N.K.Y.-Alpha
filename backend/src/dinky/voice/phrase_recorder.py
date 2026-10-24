from collections import deque
from io import BytesIO
from time import monotonic
import wave

import numpy as np
import sounddevice as sd


class PhraseRecorder:
    def __init__(self) -> None:
        self.start_timeout = 5.0
        self.max_duration = 12.0
        self.pause_duration = 1.8
        self.speech_rms = 0.004

    def record(self) -> bytes:
        sample_rate = int(
            sd.query_devices(kind="input")["default_samplerate"]
        )
        block_frames = max(1, sample_rate // 10)  # About 100 ms
        pre_roll: deque[np.ndarray] = deque(maxlen=5)
        captured: list[np.ndarray] = []

        started_at = monotonic()
        speech_started = False
        last_speech_at = started_at

        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            blocksize=block_frames,
        ) as stream:
            while True:
                block, overflowed = stream.read(block_frames)
                if overflowed:
                    raise RuntimeError("Microphone audio was lost. Try again.")

                now = monotonic()
                samples = block.astype(np.float32) / 32768
                rms = float(np.sqrt(np.mean(samples * samples)))
                speaking = rms >= self.speech_rms

                if not speech_started:
                    if speaking:
                        speech_started = True
                        captured.extend(pre_roll)
                        captured.append(block.copy())
                        last_speech_at = now
                    else:
                        pre_roll.append(block.copy())
                        if now - started_at >= self.start_timeout:
                            return b""
                else:
                    captured.append(block.copy())

                    if speaking:
                        last_speech_at = now

                    if (
                        now - last_speech_at >= self.pause_duration
                        or now - started_at >= self.max_duration
                    ):
                        break

        recording = BytesIO()
        with wave.open(recording, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(np.concatenate(captured).tobytes())

        return recording.getvalue()