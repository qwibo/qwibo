@echo off
REM Build installer retail Windows — SOLO macchina di sviluppo (non per utente finale)
REM Uso:
REM   build_installer.bat        prima volta (runtime + installer, 30-60 min)
REM   build_installer.bat fast   rebuild veloce (solo packaging, ~10-15 min)
cd /d "%~dp0"

set FAST=0
if /I "%~1"=="fast" set FAST=1

echo === Qwibo Desktop — build installer ===
if %FAST%==1 (
    echo Modalita FAST: salto pip, solo electron-builder.
) else (
    echo Prima build: torch+NeMo possono richiedere 30-60 minuti.
)
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato.
    pause
    exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
    echo ERRORE: npm/Node.js non trovato.
    pause
    exit /b 1
)

echo [1/5] Sync codice backend...
python scripts\sync_backend.py
if errorlevel 1 exit /b 1

echo [2/5] Build runtime embedded (Python + ffmpeg)...
if %FAST%==1 (
    python scripts\build_runtime.py --skip-pip
    python scripts\verify_runtime.py
) else (
    python scripts\build_runtime.py
)
if errorlevel 1 exit /b 1

echo [3/5] Icona installer (.ico per NSIS)...
set ICON_PY=build\runtime-venv\python.exe
if not exist "%ICON_PY%" set ICON_PY=build\runtime-venv\Scripts\python.exe
if not exist "%ICON_PY%" set ICON_PY=python
"%ICON_PY%" scripts\ensure_icon.py
if errorlevel 1 exit /b 1

echo [4/5] npm install...
set NODE_TLS_REJECT_UNAUTHORIZED=0
call npm install --strict-ssl=false
if errorlevel 1 exit /b 1

echo [5/5] electron-builder NSIS (no code signing)...
set NODE_TLS_REJECT_UNAUTHORIZED=0
set CSC_IDENTITY_AUTO_DISCOVERY=false
call npm run dist:win
if errorlevel 1 exit /b 1

echo.
echo === FATTO ===
echo Installer: release\Qwibo-Setup-0.1.0.exe
echo Distribuisci SOLO quel file agli utenti finali.
echo.
echo Prossimo rebuild veloce: build_installer.bat fast
pause
