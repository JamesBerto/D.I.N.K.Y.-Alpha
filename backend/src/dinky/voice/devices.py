import sounddevice as sd


def main() -> None:
    default_input = sd.default.device[0]
    found = False

    print("Available microphones:")

    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] <= 0:
            continue

        found = True
        marker = " [default]" if index == default_input else ""
        print(
            f"{index}: {device['name']}"
            f" — {device['max_input_channels']} input channel(s)"
            f"{marker}"
        )

    if not found:
        print("No microphone input device was found.")


if __name__ == "__main__":
    main()