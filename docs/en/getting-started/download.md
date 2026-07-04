# Download & install

Qwibo ships as a single Windows installer. No Python, ffmpeg, or Docker setup required.

## Download

1. Open [GitHub Releases](https://github.com/qwibo/qwibo/releases) for the **qwibo** repository.
2. Download the latest **`Qwibo-Setup-*.exe`** (alpha builds are tagged `0.1.0-alpha.*`).
3. File size is roughly **2–3 GB** — the installer bundles the runtime; models download on first run.

## Install

1. Double-click the installer.
2. Accept the license and choose an install folder (default is fine).
3. Finish the wizard — Qwibo opens automatically.

!!! warning "Windows SmartScreen"
    The alpha installer is **not code-signed yet**. Windows may show *"Windows protected your PC"*.  
    Click **More info** → **Run anyway**. See [SmartScreen](../troubleshooting/smartscreen.md).

## After install

On first launch you will see the **model setup** wizard (~4–5 GB download, one time only):

| Model | Size | Required |
|-------|------|----------|
| Parakeet ASR | ~2.5 GB | Yes |
| Qwen summary (local) | ~2 GB | Only if RAM ≥ 16 GB |

When setup completes, the main window opens and you can queue your first file. See [First run](first-run.md).

## Uninstall

Windows **Settings → Apps → Qwibo → Uninstall**.

User data in `%APPDATA%\qwibo-desktop\` is **not** removed automatically. Delete that folder if you want a clean reinstall.

## Self-hosted Docker

If you prefer a browser UI on a home server instead of the desktop app, use [qwibo-docker](https://github.com/qwibo/qwibo-docker) — separate repo, separate docs (not published on this site).
