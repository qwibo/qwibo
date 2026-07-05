# Piano microevolutivo — App desktop (Electron)

> **Data**: 2026-07-02 · **Stato**: ✅ **scelta ufficiale**  
> **Decisione:** Electron + backend Python embedded (v1). Nuitka opzionale in v2.  
> **Storico scelta:** [DESKTOP_CONFRONTO.md](../reference/DESKTOP_CONFRONTO.md) · Tauri archiviato in [old/PLAN_DESKTOP_TAURI.md](../old/PLAN_DESKTOP_TAURI.md)  
> **Obiettivo:** installer **Windows** e **macOS** retail, prodotto professionale mondiale (Win + Mac Intel + Apple Silicon).

---

## 0. Perché Electron

Electron è lo stack delle app desktop consumer più diffuse (VS Code, Slack, Discord, Figma). Per Qwibo offre:

- **Win + Mac** dallo stesso progetto (`electron-builder`).
- Ecosistema maturo: tray, `electron-updater`, code signing, DMG/NSIS documentati.
- Percezione “app vera” sul mercato retail e professionale.
- Comunicazione con il backend **semplice**: spawn processo + `http://127.0.0.1:{port}/` (stessa UI HTMX di oggi).

**Backend v1:** Python **embedded portatile** (`python-build-standalone` + venv) — affidabile con PyTorch/NeMo, stesso comportamento del dev.

**Backend v2 (opzionale):** compilazione **Nuitka** solo se serve anti-tampering enterprise — non blocca il lancio v1.

Con target **16 GB RAM**, i ~150–300 MB di Chromium sono trascurabili rispetto a NeMo (~1.5 GB).

---

## 1. Cosa esiste già (riuso)

| Pezzo | File / path | Riuso desktop |
|-------|-------------|---------------|
| Web UI | `src/qwibo/ui/server.py` | `BrowserWindow` → `http://127.0.0.1:{port}/` |
| Avvio | `start.bat`, `qwibo ui`, `ui/launch.py` | `scripts/entry_backend.py` |
| Worker ASR | `worker.py` + `process_guard.py` | Stesso codice nel runtime embedded |
| Coda job | `jobs.py` (SQLite) | Path sotto AppData |
| Licenza | `license_info.py` | First-run + `/settings/license` |
| Download modelli | `download_model.py` | Wizard integrato al first-run |

---

## 2. Architettura target

```
┌─────────────────────────────────────────────────────────┐
│  Electron (Node.js + Chromium)                           │
│  ┌───────────────────────────────────────────────────┐  │
│  │ BrowserWindow → http://127.0.0.1:{port}/          │  │
│  └───────────────────────────────────────────────────┘  │
│  Main: spawn backend · poll /health · tray · single inst. │
│  electron-updater · electron-builder (Win + Mac)         │
└──────────────────────────┬──────────────────────────────┘
                           │ spawn + HTTP localhost
┌──────────────────────────▼──────────────────────────────┐
│  Backend Python embedded (v1)                            │
│  resources/python/python.exe + venv pre-popolato         │
│  ┌─────────────┐    ┌──────────────┐                    │
│  │ FastAPI UI  │◄──►│ worker ASR   │                    │
│  └─────────────┘    └──────────────┘                    │
│  PyTorch · NeMo · ffmpeg bundled                         │
└─────────────────────────────────────────────────────────┘
```

### Flusso avvio (semplice)

1. Electron `main.js` avvia `python.exe scripts/entry_backend.py` con env AppData.
2. Poll `GET /health` ogni 200 ms finché risponde.
3. `BrowserWindow.loadURL("http://127.0.0.1:" + port)`.
4. Alla chiusura: kill tree (worker + uvicorn) — come `process_guard` oggi.

**Nessun IPC custom obbligatorio.** La UI parla già HTTP con FastAPI.

### Decisioni

1. **Electron = solo shell + orchestrazione** — zero logica ASR in JavaScript.
2. **Un solo backend** — UI web embedded = stessa UI del browser.
3. **Localhost only** — bind `127.0.0.1` in modalità desktop.
4. **Dati utente fuori dal bundle** — `AppData/Qwibo/` (Win) o `~/Library/Application Support/Qwibo/` (Mac).
5. **Modelli al first-run** — installer leggero, Parakeet ~2.5 GB scaricato dopo.
6. **Mac obbligatorio** — build ARM64 (Apple Silicon) + x64 (Intel legacy) o Universal 2.

