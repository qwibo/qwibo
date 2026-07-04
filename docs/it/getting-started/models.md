# Modelli

Qwibo usa **un modello obbligatorio** per la trascrizione e modelli **opzionali** per il riassunto. L'utente li scarica con il **wizard** — niente script manuali.

## Modello ASR (obbligatorio)

| Proprietà | Valore |
|-----------|--------|
| Hugging Face | `nvidia/parakeet-tdt-0.6b-v3` |
| File locale | `%APPDATA%\qwibo-desktop\models\parakeet-tdt-0.6b-v3.nemo` |
| Dimensione | ~2,5 GB |
| Motore | NVIDIA NeMo |

Ottimizzato per **italiano**; altre lingue con qualità variabile.

---

## Riassunto cloud (opzionale)

Nessun modello su disco. Serve **API key** del provider.

| Provider | Configurazione |
|----------|----------------|
| DeepSeek, OpenAI, Gemini, Claude, Kimi | Impostazioni riassunto |

Chiavi in `%APPDATA%\qwibo-desktop\data\.secrets\summary_keys.json`.

---

## Riassunto locale — Qwen (opzionale)

| Proprietà | Valore |
|-----------|--------|
| Modello | Qwen2.5-3B-Instruct (GGUF Q4) |
| Percorso | `models\qwen2.5-3b-instruct\*.gguf` |
| Dimensione | ~2 GB |
| RAM | ≥ 16 GB |
| Motore | llama.cpp (CPU) |

Scaricato automaticamente al setup se la RAM lo consente.

---

## Tabella riepilogo

| Componente | Posizione | Download | Rete in uso |
|------------|-----------|----------|-------------|
| Parakeet | `models\*.nemo` | Wizard | No |
| Cloud | — | Solo API key | Sì |
| Qwen locale | `models\qwen2.5-3b-instruct\` | Wizard | No |

---

## Reinstallazione pulita

1. Esci dalla tray.
2. Elimina `%APPDATA%\qwibo-desktop\models\`.
3. Riavvia Qwibo — il wizard riparte.

---

## Licenze modelli

- **Parakeet**: termini NVIDIA / NeMo
- **Qwen**: licenza Alibaba — vedi Hugging Face
- **App Qwibo**: proprietaria — [Licenze](../reference/licenses.md)

Gli sviluppatori usano `scripts/download_model.py` nel repo; non fa parte del flusso retail.
