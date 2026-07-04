# Riassunto testuale

Dopo la trascrizione, Qwibo può generare un **riassunto LLM** da `trascrizione.txt`.

## Provider

| ID | Motore | Setup |
|----|--------|-------|
| `deepseek` | API DeepSeek | Chiave in impostazioni |
| `openai` | OpenAI | Chiave |
| `gemini` | Google Gemini | Chiave |
| `claude` | Anthropic | Chiave |
| `kimi` | Moonshot | Chiave |
| `local` | Qwen GGUF | Setup + RAM ≥ 16 GB |

Chiavi in `%APPDATA%\qwibo-desktop\data\.secrets\summary_keys.json`.

---

## Lunghezza

`auto`, `short`, `normal`, `detailed`.

---

## Pipeline

1. Trascrizione NeMo
2. Scarico ASR dalla RAM
3. Riassunto (map-reduce se testo lungo)
4. Salva `riassunto.txt`

Se fallisce: job **`completed`**, trascrizione e SRT validi.

---

## Privacy

| Passo | Esce dal PC? |
|-------|--------------|
| Trascrizione | **No** |
| Riassunto cloud | **Sì** — solo testo |
| Qwen locale | **No** |

Per dati sensibili: `local` o disabilita riassunto.
