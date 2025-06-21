import os
import sys
import shutil
from pathlib import Path

def add_to_startup(app_name="Cornerpond", exe_path=None): #fix this later for accessing pyscript
    if exe_path is None:
        exe_path = sys.executable  # This points to your .exe when bundled
    startup_dir = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    shortcut_path = startup_dir / f"{app_name}.lnk"

    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(str(shortcut_path))
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = str(Path(exe_path).parent)
        shortcut.IconLocation = exe_path
        shortcut.save()
        print("Added to startup.")
    except Exception as e:
        print("Failed to add to startup:", e)
