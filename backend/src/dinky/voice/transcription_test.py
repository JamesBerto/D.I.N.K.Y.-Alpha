import os
from pathlib import Path

from faster_whisper import WhisperModel


def main() -> None:
    recording = (
        Path(os.environ.get("LOCALAPPDATA") or Path.home())
        / "DINKY"
        / "voice_test.wav"
    )

    if not recording.exists():
        print(f"Recording not found: {recording}")
        return

    print("Loading speech recognition model...")
    model = WhisperModel("base.en", device="cpu", compute_type="int8")

    print("Transcribing your recording...")
    segments, _ = model.transcribe(str(recording), language="en")
    transcript = " ".join(segment.text.strip() for segment in segments).strip()

    print(f"You said: {transcript or '(no speech detected)'}")


if __name__ == "__main__":
    main()