from comtypes.client import CreateObject


class VoiceOutput:
    def __init__(self) -> None:
        self.speaker = CreateObject("SAPI.SpVoice")
        self.speaker.Rate = 0
        self.speaker.Volume = 100

        # Prefer Microsoft David when available.
        voices = self.speaker.GetVoices()
        for index in range(voices.Count):
            candidate = voices.Item(index)
            if "david" in candidate.GetDescription().lower():
                self.speaker.Voice = candidate
                break

    def speak(self, text: str) -> None:
        if text.strip():
            self.speaker.Speak(text)