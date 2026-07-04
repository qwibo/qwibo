# Overview

Qwibo turns audio and video into text you can search, edit, and reuse — on your own Windows PC.

## How it works

```text
Installer (Electron)
    └── Embedded Python backend (FastAPI + worker)
            ├── Parakeet ASR  → trascrizione.txt + sottotitoli.srt
            └── Optional LLM  → riassunto.txt
```

You interact through a **desktop window** (not a browser tab you manage yourself). The app starts the backend automatically and keeps it running in the tray while Qwibo is open.

## Design principles

1. **Local transcription** — after the one-time model download, audio is not sent to the cloud for ASR.
2. **Offline models** — Parakeet and optional Qwen GGUF live under your user profile.
3. **No overwrites** — each job gets its own timestamped folder.
4. **One job at a time** — the worker processes the queue sequentially to limit RAM use.

## Data location

All user data is under **Electron userData** (typically):

```text
%APPDATA%\qwibo-desktop\
├── data\           ← jobs, input, output, secrets
├── models\         ← Parakeet .nemo + optional Qwen GGUF
├── logs\           ← diagnostic logs (tray → Open log folder)
└── cache\          ← internal caches (numba, matplotlib)
```

!!! tip "Open logs"
    Right-click the Qwibo tray icon → **Open log folder** if something fails during setup or transcription.

## Alpha status

Current channel: **0.1.0-alpha** — Windows installer, unsigned (SmartScreen warning). Mac and code signing are planned.

## Next steps

- [Download & install](download.md)
- [System requirements](system-requirements.md)
- [First run](first-run.md)
- [Models](models.md)
