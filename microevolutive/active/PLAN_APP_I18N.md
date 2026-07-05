# Piano microevolutivo — App desktop multilingua (UI + default)

> **Data**: 2026-07-05 · **Stato**: 📋 da implementare  
> **Obiettivo**: interfaccia dell'app e **lingue predefinite** (trascrizione + riassunto) nelle **5 lingue core** — IT, EN, FR, ES, DE. Scelta alla **prima installazione**; modificabile dopo in preferenze e per singolo job.  
> **Non confondere con:** [`done/PLAN_MULTILANG_ASR.md`](../done/PLAN_MULTILANG_ASR.md) (pipeline NeMo già multilingua) · questo piano riguarda **UI tradotta + default utente**.

---

## 0. Tre concetti distinti

| Concetto | Esempio | Stato oggi |
|----------|---------|------------|
| **Lingua UI** | Menu “File”, “Coda e storico”, messaggi errore | Solo italiano (hardcoded) |
| **Lingua audio / ASR** | Audio parlato in inglese → transcript EN | ✅ 5 lingue in job (`asr_language`) |
| **Lingua riassunto** | Summary in francese | ✅ 5 lingue in job (`summary_language`) |

**Default oggi:** `default_asr_language` e `default_summary_language` sono **`"it"` fissi** in `server.py` — non leggono preferenze utente.

**Obiettivo:** un'unica scelta all'installazione imposta **UI + default ASR + default summary**; l'utente può cambiarle singolarmente dopo.

---

## 1. Lingue supportate (v1)

Stesso set di `src/qwibo/languages.py`:

| Codice | UI | ASR/Summary |
|--------|-----|-------------|
| `it` | Italiano | ✅ |
| `en` | English | ✅ |
| `fr` | Français | ✅ |
| `es` | Español | ✅ |
| `de` | Deutsch | ✅ |

**Estensione file:** `CORE_LANGUAGE_CODES` resta fonte di verità; aggiungere `UI_LOCALE_LABELS` per nome lingua nella **propria** lingua (es. “Deutsch”, non “Tedesco”).

---

## 2. Flusso installazione / primo avvio

### Decisione: wizard Electron, non pagina NSIS custom

Come in [`PLAN_LEAD_GENERATION.md`](./PLAN_LEAD_GENERATION.md): input complessi in NSIS sono fragili.

```
Installer NSIS (solo copy file)
    ↓
Primo avvio Electron
    ↓
① Schermata lingua (NUOVA)     ← 5 bandiere / elenco, obbligatoria
    ↓
② Download modelli (esistente)  setup/index.html
    ↓
③ App principale
```

### Schermata ① — contenuto

- Titolo: “Scegli la lingua dell'app” (+ equivalenti nelle 5 lingue mostrate come label native)
- Sottotitolo: “Userai questa lingua per l'interfaccia e come predefinita per trascrizione e riassunto. Potrai cambiarla dopo.”
- Select o card cliccabili: IT · EN · FR · ES · DE
- Pulsante Continua → salva prefs → avvia setup modelli

### Persistenza

File: `%APPDATA%/Qwibo/preferences.json` (Windows) — stesso file usato da tema UI (`PLAN_UI_DESKTOP.md`).

```json
{
  "ui_locale": "it",
  "default_asr_language": "it",
  "default_summary_language": "it",
  "ui_theme": "dark",
  "setup_completed_at": "2026-07-05T10:00:00Z"
}
```

**Regola v1:** alla scelta iniziale, i tre campi lingua ricevono **lo stesso codice**. In preferenze l'utente può divergere (es. UI in IT, audio default EN).

---

## 3. Backend — leggere le preferenze

### Nuovo modulo

`src/qwibo/preferences.py`:

- `load_preferences() -> UserPreferences`
- `save_preferences(prefs)` 
- Path: `QWIBO_DATA_DIR / "preferences.json"` (allineato ad AppData in Electron)

### Modifiche `server.py`

| Punto | Da | A |
|-------|-----|---|
| `index` context | `default_asr_language: "it"` | da `load_preferences()` |
| `index` context | `default_summary_language: "it"` | da `load_preferences()` |
| Template globals | `language_label` solo IT | `language_label(code, locale=ui_locale)` |
| Nuova route | — | `GET/PATCH /settings/preferences` (o HTMX form) |

### API per Electron setup

`GET /api/preferences` + `PUT /api/preferences` (JSON) — il wizard prima del backend full può scrivere via file diretto da Electron se il backend non è ancora up; preferibile unificare su file prefs letto da entrambi.

---

## 4. Traduzione UI (5 lingue)

### Approccio consigliato: file JSON per locale

```
src/qwibo/ui/locales/
  it.json
  en.json
  fr.json
  es.json
  de.json
```

