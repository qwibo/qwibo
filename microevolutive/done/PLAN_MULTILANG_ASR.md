# Piano microevolutivo — Trascrizione multilingua (NeMo)

> **Data**: 2026-07-02 · **Stato**: ✅ **implementato** (v1 codice)  
> **Obiettivo:** in base alla lingua scelta dall’utente, NeMo deve **scrivere il trascritto in quella lingua** — non tradurre, ma riconoscere correttamente l’audio parlato.  
> **Lingue core v1 (obbligatorie):** 🇮🇹 Italiano · 🇬🇧 Inglese · 🇫🇷 Francese · 🇪🇸 Spagnolo · 🇩🇪 Tedesco  
> **Correlato:** `PLAN_MULTILANG_SUMMARY.md` (lingua del riassunto — indipendente) · `PLAN_DESKTOP_ELECTRON.md` (retail Win+Mac)

---

## 0. Obiettivo prodotto

Qwibo oggi è percepito come “solo italiano”, ma il modello **Parakeet v3** supporta già **25 lingue europee** in un unico file `.nemo` (~2.5 GB).

**Cosa manca:** esporre la scelta lingua all’utente e passarla alla pipeline NeMo.

| Requisito | Dettaglio |
|-----------|-----------|
| Scelta esplicita | L’utente indica la lingua **parlata** nell’audio (per job o default in settings) |
| Output | Testo nella lingua scelta — es. audio inglese → transcript in inglese |
| Lingue core | **IT, EN, FR, ES, DE** — coprono la maggior parte dell’Europa e del mercato mondiale retail |
| Un solo modello | Nessun download aggiuntivo per le 5 lingue core |
| Non è traduzione | Il riassunto multilingua è in `PLAN_MULTILANG_SUMMARY.md` |

**Perché ora:** prodotto desktop mondiale (Electron Win+Mac) senza ASR multilingua resta “strumento italiano”.

---

## 1. Cosa esiste già

| Pezzo | Stato |
|-------|--------|
| Modello `nvidia/parakeet-tdt-0.6b-v3` | ✅ ~2.5 GB, **25 lingue EU** in un solo `.nemo` |
| `scripts/download_model.py` | ✅ Un solo download |
| `TranscribeConfig` in `config.py` | Solo `model_name`, device, chunking — **manca `language`** |
| `transcribe.py` | Nessun `language_id` passato a NeMo |
| `JobRecord.model_name` | ✅ Persistito; **manca `asr_language`** |
| UI / CLI / sito | Copy “italiano” ovunque — da generalizzare |

**Considerazione chiave:** il 90% del lavoro è **esporre la lingua** a NeMo e all’utente, non scaricare N modelli. Modelli aggiuntivi solo se i test su una lingua core falliscono (fase 3 opzionale).

---

## 2. Lingue supportate

### 2.1 Core v1 — le cinque obbligatorie

| Codice | Lingua | Mercato / motivo |
|--------|--------|------------------|
| `it` | Italiano | **Default** — mercato primario attuale |
| `en` | Inglese | Globale — podcast, business, accademia |
| `fr` | Francese | Francia, Belgio, Svizzera, Africa francofona |
| `es` | Spagnolo | Spagna, Americas ispaniche |
| `de` | Tedesco | Germania, Austria, Svizzera |

Queste cinque lingue coprono una **fetta molto ampia** dell’uso professionale in Europa e oltre. Sono il **Definition of Done** della fase 2.

### 2.2 Estensione v1.1 — altre lingue Parakeet v3

Il modello NVIDIA supporta altre lingue EU (es. `pt`, `nl`, `pl`, `ro`, …). In UI:

- **Select principale:** IT · EN · FR · ES · DE
- **“Altre lingue (EU)”** in settings avanzate o secondo menu — lista da documentazione NVIDIA

Non promettere lingue fuori dal set Parakeet v3 senza benchmark.

### 2.3 Fuori scope v1

