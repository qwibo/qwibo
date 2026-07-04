# First run

The first time you open Qwibo after installation, a **setup wizard** downloads the speech models. This happens **once** — not during your first transcription.

## Setup wizard

1. Qwibo starts and checks `%APPDATA%\qwibo-desktop\models\`.
2. If Parakeet is missing, the wizard downloads it (~2.5 GB).
3. If your PC has **≥ 16 GB RAM**, Qwen for local summary is downloaded automatically (~2 GB).
4. When finished, the main app window opens.

!!! tip "Be patient"
    Download time depends on your connection. The window may look idle — check tray logs if unsure (**Open log folder**).

## Main window

After setup:

1. **Home** — upload area, sidebar with recent jobs, active queue.
2. **Queue & history** — full list of all jobs.
3. **Summary settings** — API keys and local engine status.
4. **License** — terms and documentation links.

## First transcription (recommended test)

1. Pick a **10–20 minute** file you know well (not a stress test on hour-long audio yet).
2. Optional: enable **Generate summary** and pick an engine.
3. Click **Queue transcription**.
4. You are redirected to the **job detail** page with live progress.
5. When complete: read `trascrizione.txt`, download SRT, open the output folder.

## Tray icon

Qwibo stays in the system tray when the window is closed (backend keeps running until you exit from the tray).

| Tray action | Effect |
|-------------|--------|
| Open Qwibo | Restore main window |
| Open log folder | Diagnostic logs for support |
| Quit | Stop backend and exit |

## Where files go

Job output lives under:

```text
%APPDATA%\qwibo-desktop\data\output\jobs\YYYYMMDD_HHMMSS_filename\
```

See [Jobs & output](../user-guide/jobs-and-output.md).

## If setup fails

| Symptom | What to try |
|---------|-------------|
| Download interrupted | Restart Qwibo — setup resumes |
| "Startup too slow" | Antivirus blocking backend; check logs |
| Out of disk space | Free at least 8 GB on system drive |

More: [Common issues](../troubleshooting/common-issues.md).
