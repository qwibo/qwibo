# Analisi evolutiva — Diarizzazione speaker ("chi parla")

> **Priorità:** 🌙 **Evolutiva remota** — non nel backlog operativo  
> **Data:** 1 luglio 2026 · **Stato:** archiviata per rivalutazione futura  
> **Indice:** [EVOLUTIVE-REMOTE.md](./EVOLUTIVE-REMOTE.md) · pilastro **P5 Qualità testo**

---

## 1. Sintesi

Durante lo sbobinamento, **distinguere una persona dall'altra** (diarizzazione) renderebbe utilizzabile il testo in scenari dove oggi l'output è un **muro di parole senza attribuzione**.

È un'evolutiva **strategicamente importante** per riunioni, interviste e panel, ma **non va generalizzata a tutte le registrazioni**. Prima di implementare serve capire se esiste un percorso **abbastanza semplice** rispetto al beneficio; se la complessità (RAM, tempi, qualità, UX) è troppo alta, **si rimanda** piuttosto che complicare il prodotto core.

**Decisione attuale:** classificata come **evolutiva remota** — non fondamentale per il prodotto attuale; dettaglio motivazioni in [EVOLUTIVE-REMOTE.md](./EVOLUTIVE-REMOTE.md).

---

## 2. Perché è importante

### Problema utente

Con più interlocutori, la trascrizione lineare diventa difficile da:

- riassumere per partecipante ("cosa ha detto il cliente?")
- citare con attribuzione (giornalismo, tesi, verbali)
- trasformare in action item per ruolo
- revisionare senza riascoltare l'audio

### Valore per l'adozione

| Senza diarizzazione | Con diarizzazione (se funziona) |
|---------------------|----------------------------------|
| TXT utile ma piatto | TXT strutturato per speaker |
| SRT con timing ma senza "chi" | SRT/VTT con label o colori per speaker |
| Riassunto generico | Riassunto per interlocutore (futuro) |

Per **Marco** (riunioni clienti), **Luca** (interviste) e **CU-02** (call aziendali) è probabilmente la feature che più aumenta il **passaggio da "demo" a strumento di lavoro** — più di export DOCX o tag.

### Perché va analizzata ora (e non ignorata)

1. Influenza scelte architetturali (pipeline, RAM, modelli multipli, formato output).
2. Esiste già nel backlog ma era classificata "solo su richiesta" — il feedback prodotto la sposta in **alta priorità analitica**.
3. Implementarla male (lenta, inaccurata, sempre attiva) danneggerebbe l'esperienza più che non averla.

---

## 3. Dove ha senso (e dove no)

### ✅ Registrazioni candidate

| Tipo | Perché |
|------|--------|
| Riunioni 2–6 persone | Turni di parola, bisogno di attribuzione |
| Interviste faccia a faccia | Domande/risposte, citazioni |
| Panel / podcast multi-ospite | Segmenti per ospite |
| Call registrate (Teams/Zoom) | Spesso 2+ voci distinte |

**Requisiti audio favorevoli:** microfoni separati o stanza silenziosa, overlap limitato, almeno 2–3 secondi per turno.

### ❌ Registrazioni da escludere (default off)

| Tipo | Perché |
|------|--------|
| Monologo (podcast solista, lezione un docente) | Zero beneficio, solo costo |
| Voce fuori campo / rumore forte | Diarizzazione inaffidabile |
| Telefono compresso, voci sovrapposte | Errori frequenti su speaker |
| Video con musica di sottofondo | Confonde il modello |

**Principio prodotto:** diarizzazione **opt-in per job**, con suggerimento UI ("Sembra una riunione con più persone — attivare speaker?") non obbligatoria globale.

---

## 4. Cosa significa "semplice" (criterio go/no-go)

### Go — si può procedere a sprint se

- [ ] Attivazione **per singolo job** (checkbox o preset "Riunione")
- [ ] **Un solo modello** aggiuntivo scaricabile come Parakeet (script dedicato)
- [ ] Incremento tempo elaborazione **≤ 2×** su campione rappresentativo (riunione 30 min, 2–4 speaker)
- [ ] RAM picco **≤ 24 GB** su profilo "uso confortevole" (16 GB = warning esplicito)
- [ ] Output leggibile: `Speaker 1:` / `Speaker 2:` o nomi editabili post-hoc
- [ ] Nessun obbligo di account cloud o API esterna per la diarizzazione locale

### No-go — si rimanda se

- Richiede **tre+ modelli** in RAM contemporaneamente senza unload ordinato
- Qualità su audio tipico Teams **< soglia accettabile** (da definire in benchmark: % turni attribuiti correttamente)
- Pipeline diventa **fragile** (ordine ASR → diarizzazione → merge non documentato)
- UX obbliga l'utente a configurare parametri tecnici (soglie, cluster, ecc.)

**Regola:** se non è spiegabile in una riga nella UI ("Attribuisci il testo a chi parla — per riunioni e interviste"), è troppo complesso per v1 di questa feature.

---

## 5. Opzioni tecniche (panorama)

