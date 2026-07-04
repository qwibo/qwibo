# Build the Windows installer

This section is for **developers** packaging Qwibo. End users only need the `.exe` from Releases.

## Prerequisites

| Tool | Version |
|------|---------|
| Windows | 10/11 64-bit |
| Python | 3.12+ |
| Node.js | 20+ |

## Build commands

```bat
cd desktop-electron
build_installer.bat          REM first build (30–60 min)
build_installer.bat fast     REM incremental (~10–15 min)
```

Output: `desktop-electron\release\Qwibo-Setup-*.exe`

## What the build does

1. Syncs backend into `backend/vendor/` (`sync_backend.py`)
2. Downloads standalone Python + creates `runtime-venv` (torch, NeMo, FastAPI)
3. Bundles static ffmpeg
4. Packages Electron + NSIS installer

**First build:** 20–40 min (large PyTorch/NeMo download).  
**Installer size:** ~2–3 GB (normal for offline ASR).

## Dev mode (no installer)

After `install.bat` in `desktop-electron/`:

```bat
npm run dev
```

Uses local venv instead of embedded runtime.

## Runtime verification

```bat
cd desktop-electron
python scripts\verify_runtime.py
```

Checks llama-cpp baseline (no AVX) on target hardware.

## Independence from qwibo-docker

| | Desktop installer | qwibo-docker |
|---|---|---|
| Python | Embedded | Container |
| ffmpeg | Bundled | In image |
| User data | `%APPDATA%\qwibo-desktop\` | Docker volume |

See `desktop-electron/README.md` in the repo for release notes and troubleshooting.
