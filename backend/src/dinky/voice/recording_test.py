import os
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd


def main() -> None:
    seconds = 5
    sample_rate = int(sd.query_devices(kind="input")["default_samplerate"])

    print("Recording for 5 seconds. Speak into your microphone...")
    audio = sd.rec(
        int(seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()

    peak = np.max(np.abs(audio.astype(np.int32))) / 32768 * 100

    data_dir = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "DINKY"
    data_dir.mkdir(parents=True, exist_ok=True)
    output = data_dir / "voice_test.wav"

    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio.tobytes())

    print(f"Peak microphone level: {peak:.1f}%")
    print(f"Recording saved to: {output}")


if __name__ == "__main__":
    main()