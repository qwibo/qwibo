# Models

Qwibo uses **one required model** for transcription and **optional models** for LLM summary. End users download these via the **first-run wizard** — no manual scripts.

## ASR model (required)

| Property | Value |
|----------|-------|
| Hugging Face | `nvidia/parakeet-tdt-0.6b-v3` |
| Local file | `%APPDATA%\qwibo-desktop\models\parakeet-tdt-0.6b-v3.nemo` |
| Size | ~2.5 GB |
| Engine | NVIDIA NeMo |

Optimized for **Italian**; other languages work with varying quality.

---

## Cloud LLM summary (optional)

No model on disk. Requires an **API key** for the chosen provider.

| Provider | Configure in app |
|----------|------------------|
| DeepSeek | Summary settings |
| OpenAI | Summary settings |
| Gemini | Summary settings |
| Claude | Summary settings |
| Kimi | Summary settings |

Keys are stored in `%APPDATA%\qwibo-desktop\data\.secrets\summary_keys.json`.

---

## Local LLM summary — Qwen (optional)

| Property | Value |
|----------|-------|
| Model | Qwen2.5-3B-Instruct (GGUF Q4) |
| Path | `models\qwen2.5-3b-instruct\*.gguf` |
| Size | ~2 GB |
| RAM | ≥ 16 GB system RAM |
| Engine | llama.cpp (CPU) |

Downloaded automatically during first-run setup when RAM threshold is met.

---

## Summary table

| Component | Location | Download | Network at runtime |
|-----------|----------|----------|-------------------|
| Parakeet ASR | `models\*.nemo` | Setup wizard | No |
| Cloud summary | — | API key only | Yes |
| Local Qwen | `models\qwen2.5-3b-instruct\` | Setup wizard (if RAM OK) | No |

---

## Reinstall / clean slate

Uninstalling Qwibo does not delete models. To force re-download:

1. Quit Qwibo from the tray.
2. Delete `%APPDATA%\qwibo-desktop\models\`.
3. Restart Qwibo — setup runs again.

---

## Licenses

- **Parakeet**: NVIDIA / NeMo terms
- **Qwen**: Alibaba model license — see Hugging Face
- **Qwibo app**: proprietary — see [Licenses](../reference/licenses.md)

Developers maintaining a dev build use `scripts/download_model.py` in the repo; that is not part of the retail installer flow.
