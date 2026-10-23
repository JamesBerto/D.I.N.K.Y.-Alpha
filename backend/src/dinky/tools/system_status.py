import json

import psutil


def get_system_status() -> dict:
    battery = psutil.sensors_battery()

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": psutil.virtual_memory().percent,
        "battery_percent": battery.percent if battery else None,
        "plugged_in": battery.power_plugged if battery else None,
    }


if __name__ == "__main__":
    print(json.dumps(get_system_status(), indent=2))