---

## 3. Layout percorsi desktop

| Risorsa | Sviluppo (oggi) | Desktop |
|---------|-----------------|---------|
| Modelli ASR/LLM | `{repo}/models/` | `%AppData%/Qwibo/models/` (Win) · `~/Library/Application Support/Qwibo/models/` (Mac) |
| Job + SQLite | `{repo}/data/` | `.../Qwibo/data/` |
| Secrets / API key | `data/.secrets/` | stesso sotto AppData |
| Log | console | `.../Qwibo/logs/` |
| Runtime Python | venv dev | `resources/python/` (installer) o `AppData/runtime/{ver}/` (OTA) |
| ffmpeg | PATH | `resources/ffmpeg` (bundled per OS/arch) |

**Env:** `QWIBO_DATA`, `NEMO_CACHE_DIR`, `QWIBO_PORT`.

---

## 4. Fasi

### Fase 2b — Backend desktop-ready — **1–2 settimane** (prima di Electron)

| # | Task | File coinvolti |
|---|------|----------------|
| 2b.1 | `GET /health` + `GET /api/status` | `ui/server.py` |
| 2b.2 | Porta dinamica + bind `127.0.0.1` | `launch.py`, env `QWIBO_PORT` |
| 2b.3 | `resolve_paths()` centralizzato | `config.py` |
| 2b.4 | `qwibo doctor` | `scripts/doctor.py` |
| 2b.5 | Log file rotante | `logging` config |
| 2b.6 | `scripts/entry_backend.py` | Entrypoint unico per Electron spawn |

### Fase 2a — Wrapper Electron dev — **2–3 settimane**

| # | Task | DoD |
|---|------|-----|
| 2a.1 | Cartella `desktop-electron/` | `npm run dev` avvia |
| 2a.2 | `backend-spawn.js`: spawn Python (dev: sistema; prod: embedded) | `/health` OK |
| 2a.3 | `BrowserWindow` su porta dinamica | Upload + trascrizione |
| 2a.4 | Chiusura → kill tree | Zero zombie |
| 2a.5 | `app.requestSingleInstanceLock()` | Secondo avvio → focus |
| 2a.6 | Tray icon + menu Esci | Test Win |

```
qwibo/
├── desktop-electron/
│   ├── package.json
│   ├── electron-builder.yml
│   ├── src/
│   │   ├── main.js
│   │   ├── preload.js          # minimale, se serve
│   │   └── backend-spawn.js
│   └── README.md
├── scripts/
│   └── entry_backend.py        # set env AppData, ui + worker
```

**Dev:** Python di sistema + `npm run dev`.  
**Non include:** installer, signing, Mac.

### Fase 2c — Packaging installer — **6–10 settimane**

| # | Task | Piattaforma |
|---|------|-------------|
| 2c.1 | **python-build-standalone** + venv pre-popolato | Win x64 + Mac ARM64 (+ Intel se serve) |
| 2c.2 | Bundle ffmpeg statico per OS/arch | Win + Mac |
| 2c.3 | `electron-builder` → NSIS (Win) | Windows |
| 2c.4 | `electron-builder` → DMG | macOS |
| 2c.5 | Code signing (Authenticode + Apple Developer) | Retail |
| 2c.6 | Notarization Apple | Obbligatoria per Mac retail |
| 2c.7 | First-run: wizard modelli + licenza | UX |
| 2c.8 | OTA — vedi §5 | Aggiornamenti |

**Sequenza piattaforme:** Windows stabile → Mac Apple Silicon → Mac Intel (se richiesto).

| Componente | Dimensione |
|------------|------------|
| Electron shell | ~80–120 MB |
| Python + torch CPU | ~1–2 GB |
| Modelli (post-install) | ~2.5 GB |

### Fase 2d — Licenza commerciale — **1–2 settimane**

Vedi `PLAN_BACKLOG.md` § A. Prerequisito vendita MSI/DMG.

### Fase 2e — Nuitka (opzionale, post-v1) — **solo se serve**

| # | Task | DoD |
|---|------|-----|
| 2e.1 | Spike Nuitka su `entry_backend.py` + torch + NeMo | Go/no-go documentato |
| 2e.2 | Pipeline CI Nuitka | Binario al posto di `python.exe` in prod |
| 2e.3 | Test VM pulite Win + Mac | Trascrizione OK |

