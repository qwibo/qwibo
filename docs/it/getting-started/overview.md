# Panoramica

Qwibo trasforma audio e video in testo che puoi cercare, modificare e riusare — sul tuo PC Windows.

## Come funziona

```text
Installer (Electron)
    └── Backend Python embedded (FastAPI + worker)
            ├── Parakeet ASR  → trascrizione.txt + sottotitoli.srt
            └── LLM opzionale → riassunto.txt
```

Interagisci con una **finestra desktop** (non un tab del browser da gestire). L'app avvia il backend e lo tiene in esecuzione nella tray finché Qwibo è aperto.

## Principi

1. **Trascrizione locale** — dopo il download iniziale, l'audio non va in cloud per l'ASR.
2. **Modelli offline** — Parakeet e Qwen GGUF opzionale nel profilo utente.
3. **Nessun overwrite** — ogni job ha la sua cartella con timestamp.
4. **Un job alla volta** — coda sequenziale per limitare la RAM.

## Dove sono i dati

```text
%APPDATA%\qwibo-desktop\
├── data\           ← job, input, output, secrets
├── models\         ← Parakeet .nemo + Qwen opzionale
├── logs\           ← log diagnostici (tray → Apri cartella log)
└── cache\          ← cache interne
```

!!! tip "Log"
    Tray Qwibo → **Apri cartella log** se qualcosa fallisce in setup o trascrizione.

## Stato alpha

Canale attuale: **0.1.0-alpha** — installer Windows non firmato (avviso SmartScreen). Mac e firma codice in roadmap.

## Prossimi passi

- [Download e installazione](download.md)
- [Requisiti di sistema](system-requirements.md)
- [Primo avvio](first-run.md)
- [Modelli](models.md)
