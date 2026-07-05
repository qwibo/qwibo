# Piano microevolutivo — Refactor UI app desktop

> **Data**: 2026-07-05 · **Stato**: 📋 da implementare  
> **Obiettivo**: l'interfaccia dentro Electron deve sembrare un'**app desktop professionale**, non una pagina web incapsulata. Menu nativo Windows, gerarchia visiva chiara, tema **light** e **dark**.  
> **Correlato:** [`PLAN_APP_I18N.md`](./PLAN_APP_I18N.md) (lingue UI + default) · [`PLAN_BRANDING.md`](../done/PLAN_BRANDING.md) Fase 3 UX · [`PLAN_DESKTOP_ELECTRON.md`](../done/PLAN_DESKTOP_ELECTRON.md)

**Hub impostazioni:** questo piano definisce la pagina **`/settings`** (impostazioni globali unificate) — non più pagine sparse senza struttura.

---

## 0. Perché

Oggi l'app carica la UI FastAPI/HTMX in un `BrowserWindow` con:

| Aspetto | Stato attuale | Problema |
|---------|---------------|----------|
| Aspetto | `style.css` scuro fisso, sidebar web | Sembra un tool interno, non retail |
| Menu | Solo tray icon (IT hardcoded) | Manca menu finestra Windows standard |
| Tema | Solo dark (`:root` fisso) | Nessuna scelta utente |
| Chrome | Titolo finestra generico | Poca identità desktop |
| Navigazione | Link HTML in sidebar | Ok per power user, poco “app” |

Target: percezione **WinRAR / VS Code / app consumer** — familiare su Windows, coerente col sito Qwibo.

---

## 1. Cosa esiste già (da riusare)

| Pezzo | Path | Note |
|-------|------|------|
| Shell Electron | `desktop-electron/src/main.js` | Tray, spawn backend, nessun `Menu.setApplicationMenu` |
| UI HTMX | `src/qwibo/ui/templates/` | `index`, `jobs`, settings, partials |
| Impostazioni riassunto | `settings_summary.html` + `/api/settings/summary-keys` | API key cloud, stato provider, LLM locale — **da assorbire in `/settings`** |
| Impostazioni licenza | `settings_license.html` | Ack / testo legale — tab o sezione collegata |
| Segreti LLM | `summary_config.py` → `.secrets/summary_keys.json` | Mai in git; resta backend, UI solo form |
| Priorità provider | `registry.py` → `PROVIDER_IDS` | `"local"` è **primo**; `first_available_provider()` preferisce Qwen offline |
| Stili | `src/qwibo/ui/static/style.css` | ~380 righe, solo palette dark |
| Logo | `assets/images/logo/` | mark + horizontal light/dark |
| Preload | `desktop-electron/src/preload.js` | Base per bridge tema/menu → renderer |

**Non rifare:** logica job, coda, worker, API — solo presentation layer + shell Electron.

---

## 2. Obiettivi UX (Definition of Done)

### Must have (v1)

- [ ] **Pagina Impostazioni globali** (`/settings`) — unico posto per preferenze, LLM, feedback
- [ ] **Menu bar Windows** (`Menu.setApplicationMenu`) con voci utili, non decorative
- [ ] **Tema light + dark** persistito (file preferenze o `localStorage` + sync Electron)
- [ ] **Layout desktop**: header app con logo, area contenuto, sidebar coda più compatta
- [ ] **Tipografia e spaziatura** allineate al brand (DM Sans / mono dove serve)
- [ ] **Stati vuoti e loading** curati (niente pagine “grezze”)
- [ ] **Errori umani** in UI (non solo dialog Electron generici)

### Nice to have (v1.1)

- [ ] Zoom 90% / 100% / 110% da menu Visualizza
- [ ] Scorciatoie da tastiera documentate nel menu
- [ ] Animazioni ridotte se `prefers-reduced-motion`

---

## 3. Menu bar Windows (proposta)

Menu in italiano di default; con `PLAN_APP_I18N` le label diventano tradotte.

