# Text summarization

After transcription, Qwibo can generate an **LLM summary** from `trascrizione.txt`.

## Providers

| ID | Engine | Setup |
|----|--------|-------|
| `deepseek` | DeepSeek API | API key in Summary settings |
| `openai` | OpenAI | API key |
| `gemini` | Google Gemini | API key |
| `claude` | Anthropic Claude | API key |
| `kimi` | Moonshot Kimi | API key |
| `local` | Qwen2.5 GGUF (CPU) | First-run download + RAM ≥ 16 GB |

Configure keys in the app: **Summary settings** (`/settings/summary`).

Keys saved to: `%APPDATA%\qwibo-desktop\data\.secrets\summary_keys.json`

---

## Length

| Value | Behavior |
|-------|----------|
| `auto` | Proportional to text length |
| `short` | Brief |
| `normal` | Balanced |
| `detailed` | Longer |

---

## Pipeline

1. NeMo transcription completes
2. ASR model unloaded from RAM
3. `summarize()` — chosen provider; map-reduce for long texts
4. Saves `riassunto.txt`

If summary fails: job stays **`completed`**, transcript and SRT remain valid; error shown on job page.

---

## Long texts

Beyond provider context → **map-reduce** (chunk summaries merged).

Local Qwen on CPU can take **several minutes** for hour-long transcripts.

---

## UI workflow

1. **Summary settings** — add API key (first time for cloud)
2. Home sidebar → **Generate summary** on
3. Pick engine + length
4. Queue file

---

## Privacy note

| Step | Data leaves PC? |
|------|-------------------|
| Transcription | **No** |
| Cloud summary | **Yes** — text only, to your provider |
| Local Qwen | **No** |

Choose `local` or skip summary if transcripts are highly sensitive.
