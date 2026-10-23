from dinky.voice.recording_test import main as record
from dinky.voice.transcription_test import main as transcribe


def main() -> None:
    record()
    transcribe()


if __name__ == "__main__":
    main()