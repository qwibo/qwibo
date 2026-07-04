# Common issues

## Setup and startup

### Model download fails or stalls

**Cause:** Network drop, antivirus, or insufficient disk space.

**Try:**

1. Tray → **Open log folder** — check `backend` log lines.
2. Ensure **≥ 8 GB** free on the system drive.
3. Restart Qwibo — setup retries missing models.
4. Temporarily allow Qwibo through antivirus.

---

### "Startup too slow" / app won't open

**Cause:** Backend did not respond within ~3 minutes (first load or blocked process).

**Try:**

1. Quit from tray, wait 10 s, relaunch.
2. Check no zombie `python.exe` from a previous crash (Task Manager).
3. Read logs in `%APPDATA%\qwibo-desktop\logs\`.
4. Reinstall if `runtime-venv` is corrupted.

---

### Qwibo opens but page is blank

**Cause:** Backend crash after window opened.

**Try:** Open log folder, restart app. If repeated, reinstall.

---

## Transcription

### Job stays `running` forever

**Cause:** Worker crash or very long file on slow CPU.

**Try:**

1. Wait — first job includes model load (1–2 min extra).
2. Check job detail for progress percentage.
3. Restart Qwibo — orphaned jobs are recovered.
4. Inspect logs for NeMo / ffmpeg errors.

---

### Job `failed` immediately

**Cause:** Corrupt file, unsupported codec, or missing ASR model.

**Try:**

1. Open job detail — read error message.
2. Confirm Parakeet exists in `models\` (> 2.2 GB `.nemo` file).
3. Test with a short `.wav` or `.mp3`.

---

### Poor Italian quality

**Cause:** Background noise, overlap, distant mic, strong accent.

**Try:** Shorter test clip in a quiet room. Parakeet is tuned for Italian but not magic.

---

## Summarization

### Summary not generated, transcript OK

**Cause:** Missing API key, local Qwen unavailable, or provider error.

**Try:**

1. **Summary settings** — verify key or local engine status.
2. For cloud: check internet and API quota.
3. For local: RAM must be ≥ 16 GB; Qwen GGUF must exist in `models\`.

Transcript is always in `trascrizione.txt`.

---

### Local summary greyed out

**Cause:** RAM below 16 GB or Qwen not downloaded.

**Use** a cloud provider or transcription-only mode.

---

## Queue and files

### Same file won't enqueue

**Cause:** An active job with the same filename is `queued` or `running`.

**Try:** Wait for completion, or use **Enqueue anyway** if shown.

---

### UI shows job but files missing

**Cause:** Manual folder deletion outside the app.

**Try:** **Delete** the stale job in UI, or **Sync disk** on `/jobs`.

---

## Performance

### Very slow on mini PC

Expected on CPU-only hardware (~2× realtime or worse). Queue long files overnight.

---

## Still stuck?

1. Tray → **Open log folder**
2. Note Qwibo version (window title)
3. Open an issue on [GitHub](https://github.com/qwibo/qwibo/issues) with log excerpt (redact API keys)

SmartScreen during install: [SmartScreen](smartscreen.md).
