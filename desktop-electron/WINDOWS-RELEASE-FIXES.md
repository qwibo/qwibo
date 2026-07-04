# Qwibo Desktop — Fix release Windows

**Stadio release: ALPHA** — versione `0.1.0-alpha.1`.
Prima build funzionante end-to-end (trascrizione + riassunto locale) collaudata
su hardware reale (un mini PC). Non firmata, testata su poche macchine: adatta a
test ristretti, non ancora distribuzione di massa. Prossimi stadi: beta (più
tester) → RC → 1.0 stabile.

Artefatto: `release/Qwibo-Setup-0.1.0-alpha.1.exe`.

Registro dei fix applicati per rendere l'installer Windows **distribuibile e
funzionante su PC diversi dalla macchina di build**. Ordine: prima i blocker,
poi build/packaging, robustezza runtime, qualità/diagnostica.

Aggiornato: 2026-07-04.

---

## 🔴 Blocker — impedivano l'avvio su qualsiasi PC "pulito"

### B6 — Riassunto locale in crash `0xC000001D` (istruzione illegale) su CPU senza AVX2 ⭐ NUOVO
- **Sintomo:** su PC diversi dalla macchina di build la **trascrizione funziona**,
  ma il **riassunto locale** fallisce subito con
  `OSError: [WinError -1073741795] Windows Error 0xc000001d`
  (`STATUS_ILLEGAL_INSTRUCTION`) nel momento in cui `llama-cpp-python` carica il
  modello GGUF (`Llama(model_path=...)` in `local_qwen.py`). Nessun log utile:
  il processo muore a livello di CPU.
- **Causa (root cause):** la **wheel CPU precompilata** di `llama-cpp-python`
  (`abetlen.github.io/whl/cpu`) contiene un solo `ggml-cpu.dll` compilato con
  istruzioni **AVX2/AVX-512**. A differenza di PyTorch, quel binario **non** fa
  rilevamento delle feature CPU a runtime: se la CPU della macchina target non ha
  quelle estensioni, la prima istruzione AVX incontrata durante il load del
  modello causa `STATUS_ILLEGAL_INSTRUCTION` → crash secco. In Docker non capita
  perché lì `llama-cpp-python` viene **compilato dal sorgente** e si adatta alla
  CPU dell'host. Sulla macchina di build (che ha AVX2) l'errore è invisibile.
- **Perché serviva una soluzione "globale":** è una release retail/mass-market,
  deve girare su **qualsiasi** CPU Windows x64, non solo su quelle con AVX2.
- **Fix — compilazione da sorgente in modalità BASELINE (nessun AVX):**
  invece di scaricare la wheel, `build_runtime.py` ora **compila
  `llama-cpp-python` dal sorgente** con un toolchain C/C++ portatile e flag che
  disattivano tutte le estensioni SIMD avanzate. Il binario prodotto usa solo il
  baseline x86-64 di ggml (**SSE4.2 + BMI2**, presente su Intel Haswell 2013+ e
  tutte le AMD Zen), quindi niente più istruzioni AVX → niente più crash.
  1. **Toolchain portatile (winlibs, MinGW-w64 14 UCRT / GCC 16).** Scaricato
     come **`.zip` puro** ed estratto con Python (`ensure_mingw()`): nessun `.exe`
     da eseguire → compatibile con l'antivirus dell'utente. Header mingw-w64
     recenti necessari a ggml (es. `THREAD_POWER_THROTTLING_STATE`, assente nelle
     mingw vecchie). → `scripts/build_runtime.py` (`MINGW_URL`, `ensure_mingw`)
  2. **Flag CMake baseline** passati via `CMAKE_ARGS` (`build_llama_cpp()`):
     `-DGGML_NATIVE=OFF -DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_AVX512=OFF`
     `-DGGML_FMA=OFF -DGGML_F16C=OFF -DGGML_OPENMP=OFF`
     + compilatori `gcc`/`g++` con **path assoluto** (CMake lo pretende).
  3. **Target Windows 10** (`-D_WIN32_WINNT=0x0A00`): MinGW punta di default a
     Windows 7 e `cpp-httplib` di llama.cpp non compila (`CreateFile2`,
     `#error "...Windows 10 or later"`). L'app è comunque Win10+.
  4. **Niente `-static` globale:** su MinGW rompe l'unwinding SEH nelle DLL
     (`multiple definition of _Unwind_Resume`). Si linka dinamico e si **copiano
     le 3 DLL runtime MinGW** accanto a `llama.dll` (`copy_mingw_runtime()`):
     `libgcc_s_seh-1.dll`, `libstdc++-6.dll`, `libwinpthread-1.dll`. Windows le
     risolve dalla cartella della DLL caricata via ctypes → self-contained.
  5. Build via pip: `pip install --no-binary llama-cpp-python --no-build-isolation
     llama-cpp-python==0.3.32` con `CMAKE_GENERATOR=Ninja`.
  - → `scripts/build_runtime.py`
