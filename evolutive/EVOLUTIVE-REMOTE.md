# Evolutive remote — Sbobinator

Idee **utili ma non fondamentali** per il prodotto attuale. Non sono nel backlog operativo (`microevolutive/active/PLAN_BACKLOG.md`); si rivalutano solo se cambiano vincoli (tempo, hardware, richiesta utenti) o se un spike dimostra costo basso.

**Criterio:** non blocca adozione, monetizzazione o affidabilità del flusso core (trascrivere italiano in locale, coda, export).

---

## ER-01 — Diarizzazione speaker ("chi parla")

**Stato:** 🌙 remota · **Non in sprint**  
**Dettaglio tecnico:** [ANALISI-DIARIZZAZIONE-SPEAKER.md](./old/ANALISI-DIARIZZAZIONE-SPEAKER.md)

### Cosa sarebbe

Attribuire il testo a `Speaker 1`, `Speaker 2`, … nelle riunioni e interviste multi-voce. Opt-in per job, non su monologhi o podcast solista.

### Perché non è fondamentale adesso

Il nucleo Sbobinator risolve **audio → testo italiano in locale**. Senza diarizzazione il prodotto resta completo per il caso base. La feature serve soprattutto a riunioni/interviste — segmento importante ma **secondario** rispetto a coda, batch, licenza, UX installazione.

### Difficoltà (sintesi)

| Aspetto | Valutazione |
|---------|-------------|
| Architettura | **Non inferno** — si innesta su worker e pipeline esistenti |
| Implementazione | **Non facile** — secondo modello, merge diarizzazione↔ASR, settimane non giorni |
| Qualità | **Variabile** — Teams/Zoom compressi e voci sovrapposte spesso deludono |
| Risorse | RAM e tempo **×2–3** su file lunghi |

**Verdetto:** medio-difficile. Non da promettere agli utenti senza benchmark su audio reale. Se lo scope fosse "perfetto su ogni call con i nomi" → **inferno, da scartare**. Se restasse opt-in con Speaker 1/2 su audio pulito → eventualmente rivalutabile in futuro.

### Quando ripescarla

- Richiesta ricorrente da utenti paganti o adottanti
- Modelli più leggeri o integrazione NeMo più lineare
- Mezza giornata di spike su **un** file reale con esito chiaramente positivo

### Quando lasciarla morta

- Output spike "mah" su registrazione Teams tipica
- Costo UX/RAM non accettabile per il target hardware (16 GB)
- Complessità pipeline che destabilizza il worker

---

## Altre candidate remote (placeholder)

| ID | Idea | Note |
|----|------|------|
| ER-02 | Identificazione speaker per nome (voice ID) | Fuori scope; privacy e complessità |
| ER-03 | SaaS multi-tenant | Già non-obiettivo in roadmap |

---

## Cronologia

| Data | Modifica |
|------|----------|
| 2026-07-01 | Creazione sezione; ER-01 diarizzazione spostata da backlog prioritario |
