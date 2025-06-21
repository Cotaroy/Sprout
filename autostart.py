import os
import sys
from pathlib import Path

def add_to_startup(app_name="Cornerpond", exe_path=None):
    if exe_path is None:
        exe_path = (Path(__file__).parent / "dist" / "main.exe").resolve()

    if not exe_path.exists():
        print(f"Executable not found: {exe_path}")
        return

    startup_dir = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_dir / f"{app_name}.lnk"

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))  # Must be str
        shortcut.TargetPath = str(exe_path)                  # Must be str
        shortcut.WorkingDirectory = str(exe_path.parent)     # Must be str
        shortcut.IconLocation = str(exe_path)                # Must be str
        shortcut.save()
        print(f"Startup shortcut created at: {shortcut_path}")
    except Exception as e:
        print("Failed to add to startup:", e)