from dinky.voice.phrase_recorder import PhraseRecorder
from dinky.voice.transcriber import SpeechTranscriber


def main() -> None:
    print("Speak a full request, then pause.")
    audio = PhraseRecorder().record()

    if not audio:
        print("No speech detected.")
        return

    print("Transcribing...")
    print("Heard:", SpeechTranscriber().transcribe(audio))


if __name__ == "__main__":
    main()
