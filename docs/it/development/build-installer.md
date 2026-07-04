# Creare l'installer Windows

Sezione per **sviluppatori**. L'utente finale usa solo l'`.exe` dalle Release.

## Prerequisiti

Windows 10/11, Python 3.12+, Node.js 20+.

## Comandi

```bat
cd desktop-electron
build_installer.bat          REM prima build (30–60 min)
build_installer.bat fast     REM incrementale (~10–15 min)
```

Output: `desktop-electron\release\Qwibo-Setup-*.exe`

## Cosa fa la build

1. Sync backend in `backend/vendor/`
2. Python standalone + `runtime-venv` (torch, NeMo, FastAPI)
3. ffmpeg statico
4. Electron + NSIS

**Prima build:** 20–40 min. **Installer:** ~2–3 GB.

## Dev rapido

Dopo `install.bat`:

```bat
npm run dev
```

## Verifica runtime

```bat
python scripts\verify_runtime.py
```

Controlla baseline llama-cpp (no AVX).

Vedi `desktop-electron/README.md` nel repo.
