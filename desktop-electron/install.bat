@echo off
REM Solo SVILUPPO — gli utenti finali usano Qwibo-Setup.exe
cd /d "%~dp0"
echo Per installer retail usa: build_installer.bat
echo.
python scripts\sync_backend.py
python scripts\install_backend.py
call npm install
echo Avvia: npm run dev
pause