**Non iniziare 2e** finché v1 embedded non è in vendita. Se lo spike fallisce, v1 resta valida.

---

## 5. Aggiornamenti OTA

| Componente | Meccanismo | Frequenza |
|------------|------------|-----------|
| Shell Electron | `electron-updater` + GitHub Releases | Spesso |
| Backend Python | Zip in `AppData/runtime/{ver}/` via manifest | Raro |
| Modelli | Wizard download esistente | Quando cambia modello |

```json
{
  "app_version": "1.2.0",
  "min_backend": "1.1.0",
  "backend_url_win": "https://releases.../backend-1.1.0-win.zip",
  "backend_url_mac_arm64": "https://releases.../backend-1.1.0-mac-arm64.zip"
}
```

---

## 6. Mac — note specifiche

| Aspetto | Azione |
|---------|--------|
| Apple Silicon (M1–M4) | Build PyTorch ARM64 — **priorità** |
| Intel Mac | Build x64 separata o Universal 2 |
| Notarization | Account Apple Developer 99$/anno; `electron-builder` + `notarize` |
| Hardened runtime | Entitlements per spawn ffmpeg e subprocess |
| WebKit vs Chromium | Electron usa Chromium su Mac — UI identica a Windows |

Il lavoro Mac **non dipende** dalla shell scelta (stesso sforzo con Tauri). Dipende da **torch ARM64 + notarization**.

---

## 7. Protezione IP e licenza

Qwibo è **software proprietario** (`LICENSE`); le dipendenze (PyTorch, NeMo) restano open source.

| v1 embedded | v2 Nuitka (opzionale) |
|-------------|----------------------|
| Codice in `resources/` / AppData — leggibile da utente tecnico | Codice app compilato — più difficile da copiare |
| Protezione commerciale via **licenza + chiavi** | + anti-tampering per enterprise |

La **professionalità mondiale** viene da installer firmato, wizard, updater, supporto — non solo da offuscamento codice.

---

## 8. Rischi e mitigazioni

| Rischio | Mitigazione |
|---------|-------------|
| PyTorch + NeMo su Mac ARM64 | Build dedicate; test su hardware reale M-series |
| Notarization rifiutata | Entitlements corretti; spike early su Mac |
| Antivirus false positive | Code signing Authenticode + Apple |
| Worker zombie | `process_guard` + Electron kill tree |
| Electron RAM | Accettato — non è il bottleneck con NeMo |
| Nuitka blocca il progetto | **Rimandato a v2** — v1 non dipende da Nuitka |

---

## 9. Cosa NON fare

| Evitare | Motivo |
|---------|--------|
| Logica ASR in JavaScript | Impossibile con NeMo |
| Nuitka come prerequisito v1 | Rischio mesi di blocco |
| Includere 2.5 GB modello nel setup | UX e CI ingestibili |
| Script `.ps1` nel repo | Antivirus utente |
| Solo Windows senza piano Mac | Obiettivo prodotto mondiale |

---

## 10. Test accettazione (release v1)

- [ ] Install Windows 11 pulito → wizard → trascrizione 1 min MP3
- [ ] Install macOS Apple Silicon pulito → stesso flusso
- [ ] Chiudi durante job → riapri → stato coerente
- [ ] Seconda istanza → focus prima finestra
- [ ] `electron-updater` applica patch shell
- [ ] Aggiornamento backend via manifest
- [ ] Solo `127.0.0.1` in ascolto
- [ ] Licenza personal + link commerciale

---

## 11. Stima effort

| Fase | Effort |
|------|--------|
| 2b Backend-ready | **M** |
| 2a Wrapper Electron | **M** |
| 2c Installer Win | **L** |
| 2c Installer Mac | **L–XL** |
| 2d Licenza | **M** |
| 2e Nuitka (opz.) | **XL** — post-v1 |

**Sequenza:** 2b → 2a → 2c Win → 2c Mac → 2d → (2e se serve).

---

## 12. Riferimenti

- Electron: https://www.electronjs.org/
- electron-builder: https://www.electron.build/
- electron-updater: https://www.electron.build/auto-update
- python-build-standalone: https://github.com/astral-sh/python-build-standalone
- Backend: `src/qwibo/ui/launch.py`, `worker.py`, `config.py`, `start.bat`