Stack attuale: **NeMo Parakeet** per ASR. La diarizzazione è un passo **aggiuntivo**, non incluso nel modello ASR.

| Approccio | Pro | Contro |
|-----------|-----|--------|
| **NeMo diarization** (stesso ecosistema) | Coerenza dipendenze, già NVIDIA nel progetto | Secondo modello pesante; integrazione da studiare |
| **pyannote.audio** | Standard de facto, modelli pretrained | Licenza HF per alcuni pesi; altro stack PyTorch |
| **WhisperX** (Whisper + diarization) | Pipeline nota | Cambierebbe motore ASR — **fuori scope** |
| **Euristiche su silenzi + clustering leggero** | Basso costo | Qualità scarsa su overlap — solo fallback |

**Raccomandazione analisi:** confrontare **NeMo diarization** vs **pyannote** su **3 campioni fissi** (vedi §7), misurando tempo, RAM e leggibilità output — senza commit su stack finché non c'è benchmark.

### Pipeline logica (bozza)

```
audio → [opzionale] diarizzazione → segmenti (t0, t1, speaker_id)
      → ASR per segmento o ASR globale + allineamento speaker
      → merge → trascrizione.txt con prefissi speaker
      → export SRT con cue per speaker (o traccia multiple)
```

**Punto critico da spike:** ASR prima o diarizzazione prima? NeMo e pyannote hanno pattern diversi; va validato su italiano.

---

## 6. Impatto su architettura attuale

| Area | Impatto |
|------|---------|
| Worker | Nuova fase pipeline: `diarize` tra `extract_audio` e `transcribe` (o dopo, da validare) |
| `job.json` | Campi: `diarization_enabled`, `speaker_count` (opz.), `speakers: [{id, label}]` |
| RAM | Unload ASR prima di caricare modello diarizzazione (o viceversa) — **sequenziale obbligatorio** |
| Export | TXT con prefissi; SRT con attributo speaker; opzionale VTT |
| UI | Toggle job; tabella rinomina "Speaker 1" → "Marco" |
| CLI | `--speakers` / `--no-speakers` |

Non richiede rifacimento coda o FastAPI; si innesta sul worker esistente **se** il merge segmenti è stabile.

---

## 7. Piano di analisi (spike)

### Campioni benchmark (da preparare)

| ID | Descrizione | Speaker | Durata | Note |
|----|-------------|---------|--------|------|
| D1 | Riunione 2 persone, microfono laptop | 2 | ~15 min | Caso minimo |
| D2 | Call Teams 3–4 persone | 3–4 | ~30 min | Caso Marco |
| D3 | Intervista giornalistica | 2 | ~20 min | Caso Luca |
| D4 | Monologo podcast | 1 | ~10 min | Controllo negativo (non deve "inventare" speaker) |

### Metriche

| Metrica | Come misurarla |
|---------|----------------|
| Tempo totale | vs stesso file senza diarizzazione |
| RAM picco | `psutil` / log worker |
| Speaker count | corretto vs ground truth manuale |
| Attribuzione turni | % segmenti con speaker plausibile (revisione umana) |
| Leggibilità export | tempo per trovare citazione di un speaker |

### Deliverable spike (1–2 giornate focalizzate)

1. Script `scripts/benchmark-diarization.py` (o notebook) riproducibile
2. Tabella risultati in `docs/` o `bug-fix/` con campioni D1–D4
3. Raccomandazione **GO / NO-GO / GO con limiti** (es. solo 2–4 speaker, solo WAV pulito)
4. Stima effort implementazione in UI (S / M / L / XL)

---

## 8. Rischi

| Rischio | Mitigazione |
|---------|-------------|
| OOM con ASR + diarizzazione | Un solo modello in RAM; fasi sequenziali |
| Qualità bassa su italiano telefonico | Opt-in; messaggio onesto in UI; benchmark prima |
| Aspettative utente ("riconosce i nomi") | Chiarire: **Speaker N**, rinomina manuale; no face/voice ID |
| Scope creep (identificazione biometrica) | **Fuori scope** — solo cluster anonimi per sessione |
| Licenze modelli pyannote | Verificare HF gating e uso commerciale prima di default |

---

## 9. Posizione in roadmap

| Documento | Prima | Dopo questa analisi |
|-----------|-------|---------------------|
| `ROADMAP-EVOLUTIVE.md` Fase 4.2 | Evolutiva remota |
| `PLAN_BACKLOG.md` F | Rimossa — vedi `EVOLUTIVE-REMOTE.md` |
| `CASI-D-USO.md` CU-07 | Caso d'uso documentato; priorità **remota** |

**Non compete** con il focus attuale (trascrizione affidabile, coda, adozione).

---

## 10. Prossimi passi

Nessuno — evolutiva **remota**. Ripescare solo su richiesta esplicita o spike positivo futuro (criteri in [EVOLUTIVE-REMOTE.md](./EVOLUTIVE-REMOTE.md)).

---

## Cronologia

| Data | Modifica |
|------|----------|
| 2026-07-01 | Spostata in EVOLUTIVE-REMOTE (non prioritaria) |
| 2026-07-01 | Creazione documento; analisi fattibilità |
