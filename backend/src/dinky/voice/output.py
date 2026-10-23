import pyttsx3


class VoiceOutput:
    def __init__(self) -> None:
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 175)

        # Prefer the Windows David voice when it is installed.
        for voice in self.engine.getProperty("voices"):
            if "david" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def speak(self, text: str) -> None:
        if text.strip():
            self.engine.say(text)
            self.engine.runAndWait()