- **Garanzia verificabile in build (non solo "fidati dei flag"):**
  `verify_runtime.py` disassembla ogni `ggml*.dll` con `objdump -d` e **fallisce
  il build** se trova registri `ymm`/`zmm` (= istruzioni AVX/AVX2/AVX512). Esito
  attuale: *"3 DLL ggml, nessuna istruzione AVX"*. Poiché il binario baseline è
  **identico** su ogni PC, ciò che passa in build vale su qualsiasi CPU.
  → `scripts/verify_runtime.py` (`check_llama_baseline`)
- **✅ COLLAUDATO SUL CAMPO (2026-07-04, mini PC dell'utente):** installato il
  nuovo `Qwibo-Setup-0.1.0-alpha.1.exe`, eseguito un riassunto locale su una
  trascrizione EN di ~4 min. Log mini PC: *"Caricamento LLM locale
  qwen2.5-3b-instruct-q4_k_m.gguf (CPU, 15 thread)..."* → **nessun crash**
  (prima moriva qui con `0xC000001D`), backend vivo, **riassunto generato
  correttamente**. Fix confermato su hardware reale.
- **Nota compatibilità CPU:** il floor è **SSE4.2 + BMI2** (baseline x86-64 di
  ggml, non ulteriormente abbassabile senza patchare upstream). Copre di fatto
  tutti i PC Windows moderni; CPU pre-2013 (Bay Trail/Atom senza BMI2) restano
  fuori, ma non sono target realistici per un LLM locale.


Tutti e tre invisibili sulla macchina di sviluppo (lì i path/DLL esistono),
visibili solo installando su un secondo PC.

### B1 — Runtime non relocabile (venv invece di standalone)
- **Sintomo:** `No Python at 'C:\...\build\python-standalone\python.exe'` già al
  wizard/download modelli. Il python non parte affatto.
- **Causa:** `build/runtime-venv` era un **venv** con `pyvenv.cfg` contenente
  path assoluti (`home`/`executable`) alla macchina di build. Un venv referenzia
  l'interprete base per path assoluto → su un altro PC non esiste.
- **Fix:** `build_runtime.py` scarica **python-build-standalone** (relocabile,
  `python.exe` nella root, niente `pyvenv.cfg`) e fa `force_remove` del runtime
  prima di ricrearlo. → `scripts/build_runtime.py`

### B2 — Install editable di `qwibo` (path assoluto nel .pth)
- **Sintomo:** anche con python ok, il server FastAPI non parte → timeout avvio.
- **Causa:** in `site-packages` c'era `__editable__.qwibo...pth` col path
  assoluto `...\backend\vendor`. `launch_ui()` avvia **uvicorn come nuovo
  processo** che non eredita il `sys.path` di `entrypoint.py`, quindi importava
  `qwibo` solo dal .pth → `ImportError` sul PC utente.
- **Fix (2 livelli):**
  1. `pip install <backend>` **non-editable** → `qwibo` copiato davvero in
     site-packages. `validate_runtime()`/`verify_runtime.py` bloccano il build
     se trovano `__editable__*.pth`. → `scripts/build_runtime.py`
  2. Difesa in profondità: `PYTHONPATH=<vendor>` nell'env dei sottoprocessi
     Python, così `qwibo` si carica dalla copia **spedita con l'app**
     (`resources/backend/vendor`) indipendentemente da site-packages.
     → `src/backend-spawn.js`, `src/model-setup.js`

### B4 — Crash encoding cp1252 su stdout Windows (trovato col collaudo su PC reale)
- **Sintomo:** backend esce con `code=1` all'avvio, l'app resta appesa e si chiude
  da sola. Log: `UnicodeEncodeError: 'charmap' codec can't encode character
  '→'` a `entrypoint.py:45` (`print(f"...backend → http://...")`).
- **Causa:** con stdout **rediretto** (Electron usa pipe), Python su Windows usa
  la codifica legacy **cp1252**, non UTF-8. Caratteri fuori codepage (`→`, `—`,
  `≥`, usati in `entrypoint.py` e nei messaggi/JSON di `download_models.py`)
  mandano in crash il `print`. Invisibile in dev (lì lo stdout è UTF-8).
- **Fix (solo stdout, senza toccare la decodifica dei sottoprocessi):**
  1. Env `PYTHONIOENCODING=utf-8` impostato da Electron → forza UTF-8 solo su
     stdin/stdout/stderr di entrypoint, uvicorn, worker e download, su qualsiasi
     codepage. Viaggia nell'installer. → `src/backend-spawn.js`, `src/model-setup.js`
  2. In-code `sys.stdout/stderr.reconfigure(encoding="utf-8", errors="replace")`
     → rete di sicurezza. → `backend/entrypoint.py`, `backend/download_models.py`
- **ATTENZIONE — perché NON `PYTHONUTF8=1`:** un primo tentativo usava
  `PYTHONUTF8=1`, ma quello cambia *anche* la decodifica dell'output dei
  sottoprocessi da locale a UTF-8. Su Windows italiano l'output di `tasklist`
  (codepage OEM, byte `0x85`) andava in `UnicodeDecodeError` → `result.stdout=None`
  → `TypeError` in `_pid_running` → crash del server in loop all'avvio. Idem
  `ffprobe`. Quindi si usa **solo** `PYTHONIOENCODING`.
- **Hardening correlato:** `_pid_running` (tasklist) e `get_duration_sec`
  (ffprobe JSON UTF-8) ora specificano encoding/`errors="replace"` e non possono
  più far crashare la decodifica. → `worker.py`, `extract.py` (vendor + `src/`)

### B5 — Trascrizione piantata al 15% (cache numba in Program Files) — diagnosi py-spy
- **Sintomo:** la trascrizione restava bloccata a "Caricamento modello NeMo... 15%"
  a tempo indefinito (>15 min), senza errori nei log. In Docker (Linux) lo stesso
  caricava in ~2 min sullo stesso mini PC → non è CPU vs GPU.
- **Diagnosi (stack del worker vivo con py-spy):**
  ```
  ensure_cache_path (numba/core/caching.py:112) → NamedTemporaryFile → _mkstemp_inner  (bloccato)
  <module> (librosa/core/notation.py)   ← librosa usa numba @jit(cache=True)
  __init__ (nemo/.../audio_preprocessing.py:272)
  restore_from → _get_model (transcribe.py:66)
  ```
- **Causa:** NeMo → librosa → numba scrive la cache JIT accanto ai propri file, in
  `C:\Program Files\...\site-packages` (**sola lettura**). Su Windows
  `os.access(dir, W_OK)` riporta erroneamente "scrivibile" → `tempfile` riprova
  fino a 10.000 volte creando file (ognuno fallisce/scansionato da Defender) →
  hang di minuti. Su Linux/Docker la dir è scrivibile → nessun problema.
- **Fix:** `NUMBA_CACHE_DIR` e `MPLCONFIGDIR` puntati a cartelle scrivibili sotto
  `%APPDATA%\qwibo-desktop\cache\`. Verificato: la funzione che si piantava
  (`librosa.filters.mel`) ora completa in ~4 s. → `src/backend-spawn.js`

### B3 — DLL Visual C++ / OpenMP mancanti (riassunto locale) — ⚠️ SUPERATO da B6
- **Sintomo:** `import llama_cpp` fallisce con *"DLL load failed"* su PC senza
  VC++ Redistributable → riassunto locale rotto.
- **Causa:** la wheel MSVC precompilata produceva `llama.dll`/`ggml*.dll`
  dipendenti da `msvcp140.dll`/`vcomp140.dll` (runtime C++/OpenMP), non presenti
  in un Windows base. Sulla macchina di build sono in `System32` → mascherato.
- **Fix storico:** `bundle_msvc_runtime()` copiava le DLL VC++ in `llama_cpp/lib/`.
- **⚠️ Ora NON più necessario:** con B6 `llama.dll` è **compilato con MinGW**, non
  dipende più dal runtime MSVC. Le sue dipendenze (`libgcc_s_seh-1.dll`,
  `libstdc++-6.dll`, `libwinpthread-1.dll`) sono copiate da `copy_mingw_runtime()`
  e `GGML_OPENMP=OFF` elimina del tutto la dipendenza da OpenMP. La chiamata a
  `bundle_msvc_runtime()` è stata rimossa da `main()` (la funzione resta nel file
  ma inutilizzata). → `scripts/build_runtime.py`

---

## 🛠️ Build & packaging

### F1 — Strategia pip robusta in `build_runtime.py`
- `PYTHONNOUSERSITE=1` (no contaminazione dai pacchetti del profilo utente).
- 3 stadi in ordine:
  1. **Bootstrap** di `pip/setuptools/wheel/scikit-build-core/cmake/ninja`
     (build-deps per compilare llama da sorgente).
  2. **`llama-cpp-python` compilato da sorgente baseline** (vedi **B6**): non più
     wheel precompilata `abetlen.github.io` (causava il crash AVX `0xC000001D`).
  3. **Backend non-editable** (`--no-build-isolation`); `llama-cpp-python` è già
     soddisfatto dallo stadio 2, non viene ricompilato.
- `--extra-index-url` PyTorch CPU + `--trusted-host` per reti con TLS intercept.
- Retry ×3 su ogni step pip (`_pip_retry`).
- → `scripts/build_runtime.py`

### F2 — `check-build.js` (gate predist)
- Accetta `python.exe` in root **o** in `Scripts/`.
- **Blocca** il build se trova `pyvenv.cfg` (runtime venv non relocabile), con
  messaggio esplicito.
- → `scripts/check-build.js`

### F3 — `verify_runtime.py` (gate fast build)
- Rimossa l'euristica `"hp\\Documents"` che dava **falso positivo** (il repo
  *sta* sotto quel path → falliva anche un runtime corretto).
- Ora verifica invarianti reali: no `pyvenv.cfg`, `python.exe` in root, no
  `__editable__*.pth`, import deps (`torch/fastapi/uvicorn/nemo`) + import
  `qwibo` da vendor con `PYTHONPATH`.
- **Gate CPU-compat (B6):** `check_llama_baseline()` disassembla i `ggml*.dll`
  con `objdump` e fallisce se trova istruzioni AVX (registri `ymm`/`zmm`);
  `check_llama_load()` carica un GGUF reale se presente (smoke test end-to-end).
- → `scripts/verify_runtime.py`

### F4 — `build_installer.bat`
- Esegue `verify_runtime.py` dopo la fast build.
- `ICON_PY` prova prima `runtime-venv\python.exe` (root, standalone) poi
  `Scripts\python.exe`.
- → `build_installer.bat`

---

## 🧩 Robustezza runtime

### R1 — `PYTHONPATH=<vendor>` per i sottoprocessi
- `launch_ui()` avvia uvicorn/worker come nuovi processi: senza `PYTHONPATH`
  non troverebbero `qwibo`. Impostato su vendor bundlato.
- → `src/backend-spawn.js` (`startBackend`), `src/model-setup.js` (`buildDownloadEnv`)

### R2 — `entrypoint.py` aggiunge `vendor` a `sys.path`
- Il processo padre importa `qwibo` dal vendor bundlato.
- → `backend/entrypoint.py`

### R3 — Download Qwen non-bloccante
- Il fallimento del modello di **riassunto locale** non impedisce più l'avvio:
  solo l'ASR (Parakeet) è obbligatorio. Se Qwen non si scarica, l'app parte e si
  usano le API cloud (evento `skip`, non `error`).
- → `backend/download_models.py`

### R4 — Barra Qwen bloccata a 0% (sembrava non scaricare)
- **Sintomo:** durante il wizard, il modello Qwen restava a **0%** e sembrava
  bloccato, mentre l'ASR mostrava il progresso correttamente.
- **Causa:** ASR usa `curl -o <file finale>` (la barra vede crescere i byte),
  Qwen usava `hf_hub_download` che scrive in un file temporaneo nascosto
  (`.cache/huggingface/download/*.incomplete`) e sposta nel file finale **solo
  alla fine** → il poll leggeva 0 byte fino all'ultimo istante. Il download
  avveniva davvero, ma sembrava fermo.
- **Fix:** Qwen scaricato con `curl` diretto al file finale (come l'ASR):
  progresso reale, resume (`-C -`), niente più dipendenza da `hf_hub`/`hf_xet`.
  Verificato: 66 MB scritti nel file finale in 3 s.
  → `backend/download_models.py`

---

## 🎨 Icone

### I1 — Icona Electron di default invece di Qwibo
- **Sintomo:** collegamento desktop/exe e finestra/taskbar mostravano l'icona
  di Electron, non quella del progetto.
- **Cause e fix:**
  1. `package.json` aveva `"signAndEditExecutable": false` → electron-builder
     **non modificava l'exe**, quindi non applicava l'icona `assets/icon.ico`.
     Rimosso (default = editing attivo; la firma resta saltata perché non c'è
     certificato). → `package.json`
  2. Le finestre non impostavano `icon:` → mentre l'app gira, finestra e taskbar
     mostravano Electron. Aggiunto `icon: assets/icon.ico` alla finestra
     principale e a quella del wizard. → `src/main.js`, `src/model-setup.js`
- `assets/icon.ico` è già multi-risoluzione (16→256px), quindi valido.
- **Nota:** su un PC che aveva la vecchia versione, il collegamento potrebbe
  restare cachato da Windows; una nuova installazione o il refresh cache icone
  lo aggiorna.

## 🔎 Qualità & diagnostica

### Q1 — Rimossa dipendenza npm `get-port`
- Sostituita da `src/find-port.js` locale (niente pacchetto ESM-only runtime;
  `dependencies: {}`).
- → `src/main.js`, `src/find-port.js`, `package.json`

### Q2 — Logging diagnostico
- `src/logger.js`: log su `%APPDATA%\qwibo-desktop\logs\`, cattura
  `console.*`, `uncaughtException`, `unhandledRejection`.
- `main.js`: dialoghi d'errore con path del log + voce tray **"Apri cartella log"**.
- → `src/logger.js`, `src/main.js`

---

## ✅ Stato attuale

- Rebuild completo → runtime **standalone relocabile, non-editable** (verificato:
  `python.exe` in root, no `pyvenv.cfg`, no `__editable__*.pth`, `qwibo`
  reale in site-packages).
- **`llama-cpp-python` compilato da sorgente baseline (no AVX)** con winlibs MinGW:
  `verify_runtime.py` conferma *"3 DLL ggml, nessuna istruzione AVX"* + import ok.
  Runtime MinGW (`libgcc_s_seh-1`, `libstdc++-6`, `libwinpthread-1`) copiato in
  `llama_cpp/lib/`. DLL MSVC residue rimosse.
- `check-build.js` (predist) passa; `verify_runtime.py` passa.
- Packaging installer (`npm run dist:win`) → `release/Qwibo-Setup-0.1.0-alpha.1.exe`.

## ⏭️ Da fare

1. ~~Collaudo su PC pulito~~ ✅ **FATTO** (2026-07-04): riassunto locale generato
   sul mini PC senza crash `0xC000001D`. B6 confermato.
2. Non usare `build_installer.bat fast` finché non esiste un runtime standalone
   pulito da build completa.
3. (Opzionale, pulizia) Rimuovere dal runtime i tool solo-build (`cmake`, `ninja`,
   `scikit-build-core`) dopo la compilazione di llama, per snellire l'installer
   (~150 MB in meno; solo estetica/peso, non funzionale).

## 📌 Note non-bloccanti (roadmap)

- Installer **non firmato** → avviso SmartScreen / possibile allarme antivirus
  (code signing Authenticode previsto v0.2).
- Finestra di setup non chiusa esplicitamente nel path d'errore (cosmetico;
  l'app si chiude comunque mostrando il dialogo d'errore).
- Doppia copia di `qwibo` (vendor spedito + site-packages): con
  `PYTHONPATH=vendor` la copia vendor è autoritativa; site-packages resta solo
  per le dipendenze. Ridondanza innocua.
