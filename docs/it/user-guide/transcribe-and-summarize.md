# Trascrivere e riassumere

Workflow rapido per il primo file reale.

## 1. Apri Qwibo

Setup modelli completato ([Primo avvio](../getting-started/first-run.md)).

## 2. Opzionale — impostazioni riassunto

1. **Impostazioni riassunto** (`/settings/summary`).
2. Incolla API key (es. DeepSeek) **oppure** verifica Qwen locale.
3. Torna alla **Home**.

## 3. Sidebar

- **Genera riassunto** — on/off
- **Motore** — `deepseek`, `openai`, `local`, …
- **Lunghezza** — `auto`, `short`, `normal`, `detailed`

## 4. Carica e accoda

1. Scegli audio o video.
2. **Accoda trascrizione**.
3. Attendi sulla pagina dettaglio job.

## 5. Risultati

| Output | Uso |
|--------|-----|
| Trascrizione | Copia da UI o TXT |
| Sottotitoli | SRT per editor / YouTube |
| Riassunto | Download o lettura in UI |

**Apri cartella**:

```text
trascrizione.txt
sottotitoli.srt
riassunto.txt
source.*
job.json
```

## 6. Accoda altro

Torna alla **Home** o usa `/jobs` — **un file alla volta** in ordine FIFO.

---

## Errori comuni

| Errore | Fix |
|--------|-----|
| Chiudi finestra durante job | OK — worker attivo finché non **Esci** da tray |
| File lungo lento | Normale su CPU |
| Riassunto fallito, trascrizione OK | Leggi errore in pagina job |

Dettagli: [Riassunto](summarization.md) · [Formati](file-formats.md)