| Menu | Voci | Azione |
|------|------|--------|
| **File** | Apri file audio/video… | `dialog.showOpenDialog` → enqueue job |
| | Esci | `app.quit()` |
| **Modifica** | Preferenze… | Naviga a `/settings` |
| **Visualizza** | Tema chiaro / Tema scuro | Toggle + persist |
| | Ricarica interfaccia | `webContents.reload()` (debug/supporto) |
| **Lavori** | Coda e storico | `/jobs` |
| | Nuovo trascrivi | `/` |
| **Aiuto** | Guida utente | Apre docs MkDocs in browser |
| | Apri cartella log | Già in tray — duplicare qui |
| | Informazioni su Qwibo | Dialog versione + licenza |

**Implementazione:** `buildAppMenu(locale, theme)` in `desktop-electron/src/menu.js`; aggiornare menu al cambio lingua/tema via `ipcMain`.

---

---

## 4. Pagina Impostazioni globali (`/settings`)

### Perché una pagina unica

Oggi le preferenze sono sparse:

| Oggi | Problema |
|------|----------|
| `/settings/summary` | Solo LLM; niente lingua/tema/default job |
| `/settings/license` | Pagina separata, poco “app” |
| Default hardcoded in `server.py` | `default_asr_language`, `default_summary_language` = `"it"` |
| Nessun feedback in-app | Utente non sa come segnalare bug |

**Target:** una pagina **Impostazioni** con sezioni/tab chiare. Menu **Modifica → Preferenze** e nav laterale puntano qui.

### Layout proposto

```
/settings
├── [Tab] Generale
├── [Tab] Riassunto LLM
├── [Tab] Licenza
└── [Tab] Feedback e supporto
```

Sidebar nav aggiornata: `Home` · `Coda` · **`Impostazioni`** · (licenza come tab interno, non voce top-level obbligatoria).

### 4.1 Tab **Generale**

| Campo | Tipo | Persistenza | Note |
|-------|------|-------------|------|
| Lingua interfaccia | select 5 lingue | `preferences.json` → `ui_locale` | Vedi `PLAN_APP_I18N` |
| Tema | light / dark / sistema | `ui_theme` | Toggle anche in header |
| Lingua audio predefinita | select IT EN FR ES DE | `default_asr_language` | Precompila form home |
| Lingua riassunto predefinita | select IT EN FR ES DE | `default_summary_language` | Precompila form home |
| Riassunto attivo di default | checkbox | `default_summary_enabled` | Opzionale v1 |
| Lunghezza riassunto default | corto / medio / lungo | `default_summary_length` | Opzionale v1 |

**Salvataggio:** form HTMX `POST /api/settings/preferences` → `preferences.py` → `preferences.json`.

**Rimozione wizard-only:** la lingua scelta all'installazione popola questi campi; l'utente può **reimpostare tutto** da qui in qualsiasi momento.

### 4.2 Tab **Riassunto LLM**

Assorbe il contenuto attuale di `settings_summary.html`, riorganizzato.

#### Priorità LLM locale (regola prodotto — non rompere)

Ordine già in codice (`PROVIDER_IDS`: `local` prima di cloud):

```
1. LLM locale (Qwen GGUF)  — se modello presente e RAM sufficiente
2. Primo provider cloud configurato (openai → gemini → …)
3. Fallback a job time se il provider scelto non è disponibile
```

**Comportamento UI impostazioni:**

| Controllo | Comportamento |
|-----------|---------------|
| **Motore predefinito** | Select: `locale (consigliato)` · openai · gemini · claude · deepseek · kimi |
| Valore consigliato | Se `local` è disponibile → default prefs = `"local"`; altrimenti primo cloud con API key |
| Opzione «Preferisci sempre locale» | Checkbox `prefer_local_llm: true` (default **on**) — a parità di disponibilità, i nuovi job usano Qwen anche se l'utente aveva scelto un cloud in passato |
| Override per job | Resta sulla home: l'utente può cambiare motore per singolo file |

**Implementazione backend:**

- `preferences.json` → `default_summary_provider`, `prefer_local_llm`
- `_summary_context()` legge prefs invece di solo query string
- `summarize._resolve_provider_id()` — se `prefer_local_llm` e local available → forza `local` quando provider non specificato esplicitamente nel job
- **Non** cambiare l'ordine in `first_available_provider()` — già corretto

#### Sezioni nella tab

