# Qwibo

**Qwibo** è un'app desktop per Windows che trascrive audio e video in testo **offline**, con il modello [NVIDIA NeMo Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3). I riassunti LLM opzionali possono essere locali (Qwen) o via API cloud.

!!! info "Documentazione bilingue"
    Questa documentazione è disponibile anche in **inglese**. Usa il selettore lingua in alto.

## Cosa fa

| Funzione | Descrizione |
|----------|-------------|
| **Trascrizione** | Audio/video → testo + sottotitoli SRT |
| **Coda job** | Più file elaborati uno alla volta; storico e dettaglio in app |
| **Riassunto** | LLM multi-provider (DeepSeek, OpenAI, Qwen locale, …) |
| **App desktop** | Installer Electron — niente Python, terminale o Docker |
| **Privacy** | L'audio resta sul PC durante la trascrizione |

## A chi serve

Qwibo è per chi ha già registrazioni — riunioni, podcast, interviste, lezioni — e vuole testo utilizzabile **senza** caricare file su cloud né pagare al minuto.

Per **Docker self-hosted** su mini PC o NAS, vedi il repo [qwibo-docker](https://github.com/qwibo/qwibo-docker).

## Avvio rapido

1. Scarica `Qwibo-Setup-*.exe` dalle [GitHub Releases](https://github.com/qwibo/qwibo/releases).
2. Esegui l'installer (vedi [SmartScreen](troubleshooting/smartscreen.md) se Windows blocca).
3. Completa il **setup iniziale** (~4–5 GB di modelli, una sola volta).
4. Carica un file e clicca **Accoda trascrizione**.

Dettagli: [Download](getting-started/download.md) · [Primo avvio](getting-started/first-run.md)

## Hardware in sintesi

| Risorsa | Minimo | Consigliato |
|---------|--------|-------------|
| Windows | 10/11 64-bit | 11 |
| RAM (solo ASR) | 8 GB | 16 GB |
| RAM (Qwen locale) | 16 GB | 32 GB |
| Disco libero | 8 GB | 12 GB |
| GPU | Non richiesta | NVIDIA (futuro) |

Dettagli: [Requisiti di sistema](getting-started/system-requirements.md)

## Mappa documentazione

| Sezione | Contenuto |
|---------|-----------|
| [Per iniziare](getting-started/overview.md) | Installazione, primo avvio, modelli |
| [Guida utente](user-guide/app-interface.md) | Interfaccia, coda, riassunti |
| [Risoluzione problemi](troubleshooting/common-issues.md) | Errori comuni |
| [Riferimento](reference/faq.md) | FAQ, licenze |

## Anteprima e pubblicazione docs

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

Anteprima su http://127.0.0.1:8000 — pubblicazione: `scripts\publish_docs.bat` (o `python scripts/publish_docs.py`), poi `git push` nel repo gemello `qwibo.github.io`. **Nessuna GitHub Action.**

## Licenza

**Software proprietario** — Copyright © 2024-2026 [Antonio Trento](https://antoniotrento.net). Uso personale gratuito; uso commerciale con [licenza a pagamento](reference/commercial-license.md). Vedi [Licenze](reference/licenses.md).
