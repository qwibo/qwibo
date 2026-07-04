# Interfaccia

La finestra Qwibo incorpora l'interfaccia **FastAPI + HTMX** su `127.0.0.1` e una porta locale libera (da ~**8765**). Non devi digitare URL — Electron la apre per te.

## Avvio e chiusura

| Azione | Come |
|--------|------|
| Avvia | Menu Start o collegamento desktop |
| Minimizza | Chiudi finestra → resta in **tray** |
| Esci | Tray → **Esci** (ferma worker) |

Una sola istanza: riaprire Qwibo mette a fuoco la finestra esistente.

---

## Navigazione

| Schermata | Percorso | Descrizione |
|-----------|----------|-------------|
| Home | `/` | Upload, coda, job recenti |
| Coda e storico | `/jobs` | Tabella completa |
| Dettaglio job | `/jobs/{id}` | Trascrizione, riassunto, download |
| Impostazioni riassunto | `/settings/summary` | API key, motori |
| Licenza | `/settings/license` | Termini, link docs |

---

## Home

- Upload file
- Sidebar: **Genera riassunto**, motore, lunghezza
- Coda attiva (aggiornamento ~2 s)
- Ultimi **8** job nella sidebar

Dopo l'accodamento → redirect a **`/jobs/{id}`**.

---

## Dettaglio job

- **In corso**: barra progresso con refresh automatico
- **Completato**: trascrizione, riassunto, download TXT/SRT
- **Apri cartella** → Explorer
- Azioni: annulla, riprova, rielabora, elimina

---

## Impostazioni riassunto

- Chiavi API cloud
- Stato motori disponibili
- Controllo RAM per Qwen locale

---

## Worker in background

Processo Python separato per la trascrizione (NeMo non gira nel processo web).

Dopo un crash, i job `running` orfani vengono recuperati al riavvio.

---

## Suggerimenti

- Primo job a freddo: **1–2 min** extra per caricare Parakeet
- Stesso file due volte → **due cartelle** con timestamp diversi
- Log: tray → **Apri cartella log**

Vedi [Coda e output](jobs-and-output.md).