| Sezione | Contenuto (da `settings_summary.html`) |
|---------|----------------------------------------|
| Stato motori | Griglia provider con badge Pronto / Da configurare |
| API key cloud | Form password per openai, gemini, claude, deepseek, kimi + test connessione |
| LLM locale | RAM, path GGUF, pulsante «Scarica modello» (o link wizard), stato download |
| Modello predefinito | Select motore + nota «Il locale non richiede API key e non invia dati in rete» |

Le API key restano in `.secrets/summary_keys.json` (`summary_config.py`) — la pagina impostazioni è solo UI; nessuna chiave in `preferences.json`.

### 4.3 Tab **Licenza**

- Contenuto attuale di `settings_license.html` (personal / commercial, link documentazione)
- Banner first-run resta; questa tab è consultazione e eventuale inserimento chiave commerciale (futuro `PLAN_BACKLOG` A)

### 4.4 Tab **Feedback e supporto**

Obiettivo: raccogliere segnalazioni **senza uscire dall'app** e abbassare la barriera per bug utili.

| Elemento | Descrizione |
|----------|-------------|
| **Segnala un bug** | Form: categoria Bug · descrizione · passi per riprodurre · email opzionale |
| **Suggerisci una funzione** | Stesso form, categoria Idea |
| **Altro feedback** | Categoria Generale |
| **Allega log** | Checkbox default on: include ultimi ~200 KB di `qwibo.log` + versione app + OS |
| **Esporta pacchetto supporto** | Pulsante → ZIP in Downloads: log redatto, `preferences.json` (senza segreti), `version.txt`, elenco job (solo id/stato, no testi) |
| **Apri cartella log** | Come menu Aiuto / tray |
| **Issue su GitHub** | Link `https://github.com/qwibo/qwibo/issues/new` con template precompilato (versione, OS) |
| **Guida utente** | Link docs MkDocs nella lingua UI |

**Invio v1 (offline-first):**

1. **Primario:** salva bozza in `data_dir/feedback/draft.json` + apre client email / cartella con ZIP allegato (`mailto:` o `shell.showItemInFolder`) — nessun server obbligatorio
2. **v1.1 (opzionale):** `POST` a endpoint (stesso infra di `PLAN_LEAD_GENERATION`) con consenso esplicito

**DoD feedback:**

- [ ] Form validato (descrizione min 20 caratteri)
- [ ] ZIP supporto non contiene API key né testi trascritti
- [ ] Versione e build visibili in fondo alla tab

### 4.5 Altre impostazioni globali (backlog nella stessa pagina)

Da valutare in v1 o v1.1 — stessa tab Generale o sotto-tab **Avanzate**:

| Impostazione | Utilità |
|--------------|---------|
| Cartella dati / job | Apri in Explorer, path read-only |
| Cartella modelli ASR | Dove sta Parakeet `.nemo` |
| Notifiche desktop al completamento job | Win toast (Electron) |
| Avvio con Windows | Checkbox (Electron `app.setLoginItemSettings`) |
| Conservazione storico job | Giorni / numero max (futuro) |

Non bloccare v1: tab Generale + Riassunto + Feedback bastano per il refactor.

### 4.6 Schema `preferences.json` (unificato)

```json
{
  "ui_locale": "it",
  "ui_theme": "dark",
  "default_asr_language": "it",
  "default_summary_language": "it",
  "default_summary_enabled": false,
  "default_summary_length": "medium",
  "default_summary_provider": "local",
  "prefer_local_llm": true,
  "setup_completed_at": "2026-07-05T10:00:00Z"
}
```

File: `%APPDATA%/Qwibo/preferences.json` — letto da Electron (tema, wizard) e da Python (`preferences.py`).

### 4.7 Migrazione route

| Route attuale | Dopo |
|---------------|------|
| `GET /settings/summary` | Redirect → `/settings#summary` o tab Riassunto |
| `GET /settings/license` | Redirect → `/settings#license` |
| `GET /settings` | **Nuova** pagina hub |
| `POST /api/settings/summary-keys` | Invariato (backend) |
| `POST /api/settings/preferences` | **Nuovo** |

Template: `settings.html` con partials `settings_general.html`, `settings_summary.html` (refactor), `settings_license.html`, `settings_feedback.html`.

---

## 5. Tema light / dark

### Modello

