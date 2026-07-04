# Jobs & output

## Two data layers

| Layer | Location | Role |
|-------|----------|------|
| **Registry** | `data\output\jobs\queue.db` | Job list, states, timestamps |
| **Files** | `data\output\jobs\{id}\` | Audio copy, transcript, SRT, summary |

Base path: `%APPDATA%\qwibo-desktop\data\`

The UI reads the list from SQLite and content from files. On startup the app **syncs** DB and disk.

---

## Job states

| State | Meaning |
|-------|---------|
| `queued` | Waiting in line |
| `running` | Processing now |
| `completed` | Finished OK |
| `failed` | Error (see job detail / `job.json`) |
| `cancelled` | User cancelled while queued |

---

## IDs and folders

Format: `YYYYMMDD_HHMMSS_file-name`

Example: `20260704_183045_interview-podcast`

If two uploads share the same second: suffix `_2`, `_3`, …

### Folder contents

```text
20260704_183045_interview-podcast/
├── source.mp3
├── job.json
├── trascrizione.txt
├── sottotitoli.srt
└── riassunto.txt        ← optional
```

---

## FIFO queue

1. Upload → job `queued`
2. Worker claims next job → `running`
3. Transcription + export + optional summary
4. → `completed` or `failed`

**One job at a time** per worker instance.

---

## Duplicates

| Situation | Behavior |
|-----------|----------|
| Same filename **queued/running** | Skipped by default |
| Same filename **already completed** | **New** job, new folder |
| Re-upload with "Enqueue anyway" | Forces duplicate in queue |

**No overwrite** of past jobs.

---

## Actions (UI)

| Action | When | Effect |
|--------|------|--------|
| **Cancel** | `queued` | → `cancelled` |
| **Retry** | `failed` / `cancelled` | Same job requeued |
| **Reprocess** | `completed` | New run, transcript only |
| **+ Summary** | `completed` | Reprocess with summary |
| **Delete** | Not `running` | Removes DB row + folder |
| **Sync disk** | Anytime | Reconcile DB ↔ filesystem |

---

## After restart

- `queue.db` persists — history remains
- Worker resumes `queued` jobs
- Stale `running` jobs recovered on startup

---

## Manual cleanup

Prefer **Delete** in the UI. To wipe everything:

1. Quit Qwibo from tray.
2. Delete `%APPDATA%\qwibo-desktop\data\output\jobs\`.

Models in `models\` are **not** affected.