| Lingua | Motivo |
|--------|--------|
| Cinese, Giapponese, Arabo, … | Richiedono **altro modello** ASR — fase 3+ |
| Traduzione IT→EN del trascritto | Out of scope — vedi summary multilingua |
| Auto-detect lingua obbligatorio | Utile in v2; v1 = scelta esplicita (meno errori) |


## 3. Architettura

```
Upload UI / CLI
      │
      ▼
 JobRecord.asr_language  ──►  pipeline.py
      │                            │
      ▼                            ▼
 TranscribeConfig.language   transcribe.py
      │                            │
      ▼                            ▼
 NeMo ASRModel.transcribe(..., language_id=?)   ← da verificare su API NeMo 2.x
```

### 3.1 Un modello

```
models/
  parakeet-tdt-0.6b-v3.nemo    ← unico file
```

`download_model.py` invariato per la fase 1.

### 3.2 Più modelli (solo se necessario — fase 3)

Registro opzionale in `config.py`:

```python
ASR_MODELS = {
    "parakeet-v3": "nvidia/parakeet-tdt-0.6b-v3",
    # "canary-1b": "nvidia/canary-1b-v2",  # esempio futuro
}
```

UI: "Modello ASR" avanzato + `scripts/download_model.py --model …`.

**Non implementare subito** — evita gestione disco e RAM doppia senza benchmark.

---

## 4. Modifiche codice

### 4.1 Config

```python
@dataclass(frozen=True)
class TranscribeConfig:
    model_name: str = DEFAULT_MODEL
    language: str = "it"   # BCP-47 semplificato: it, en, de, ...
    ...
```

### 4.2 `transcribe.py`

1. Accettare `language` in `transcribe_file()` / path chunk.
2. Passare hint a NeMo (da documentare dopo spike):
   - `model.transcribe(paths, language_id='it')` **oppure**
   - decoder config / `prompt` multilingue se richiesto dalla versione NeMo installata.
3. **Spike obbligatorio (0.5 giorni):** script `scripts/spike_nemo_language.py` con
   WAV campione IT + EN → confronto con/senza language_id.

### 4.3 `jobs.py`

- Colonna `asr_language TEXT DEFAULT 'it'`
- `register_job(..., asr_language=...)`
- Reprocess: opzione "Ritrascrivere con altra lingua" (nuovo job o stesso job fase transcribe)

### 4.4 UI

| Dove | Modifica |
|------|----------|
| `index.html` | Select "Lingua audio" (default da settings utente) |
| `jobs.html` | Colonna/filtro lingua |
| `job_detail_page.html` | Badge lingua ASR |
| Settings (nuova o in license/summary) | Lingua ASR predefinita |

### 4.5 CLI

```powershell
qwibo transcribe video.mp4 --language en
```

### 4.6 Docs + sito

- MkDocs: pagina "Lingue supportate ASR"
- Homepage: "Italian first, EU languages supported" (non solo IT)

---

## 5. Fasi

### Fase 0 — Spike NeMo language API — **prima di tutto**

| Output | Criterio |
|--------|----------|
| `scripts/spike_nemo_language.py` | Log WER qualitativo o diff testo IT vs EN su stesso modello |
| Nota in questo file § "Esito spike" | Go/no-go su language_id |

**Se NeMo non espone language_id su questa build:** alternative documentate (prompt iniziale, modello alternativo, o accettare auto-detect del modello).

### Fase 1 — Pipeline + IT + EN — **settimana 1–2**

| # | Task | DoD |
|---|------|-----|
| 1.1 | Spike completato | Decisione tecnica scritta |
| 1.2 | `asr_language` su job + pipeline | Job EN → transcript inglese |
| 1.3 | UI select lingua + CLI `--language` | Funzionante su home upload |
| 1.4 | Test campione EN | `transcript.txt` leggibile |
| 1.5 | Docs | Pagina lingue ASR |