```css
:root, [data-theme="dark"] { /* palette attuale */ }
[data-theme="light"] {
  --bg: #f8fafc;
  --panel: #ffffff;
  --border: #e2e8f0;
  --text: #0f172a;
  --muted: #64748b;
  /* accent invariato o leggermente adattato */
}
```

### Persistenza

| Chiave | Dove | Valore |
|--------|------|--------|
| `ui_theme` | `%APPDATA%/Qwibo/preferences.json` | `"light"` \| `"dark"` \| `"system"` |

- All'avvio Electron legge prefs → imposta `data-theme` sul `<html>` via preload prima del paint (evita flash).
- Toggle da menu **e** toggle in UI (icona sole/luna in header).
- `"system"` segue `prefers-color-scheme` (opzionale v1).

### File toccati

- `src/qwibo/ui/static/style.css` — variabili dual-theme
- `src/qwibo/ui/templates/base.html` (o layout wrapper) — `data-theme` su `<html>`
- `desktop-electron/src/preload.js` — `window.qwibo.getTheme()` / `setTheme()`
- `desktop-electron/src/main.js` — menu Visualizza

---

## 6. Refactor visivo UI (HTMX)

### Fasi

| Fase | Deliverable |
|------|-------------|
| **U1** | Template base unico: `base.html` con header (logo + nav + theme toggle), footer minimale |
| **U2** | Home: card upload più grande, stats row, copy meno “dev” |
| **U3** | Coda/storico: tabella o card list con stati colore coerenti |
| **U4** | **`/settings` hub** + tab (Generale, Riassunto, Licenza, Feedback) |
| **U5** | Home + Coda: stesso chrome, default da prefs |
| **U6** | Responsive minimo 960px (già `minWidth` finestra) |

### Principi

- Meno bordi spessi, più whitespace
- Logo Qwibo in header (SVG light/dark)
- Sidebar storico job: larghezza fissa, scroll indipendente
- Bottoni primari un solo stile (brand purple come sito)

---

## 7. Integrazione Electron ↔ UI

```
main.js
  ├─ menu.js          → Menu applicazione
  ├─ preferences.js   → read/write preferences.json
  └─ ipc handlers     → theme, open-file, open-docs, about, export-support-bundle

preload.js
  └─ contextBridge.exposeInMainWorld('qwibo', { exportSupportBundle, … })

UI (HTMX)
  └─ script leggero: ascolta theme, applica data-theme
```

**Regola:** la UI resta servita dal backend Python anche in dev (`qwibo ui`); il bridge `window.qwibo` esiste solo in Electron (feature-detect, no break browser dev).

---

## 8. Ordine di implementazione

```
U1 base template + CSS variables light/dark
    ↓
preferences.py + schema JSON
    ↓
U4 /settings hub — tab Generale (lingua, tema, default job)
    ↓
U4 tab Riassunto (migra settings_summary + prefer_local_llm)
    ↓
U4 tab Feedback (form + ZIP supporto)
    ↓
Menu bar Electron → Preferenze = /settings
    ↓
U2–U3 home + coda (default da prefs)
    ↓
PLAN_APP_I18N (traduzioni tab Impostazioni)
```

**Prerequisito soft:** nessuno bloccante. Può partire in parallelo a fix alpha installer.

---

## 9. Non obiettivi (questo piano)

- Riscrivere in React/Vue (resta HTMX)
- Custom title bar frameless (fase 2 se serve)
- macOS menu bar (stesso codice Electron, adattare in sprint Mac)
- Ridisegno sito marketing (resta `qwibo.github.io`)

---

## 10. Test / DoD finale

- [ ] Installer Win: menu visibile, tema dark default, switch light persiste al riavvio
- [ ] **Impostazioni:** cambio lingua default + motore riassunto → home rispetta i nuovi default
- [ ] **LLM locale:** con Qwen presente e `prefer_local_llm` on, nuovo job usa locale senza API key
- [ ] **Feedback:** ZIP supporto generato senza segreti; form bug compilabile
- [ ] “Apri file” dal menu crea job come drag-and-drop
- [ ] Dev mode `npm run dev`: UI identica (menu opzionale in dev)
- [ ] Nessuna regressione coda, riassunto, licenza first-run
- [ ] `/settings/summary` e `/settings/license` redirectano correttamente
- [ ] Screenshot prima/dopo per release notes