Chiavi flat o nested, es.:

```json
{
  "nav.home": "Home",
  "nav.jobs": "Coda e storico",
  "nav.summary_settings": "Riassunto LLM",
  "nav.license": "Licenza",
  "home.upload_title": "Trascrivi audio o video",
  "job.status.running": "In corso"
}
```

### Template Jinja2

```jinja2
{{ t('nav.home') }}
```

Helper `t(key)` registrato in `server.py` con `ui_locale` da prefs/cookie/query.

### Ambito v1 (stringhe da tradurre)

| Area | Priorità |
|------|----------|
| Nav, home, form upload | P0 |
| Coda/storico, stati job | P0 |
| Settings summary + license | P1 |
| Messaggi errore comuni | P1 |
| Email/modal first-run | P2 (con lead gen) |
| Tray + menu Electron | P0 (con `PLAN_UI_DESKTOP`) |

**Stima:** ~120–180 chiavi per v1.

### Cosa NON tradurre in v1

- Contenuto trascritto / riassunto (è output ASR/LLM)
- Documentazione MkDocs (resta IT/EN su sito; link da menu Aiuto alla lingua UI se esiste)

---

## 5. Preferenze in app (post-install)

Gestite nella tab **Generale** della pagina unificata **`/settings`** (vedi [`PLAN_UI_DESKTOP.md`](./PLAN_UI_DESKTOP.md) §4.1) — non una pagina separata.

| Campo | Controllo |
|-------|-----------|
| Lingua interfaccia | Select 5 lingue → reload UI |
| Lingua audio predefinita | Select 5 lingue |
| Lingua riassunto predefinita | Select 5 lingue |
| Tema | light / dark (se `PLAN_UI_DESKTOP` fatto) |

La home mantiene i select per job singolo (già esistenti); precompilati dai default prefs.

---

## 6. Electron — menu e setup

| File | Modifica |
|------|----------|
| `desktop-electron/setup/index.html` | Step 0 lingua prima del progress download |
| `desktop-electron/src/model-setup.js` | Salta step lingua se `preferences.json` esiste |
| `desktop-electron/src/main.js` | Passa `ui_locale` a `buildAppMenu()` |
| `desktop-electron/src/menu.js` | Label menu da JSON locale |

**Rilevamento lingua installer (opzionale):** pre-selezionare in wizard la lingua OS (`app.getLocale()`) se è una delle 5 core; altrimenti default `en`.

---

## 7. Fasi e Definition of Done

| Fase | Deliverable | DoD |
|------|-------------|-----|
| **I0** | `preferences.json` + `preferences.py` | Lettura/scrittura; default `it` se assente |
| **I1** | Wizard lingua primo avvio | Scelta obbligatoria; prefs salvate |
| **I2** | `server.py` usa default da prefs | Home mostra select precompilati corretti |
| **I3** | `locales/*.json` + helper `t()` | Nav + home in 5 lingue |
| **I4** | Tab Generale in `/settings` | Cambio UI + default ASR/summary (hub unificato) |
| **I5** | Menu Electron tradotto | Coerente con `ui_locale` |
| **I6** | Coda, settings, errori | Copertura P0/P1 completa |

### DoD finale sprint

- [ ] Installazione pulita: wizard lingua → modelli → app nella lingua scelta
- [ ] Default trascrizione e riassunto = lingua scelta
- [ ] Cambio lingua UI da Preferenze senza reinstall
- [ ] Job singolo: override lingua audio/riassunto ancora possibile
- [ ] Dev `qwibo ui`: prefs in cartella dati locale; fallback `it`

---

## 8. Ordine rispetto ad altri piani

```
PLAN_APP_I18N  I0–I2  (prefs + wizard)     ← può partire subito
      ↓
PLAN_UI_DESKTOP  U1     (layout + tema)    ← in parallelo
      ↓
PLAN_APP_I18N  I3–I6  (traduzioni complete)
      ↓
PLAN_UI_DESKTOP  menu   (menu tradotti)
```

---

## 9. Non obiettivi

- Più di 5 lingue in UI (Parakeet ne supporta 25 — solo ASR avanzato futuro)
- Traduzione automatica dei transcript
- Localizzazione installer NSIS (wizard Electron basta)
- RTL / lingue non latine

---

## 10. Riferimenti codice

| File | Ruolo |
|------|--------|
| `src/qwibo/languages.py` | Codici e label ASR |
| `src/qwibo/ui/server.py` | Default hardcoded oggi — da collegare a prefs |
| `src/qwibo/ui/templates/index.html` | Select `asr_language` / `summary_language` |
| `desktop-electron/setup/` | Wizard post-install |
| `microevolutive/done/PLAN_MULTILANG_ASR.md` | Pipeline ASR (già fatto) |
