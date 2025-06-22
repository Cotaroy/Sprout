import os
import sys
from pathlib import Path

def add_to_startup(app_name="Sprout", exe_path=None):
    if exe_path is None:
        exe_path = sys.executable  # This points to the .exe if bundled with PyInstaller

    startup_dir = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_dir / f"{app_name}.lnk"

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = str(exe_path)
        shortcut.WorkingDirectory = str(Path(exe_path).parent)
        shortcut.IconLocation = str(exe_path)
        shortcut.save()
        print(f"Startup shortcut created at: {shortcut_path}")
    except Exception as e:
        print("Failed to add to startup:", e)