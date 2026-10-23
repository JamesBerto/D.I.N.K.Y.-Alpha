from dinky.voice.output import VoiceOutput


def main() -> None:
    print("Testing D.I.N.K.Y.'s voice...")
    VoiceOutput().speak("At your service, sir.")
    print("Playback finished.")


if __name__ == "__main__":
    main()