### Fase 2 — FR, ES, DE (le 5 core complete) — **settimana 2–3**

| # | Task | DoD |
|---|------|-----|
| 2.1 | Select con tutte e 5 le lingue core | IT · EN · FR · ES · DE |
| 2.2 | Test qualitativo per lingua | WAV/podcast breve per FR, ES, DE |
| 2.3 | Badge lingua su job detail + filtro jobs | Visibile in storico |
| 2.4 | Settings: lingua ASR predefinita | Persistita in `data/settings` |
| 2.5 | Copy UI + sito + MkDocs | Non più “solo italiano” |
| 2.6 | `index.html` stat “Lingua” dinamica | Non più hardcoded `IT` |

**DoD fase 2:** utente carica audio tedesco, sceglie DE, ottiene transcript in tedesco; stesso per FR, ES, EN, IT.
### Fase 3 — Modelli ASR aggiuntivi (opzionale) — **solo con dati**

Trigger per aprire fase 3:

- WER/qualità percepita insufficiente su lingua commerciale target
- Richiesta cliente pagante

Deliverable: registry modelli, download selettivo, job `model_name` + `asr_language`.

---

## 6. Cosa NON fare (v1)

| Non fare | Perché |
|----------|--------|
| Scaricare un `.nemo` per ogni lingua | Parakeet v3 è già multilingue |
| Traduzione automatica del trascritto | Out of scope — vedi summary multilingua |
| Training / fine-tuning | Escluso — vedi `evolutive/old/ROADMAP-EVOLUTIVE.md` |
| Rilevamento lingua automatico obbligatorio | Utile in v2; v1 = scelta esplicita (meno sorprese) |

---

## 7. Rischi

| Rischio | Mitigazione |
|---------|-------------|
| API NeMo diversa tra versioni | Pin versione in `requirements/` + spike |
| Utente sceglie lingua sbagliata | Hint in UI + riprocessa job |
| RAM con modello unico già al limite | Invariato — un solo modello in memoria |
| Docker mini PC | Nessun cambio immagine se un solo `.nemo` |

---

## 8. Stima effort

| Fase | Effort |
|------|--------|
| Fase 0 spike | **XS** (mezza giornata) |
| Fase 1 (IT + EN) | **M** (3–5 giorni) |
| Fase 2 (FR, ES, DE — 5 core) | **M** (3–5 giorni) |
| Fase 3 modelli extra | **L** (solo se serve) |
---

## 9. Ordine rispetto ad altri piani

```
PLAN_MULTILANG_SUMMARY (fase 1)   ← può partire in parallelo
        ‖
PLAN_MULTILANG_ASR (fase 0 spike) ← iniziare subito lo spike
        ↓
PLAN_MULTILANG_ASR (fase 1)
```

Dopo entrambi (ASR + summary): prodotto multilingua coerente — es. audio EN → transcript EN → summary EN (o IT se scelto).

**Prerequisito desktop:** le 5 lingue core dovrebbero essere **completate prima** o **in parallelo** alla fase 2c installer — un’app mondiale senza ASR multilingua non regge sul mercato.
---

## 10. Esito spike NeMo

> **Aggiornato:** 2026-07-02 — implementazione v1

| Domanda | Risposta |
|---------|----------|
| Parametro `language_id` in `transcribe()`? | **Non garantito** su Parakeet v3 — si prova in cascata; il modello **auto-rileva** la lingua |
| Hint decoder `change_decoding_strategy` | **Best-effort** in `transcribe._apply_asr_language_hint()` |
| Versione NeMo testata | Da verificare su ambiente con ASR installato (`scripts/spike_nemo_language.py`) |
| Go per fase 1 | **Sì** — UI + job + pipeline implementati; qualità per lingua da validare con audio reali |

**Nota prodotto:** la scelta lingua in UI è **intenzione utente** e metadata job; Parakeet può comunque auto-rilevare. Per controllo rigido futuro: valutare Canary-1B (fase 3).
