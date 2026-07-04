# Qwibo Desktop v0.1 — installer retail

App Windows **completa per l'utente finale**: scarica `Qwibo-Setup-0.1.0.exe`, installa, apre.  
Nessun Python, nessun terminale, nessun Docker.

## Utente finale

1. Scarica `Qwibo-Setup-0.1.0.exe`
2. Doppio click → Avanti → Installa → **Fine** (si apre Qwibo)
3. **Configurazione iniziale** (~4–5 GB, una sola volta):
   - modello vocale Parakeet (~2,5 GB) — **obbligatorio**
   - modello riassunto locale Qwen (~2 GB) — **automatico se RAM ≥ 16 GB**
4. Al termine si apre l'app, pronta all'uso

Nessun download durante la prima trascrizione.  
Dati e modelli: `%APPDATA%\qwibo-desktop\`  
Log diagnostici: `%APPDATA%\qwibo-desktop\logs\` (menu tray → **Apri cartella log**)

## Sviluppatore — creare l'installer

Serve **una volta** su macchina di build (Windows, Python 3.12+, Node 20+):

```bat
cd desktop-electron
build_installer.bat          REM prima volta (30-60 min)
build_installer.bat fast     REM rebuild veloce (~10-15 min)
```

Output: `release\Qwibo-Setup-0.1.0.exe` — **solo questo file** va distribuito.

La build:
- copia il codice backend in `backend/vendor/`
- scarica Python standalone + crea venv con torch, NeMo, FastAPI
- scarica ffmpeg statico
- impacchetta tutto in NSIS con Electron

**Tempo prima build:** 20–40 min (download torch/NeMo).  
**Dimensione installer:** ~2–3 GB (normale per app ASR locale).

## Sviluppo rapido (solo dev)

Dopo `install.bat` (venv dev, opzionale):

```bat
npm run dev
```

## Indipendenza dal repo principale

| | Desktop installer | Repo Docker/FastAPI |
|---|---|---|
| Runtime Python | embedded in installer | container / venv dev |
| ffmpeg | bundled | in immagine Docker |
| Codice | `backend/vendor/` | `src/qwibo` |
| Dati utente | AppData desktop | `data/` volume |

Zero modifiche a `docker/` o al server FastAPI del mini PC.

## Roadmap v0.2

- Code signing Authenticode (SmartScreen)
- Download modello con barra di progresso in-app
- Mac DMG + notarization
