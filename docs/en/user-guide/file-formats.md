# File formats

## Supported input

### Audio

`.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`, `.opus`, `.aac`, `.wma`

### Video

`.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.m4v`, `.flv`, `.wmv`

Audio is extracted with bundled **ffmpeg** at 16 kHz mono PCM (NeMo requirement).

---

## Output per job

| File | Format | Content |
|------|--------|---------|
| `trascrizione.txt` | UTF-8 plain text | Full transcript |
| `sottotitoli.srt` | SubRip | Timestamped segments |
| `riassunto.txt` | UTF-8 plain text | Summary (if generated) |
| `source.*` | Original | Copy of upload |
| `job.json` | JSON | Job metadata |

---

## SRT example

```srt
1
00:00:00,000 --> 00:00:05,120
First transcribed sentence.

2
00:00:05,120 --> 00:00:10,450
Second sentence.
```

---

## Long files

| Threshold | Behavior |
|-----------|----------|
| ≤ 30 minutes | Single pass |
| > 30 minutes | 30 s chunks, 2 s overlap, merged |

Long files take proportionally longer on CPU.

---

## Encoding

All text output is **UTF-8**.
