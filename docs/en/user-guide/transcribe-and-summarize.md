# Transcribe & summarize

Short workflow for your first real file.

## 1. Open Qwibo

Ensure first-run model setup is complete ([First run](../getting-started/first-run.md)).

## 2. Optional — summary settings

If you want a summary:

1. Go to **Summary settings** (`/settings/summary`).
2. Paste an API key (e.g. DeepSeek), **or** confirm local Qwen is available.
3. Return to **Home**.

## 3. Configure sidebar

On the home page sidebar:

- **Generate summary** — on/off
- **Engine** — `deepseek`, `openai`, `local`, …
- **Length** — `auto`, `short`, `normal`, `detailed`

## 4. Upload and queue

1. Choose your audio or video file.
2. Click **Queue transcription**.
3. Wait on the job detail page — progress updates automatically.

## 5. Use the results

| Output | Use |
|--------|-----|
| Transcript | Copy from UI or download TXT |
| Subtitles | Download SRT for editors / YouTube |
| Summary | Download or read in UI |

**Open folder** shows files on disk:

```text
trascrizione.txt
sottotitoli.srt
riassunto.txt      ← if summary succeeded
source.*           ← copy of upload
job.json           ← metadata
```

## 6. Queue another file

Return to **Home** or stay on `/jobs` — the worker processes **one file at a time** in FIFO order.

---

## Common first-time mistakes

| Mistake | Fix |
|---------|-----|
| Closing the window during a job | OK — worker continues until you **Quit** from tray |
| Expecting instant results on long files | Normal on CPU — check progress on job page |
| Summary failed but transcript OK | Read `summary_error` on job page; transcript is still valid |

Details: [Summarization](summarization.md) · [File formats](file-formats.md)
