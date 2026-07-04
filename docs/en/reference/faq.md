# FAQ

## General

### Does Qwibo send my audio over the internet?

**No** for transcription. After the one-time model download, ASR runs locally. Cloud **summaries** send text (not audio) to your chosen provider if you enable them.

### Which languages are supported?

Parakeet TDT 0.6B v3 is optimized for **Italian**. Other languages work with varying quality.

### Do I need Python or Docker?

**No.** The desktop installer is self-contained. Docker is a separate product ([qwibo-docker](https://github.com/qwibo/qwibo-docker)).

### Mac or Linux desktop?

Not in alpha. Windows first; Mac DMG is planned.

---

## Models

### How much disk space?

| Component | Size |
|-----------|------|
| Parakeet ASR | ~2.5 GB |
| Local Qwen | ~2 GB |
| App + jobs | varies |

Plan **8–12 GB** free for a comfortable install.

### Re-download after update?

Usually **no** — models stay in `%APPDATA%\qwibo-desktop\models\`. Release notes will say if a new model version is required.

---

## Queue and jobs

### Why one file at a time?

The worker runs **FIFO** to limit RAM (NeMo + optional Qwen are heavy).

### Same file twice?

If the first job is **completed**, a new upload creates a **new folder** with a new timestamp.

### Close the window during a job?

The worker continues until you **Quit** from the system tray.

---

## Interface

### Browser vs desktop?

Qwibo uses a local web UI inside Electron. You don't manage ports or bookmarks — the app handles it.

### Worker starts automatically?

Yes. Each app launch starts the backend and worker subprocess.

---

## Summarization

### Cloud vs local?

| Mode | Privacy | Requirements |
|------|---------|--------------|
| Cloud API | Text sent to provider | API key + internet |
| Local Qwen | Fully offline | ≥ 16 GB RAM + ~2 GB model |

### Transcript OK but summary failed?

Normal if API key missing or provider error. Text is in `trascrizione.txt`.

---

## Performance

### How fast on CPU?

Rough guide: **~2× realtime** on a typical laptop i5 (1 min audio ≈ 2 min). Mini PCs may be slower.

### First job slower?

Parakeet loads into RAM on first transcription (+1–2 min).

---

## Documentation

### How do I publish these docs?

From the **qwibo** repo root:

```cmd
python scripts\publish_docs.py
```

or `scripts\publish_docs.bat` — builds MkDocs and copies HTML to `../qwibo.github.io/docs/`, then commits there if git is initialized. **No GitHub Actions.** Push `qwibo.github.io` to publish.

---

## Licensing

Personal use is free. Business use needs a [commercial license](commercial-license.md).
