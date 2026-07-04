# Piano microevolutivo — App desktop (Tauri + sidecar Python)

> **⚠️ ARCHIVIATO** — luglio 2026. Scelta ufficiale: [PLAN_DESKTOP_ELECTRON.md](../PLAN_DESKTOP_ELECTRON.md).  
> **Data**: 2026-07-02 · **Stato**: ❌ non attivo · **Opzione**: A (scartata)  
> **Obiettivo**: installer **Windows** e **macOS** per uso retail/commerciale,
> con **time-to-market** rapido e packaging **affidabile** (embedded Python).  
> **Riferimento commerciale:** `docs/en/reference/commercial-license.md`

---

## 0. Perché questa opzione esiste

Tauri offre una shell desktop **leggera** (~20 MB) che usa il motore web del sistema (WebView2 su Windows, WebKit su Mac) invece di impacchettare Chromium. Il backend Python resta **embedded portatile** — stesso comportamento dell’ambiente di sviluppo, senza combattere Nuitka su PyTorch/NeMo.

**Trade-off:** protezione IP del codice Python **media** (runtime leggibile in AppData). Adatta se licenza + contratto B2B bastano.

---

## 1. Cosa esiste già (forte base)

| Pezzo | File / path | Riuso desktop |
|-------|-------------|---------------|
| Web UI | `src/qwibo/ui/server.py` (FastAPI) | WebView → `http://127.0.0.1:8501` |
| Avvio UI | `start.bat`, `qwibo ui`, `ui/launch.py` | Sidecar entrypoint |
| Worker ASR | `worker.py` + `process_guard.py` | Stesso processo o subprocess |
| Coda job | `jobs.py` (SQLite) | Path sotto AppData |
| Licenza | `license_info.py` + modal UI | First-run obbligatorio |
| Download modelli | `download_model.py`, `download_summary_llm.py` | Wizard integrato |
| Docker | `docker/` | **Non** è il desktop — resta per mini PC/server |

Il refactor desktop è in gran parte **packaging e percorsi**, non riscrittura ASR.

---

## 2. Architettura target

```
┌─────────────────────────────────────────────────────────┐
│  Tauri 2.x (Rust)                                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │ WebView (Wry) → http://127.0.0.1:{port}/          │  │
│  └───────────────────────────────────────────────────┘  │
│  Tray · single instance · Tauri updater                  │
│  Spawn / monitor / kill sidecar                          │
└──────────────────────────┬──────────────────────────────┘
                           │ health HTTP
┌──────────────────────────▼──────────────────────────────┐
│  Sidecar Python (python-build-standalone + venv)         │
│  ┌─────────────┐    ┌──────────────┐                    │
│  │ FastAPI UI  │◄──►│ qwibo      │                    │
│  │ (uvicorn)   │    │ worker       │                    │
│  └─────────────┘    └──────────────┘                    │
│  NeMo · ffmpeg · modelli in AppData                      │
└─────────────────────────────────────────────────────────┘
```

### Decisioni

1. **NeMo resta in Python** — niente port ASR in Rust/C++.
2. **Un solo backend** — UI web embedded = stessa UI del browser.
3. **Localhost only** — bind `127.0.0.1` in modalità desktop.
4. **Dati utente fuori dal bundle** — `AppData/Qwibo/` (Win) o `~/Library/Application Support/Qwibo/` (Mac).
5. **Packaging primario: embedded Python** — non PyInstaller/Nuitka (vedi opzione B).

---

## 3. Layout percorsi desktop

| Risorsa | Sviluppo (oggi) | Desktop |
|---------|-----------------|---------|
| Modelli ASR/LLM | `{repo}/models/` | `%AppData%/Qwibo/models/` |
| Job + SQLite | `{repo}/data/` | `%AppData%/Qwibo/data/` |
| Secrets / API key | `data/.secrets/` | stesso sotto AppData |
| Log | console / file | `%AppData%/Qwibo/logs/` |
| Runtime Python | venv dev | `%AppData%/Qwibo/runtime/` o `resources/python/` |
| ffmpeg | PATH / winget | Bundled in `resources/ffmpeg.exe` |

**Env:** `QWIBO_DATA`, `NEMO_CACHE_DIR` già in `config.py`.

---

## 4. Fasi

### Fase 2b — Backend desktop-ready — **1–2 settimane** (prima della shell)

**Condivisa con Electron** — si fa una volta sola.

| # | Task | File coinvolti |
|---|------|----------------|
| 2b.1 | `GET /health` + `GET /api/status` | `ui/server.py` |
| 2b.2 | Porta configurabile + bind 127.0.0.1 | `launch.py`, env `QWIBO_PORT` |
| 2b.3 | `resolve_paths()` centralizzato | `config.py` |
| 2b.4 | Wizard CLI: `qwibo doctor` | `scripts/doctor.py` |
| 2b.5 | Log file rotante | `logging` config |

