import os

from dinky.assistant import Assistant
from dinky.ollama_client import OllamaClient
from dinky.storage import ConversationStore
from dinky.tools.system_status import get_system_status


def main() -> None:
    model = os.getenv("DINKY_MODEL")
    if not model:
        print("Set DINKY_MODEL to a model shown by 'ollama list' first.")
        return

    store = ConversationStore()
    assistant = Assistant(OllamaClient(model), store)
    voice_input = None
    voice_output = None

    print(f"D.I.N.K.Y. is using {model}.")
    print("Commands: /voice, /status, /new, /chats, /use NUMBER, /history, /quit")
    print(f"Current chat: {store.active_conversation()}")

    while True:
        try:
            text = input("You: ").strip()
            spoken_request = False
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if text.lower() == "/quit":
            print("Goodbye!")
            break

        if text.lower() == "/new":
            print(f"Started Chat {store.new_conversation()}.")
            continue

        if text.lower() == "/chats":
            active = store.active_conversation()
            for chat_id, title in store.list_conversations():
                marker = "*" if chat_id == active else " "
                print(f"{marker} {chat_id}: {title}")
            continue

        if text.lower() == "/history":
            messages = store.recent(store.active_conversation())

            if not messages:
                print("This chat has no saved messages.")
            else:
                for message in messages:
                    print(f"{message['role']}: {message['content']}")
            continue

        if text.lower() == "/use" or text.lower().startswith("/use "):
            parts = text.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("Use the command like this: /use 1")
            elif store.select_conversation(int(parts[1])):
                print(f"Switched to Chat {parts[1]}.")
            else:
                print("That chat does not exist.")
            continue

        if text.lower() == "/status":
            status = get_system_status()
            print(f"CPU: {status['cpu_percent']}%")
            print(f"Memory: {status['memory_percent']}%")

            if status["battery_percent"] is not None:
                power = "plugged in" if status["plugged_in"] else "on battery"
                print(f"Battery: {status['battery_percent']}% ({power})")
            else:
                print("Battery: unavailable")
            continue

        if text.lower() == "/voice":
            try:
                if voice_input is None:
                    from dinky.voice.input import VoiceInput

                    voice_input = VoiceInput()

                text = voice_input.listen()

                if not text:
                    print("No speech detected. Please try again.")
                    continue

                print(f"You said: {text}")
                spoken_request = True
            except KeyboardInterrupt:
                print("\nRecording interrupted.")
                continue
            except Exception as error:
                print(f"Voice error: {error}")
                continue

        if text.startswith("/"):
            print(f"Unknown command: {text}")
            continue

        if not text:
            continue

        stream = assistant.stream_reply(
            text, store.active_conversation()
        )

        try:
            pieces = []
            print("D.I.N.K.Y.: ", end="", flush=True)

            for piece in stream:
                pieces.append(piece)
                print(piece, end="", flush=True)

            print()

        except KeyboardInterrupt:
            stream.close()
            print("\nReply interrupted.")
            continue
        except RuntimeError as error:
            print(f"\nError: {error}")
            continue

        if spoken_request:
            try:
                if voice_output is None:
                    from dinky.voice.output import VoiceOutput

                    voice_output = VoiceOutput()

                voice_output.speak("".join(pieces))
            except Exception as error:
                print(f"Speech output error: {error}")


if __name__ == "__main__":
    main()