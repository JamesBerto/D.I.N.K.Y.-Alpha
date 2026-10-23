from dinky.voice.recorder import MicrophoneRecorder
from dinky.voice.transcriber import SpeechTranscriber


class VoiceInput:
    def __init__(self) -> None:
        self.recorder = MicrophoneRecorder()
        self.transcriber = SpeechTranscriber()

    def listen(self) -> str:
        self.recorder.start()

        try:
            print("Recording. Speak, then press Enter to stop.")
            input()
        finally:
            audio = self.recorder.stop()

        if not audio:
            return ""

        print("Transcribing...")
        return self.transcriber.transcribe(audio)