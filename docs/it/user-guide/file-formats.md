# Formati file

## Input supportati

**Audio:** `.wav`, `.mp3`, `.flac`, `.m4a`, `.ogg`, `.opus`, `.aac`, `.wma`

**Video:** `.mp4`, `.mkv`, `.avi`, `.mov`, `.webm`, `.m4v`, `.flv`, `.wmv`

Estrazione audio con **ffmpeg** incluso (16 kHz mono PCM).

---

## Output per job

| File | Contenuto |
|------|-----------|
| `trascrizione.txt` | Testo completo UTF-8 |
| `sottotitoli.srt` | SubRip con timestamp |
| `riassunto.txt` | Riassunto (se generato) |
| `source.*` | Copia upload |
| `job.json` | Metadati |

---

## File lunghi

| Soglia | Comportamento |
|--------|---------------|
| ≤ 30 min | Passaggio unico |
| > 30 min | Chunk 30 s, overlap 2 s |

Su CPU i tempi crescono proporzionalmente.

---

## Codifica

Tutto in **UTF-8**.
