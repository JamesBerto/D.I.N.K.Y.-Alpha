from io import BytesIO
import wave

import numpy as np

from dinky.voice.recorder import MicrophoneRecorder
from dinky.voice.transcriber import SpeechTranscriber
from dinky.voice.wake import request_after_wake_word


def audio_levels(audio: bytes) -> tuple[float, float]:
    with wave.open(BytesIO(audio), "rb") as wav:
        samples = np.frombuffer(
            wav.readframes(wav.getnframes()), dtype=np.int16
        ).astype(np.float32) / 32768

    if samples.size == 0:
        return 0.0, 0.0

    peak = float(np.max(np.abs(samples)))
    rms = float(np.sqrt(np.mean(samples * samples)))
    return peak, rms


def main() -> None:
    recorder = MicrophoneRecorder()
    transcriber = SpeechTranscriber()

    print("Listening in four-second recordings. Press Ctrl+C to stop.")

    try:
        while True:
            audio = recorder.record_for(4)
            if not audio:
                continue

            peak, rms = audio_levels(audio)
            print(f"Levels: peak={peak:.1%}, rms={rms:.2%}")
            if rms < 0.002:  # 0.2% RMS; based on this microphone test
                print("Skipped quiet recording.")
                continue

            text = transcriber.transcribe(audio).strip()
            if text:
                print(f"Heard: {text}")

            request = request_after_wake_word(text)
            if request is None:
                continue

            print("Wake word detected.")
            print(f"Request: {request or '(waiting for a request)'}")
            break
    except KeyboardInterrupt:
        print("\nStopped listening.")


if __name__ == "__main__":
    main()