@echo off
Echo Deleting Old Program...
taskkill /f /im main.exe >nul 2>&1
Echo Building...
pyinstaller --noconfirm --onedir --windowed --name sprout ^
  --icon "assets/icon.ico" ^
  --add-data "assets;assets" ^
  --add-data "data;data" ^
  --add-data "event_list;event_list" ^
  main.py
pause