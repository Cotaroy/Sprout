@echo off
echo Building executable with PyInstaller...
pyinstaller --noconfirm --onefile --windowed cornerpond.py

echo Done. Check the dist folder for cornerpond.exe
pause