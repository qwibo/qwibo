# App interface

The Qwibo desktop window embeds the same **FastAPI + HTMX** UI used in development, bound to `127.0.0.1` on a free local port (starting around **8765**). You never type a URL — Electron opens it for you.

## Starting and quitting

| Action | How |
|--------|-----|
| Start | Launch from Start menu or desktop shortcut |
| Minimize | Close button → app stays in **tray** |
| Quit | Tray → **Quit** (stops backend worker) |

Only **one instance** runs at a time. Opening Qwibo again focuses the existing window.

---

## Navigation

| Screen | Path | Description |
|--------|------|-------------|
| Home | `/` | Upload, live queue, recent jobs sidebar |
| Queue & history | `/jobs` | Full table, filters, actions |
| Job detail | `/jobs/{id}` | Transcript, summary, downloads, progress |
| Summary settings | `/settings/summary` | API keys, engine status |
| License | `/settings/license` | Terms, doc links |

---

## Home (`/`)

- Drag-and-drop or file picker upload
- Sidebar: **Generate summary**, engine, length
- Active queue panel (updates every ~2 s)
- Sidebar lists latest **8** jobs with links to detail pages

After enqueueing, you are redirected to **`/jobs/{id}`**.

---

## Queue & history (`/jobs`)

Table of all jobs with search and filters. Click the file name or **Open** to view details.

---

## Job detail (`/jobs/{id}`)

- **In progress**: progress bar with auto-refresh until complete
- **Completed**: transcript, summary, download buttons (TXT / SRT / summary)
- **Open folder** — opens the job directory in Explorer
- Actions: cancel (queued only), retry, reprocess, delete

---

## Summary settings (`/settings/summary`)

- Enter cloud provider API keys
- See which engines are available
- Local Qwen status and RAM check

---

## Background worker

When the UI starts, a **separate Python process** runs the transcription worker (NeMo does not run inside the web server process).

If Qwibo crashes, orphaned `running` jobs are recovered on the next start.

---

## Tips

- First job after cold start: **1–2 minutes** to load Parakeet into RAM
- Same file twice → **two folders** with different timestamps — use `/jobs` to tell them apart
- Logs: tray → **Open log folder**

See [Jobs & output](jobs-and-output.md) for queue logic.