### Fase 2a — Wrapper dev (senza installer) — **2–3 settimane**

| # | Task | DoD |
|---|------|-----|
| 2a.1 | Cartella `desktop-tauri/` | `cargo tauri dev` avvia |
| 2a.2 | Sidecar `start_backend.py` (no `.ps1`) | Health `GET /health` OK |
| 2a.3 | WebView su porta dinamica | UI upload funziona |
| 2a.4 | Chiusura app → termina worker + uvicorn | Nessun zombie |
| 2a.5 | Single instance | Secondo avvio → focus finestra |

```
qwibo/
├── desktop-tauri/
│   ├── src-tauri/
│   │   ├── tauri.conf.json
│   │   ├── src/main.rs
│   │   └── icons/
│   ├── README.md
│   └── sidecar/
│       └── start_backend.py
```

**Dev:** Python di sistema. **Non include** installer, signing, OTA.

### Fase 2c — Packaging installer — **4–8 settimane**

| # | Task | Note |
|---|------|------|
| 2c.1 | **python-build-standalone** + venv pre-popolato | **Primario** — non PyInstaller |
| 2c.2 | Bundle ffmpeg | Win static / Mac binary |
| 2c.3 | MSI / NSIS o WiX | Windows |
| 2c.4 | DMG + notarization | macOS (dopo Win stabile) |
| 2c.5 | Code signing | Authenticode + Apple |
| 2c.6 | First-run download modelli | Installer leggero |
| 2c.7 | OTA — vedi §5 | Manifest backend |

**Fallback packaging** (solo se embedded fallisce): installer “richiede Python 3.11” per beta.

| Componente | Dimensione |
|------------|------------|
| Shell Tauri | ~15–30 MB |
| Python + torch CPU | ~1–2 GB |
| Modelli (post-install) | ~2.5 GB |

### Fase 2d — Licenza commerciale

Vedi `PLAN_BACKLOG.md` § A.

---

## 5. Aggiornamenti OTA

| Componente | Meccanismo |
|------------|------------|
| Shell Tauri | [Tauri updater](https://v2.tauri.app/plugin/updater/) |
| Backend Python | Zip in `AppData/runtime/{version}/` via manifest |
| Modelli | Wizard download esistente |

Manifest unico su GitHub Releases (`app_version`, `min_backend`, `backend_url_*`). All’avvio Tauri confronta versioni e scarica backend se necessario — **senza** reinstall da 2 GB.

---

## 6. Cosa NON fare (in questa opzione)

| Evitare | Motivo |
|---------|--------|
| Nuitka come default | Complessità su NeMo; vedi opzione B se serve IP |
| Riscrivere UI in Qt/WPF/WinUI | Due front-end |
| Includere 2.5 GB nel MSI | UX e CI |
| Script `.ps1` nel repo | Antivirus utente |
| macOS come prima piattaforma | Win = mercato primario IT |

---

## 7. Rischi e mitigazioni

| Rischio | Mitigazione |
|---------|-------------|
| Distribuire torch+NeMo | python-build-standalone; test VM pulita |
| Codice Python leggibile | Accettato in A; opzione B se problema |
| Antivirus false positive | Code signing |
| Worker zombie | `process_guard` + Tauri kill tree |
| Apple notarization | Budget; Mac dopo Win |

---

## 8. Test accettazione (release v1)

- [ ] Install Windows 11 pulito → wizard → trascrizione 1 min MP3
- [ ] Chiudi durante job → riapri → stato coerente
- [ ] Seconda istanza → focus prima finestra
- [ ] Disinstall → dati AppData opzionali (checkbox)
- [ ] Licenza personal + link commerciale
- [ ] Solo `127.0.0.1` in ascolto

---

## 9. Stima effort

| Fase | Effort |
|------|--------|
| 2b Backend-ready | **M** (condiviso) |
| 2a Wrapper Tauri | **M** |
| 2c Installer | **L–XL** |
| 2d Licenza | **M** |

**Sequenza:** 2b → 2a → 2c → 2d.

---

## 10. Riferimenti

```
src/qwibo/ui/launch.py
src/qwibo/ui/process_guard.py
src/qwibo/worker.py
src/qwibo/config.py
start.bat
```

- Tauri: https://v2.tauri.app/
- Sidecar: https://v2.tauri.app/develop/sidecar/
- python-build-standalone: https://github.com/astral-sh/python-build-standalone
- Confronto: [DESKTOP_CONFRONTO.md](./DESKTOP_CONFRONTO.md)
