import os
import subprocess
from pathlib import Path


def open_explorer() -> dict[str, str]:
    if os.name != "nt":
        raise RuntimeError("File Explorer is only available on Windows.")

    windows_dir = os.environ.get("WINDIR")
    if not windows_dir:
        raise RuntimeError("Windows directory was not found.")

    executable = Path(windows_dir) / "explorer.exe"
    if not executable.is_file():
        raise FileNotFoundError(f"File Explorer was not found: {executable}")

    subprocess.Popen([str(executable)], shell=False)
    return {"opened": "File Explorer"}