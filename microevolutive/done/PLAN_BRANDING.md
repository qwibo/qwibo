# Piano microevolutivo — Branding & nome prodotto

> **Data**: 2026-07-04 · **Stato**: ✅ NOME SCELTO — **Qwibo**
> **Obiettivo**: trovare un nome brand internazionale, distintivo e **libero**,
> con cui rimpiazzare "Sbobinator".
> **Timing:** l'alpha è **il momento più economico** per cambiare nome (poche
> installazioni, SEO da costruire, nessun utente da confondere).

---

## ✅ DECISIONE FINALE (2026-07-04): **Qwibo**

- **Nome ufficiale: `Qwibo`** (pronuncia: *KWEE-bo*).
- **Org GitHub `qwibo`: LIBERA** → sito su **`qwibo.github.io`** (gratis).
- **Categoria pulita**: nessun concorrente nel settore trascrizione/voce.
  Unico omonimo = una piccola app Shopify per QuickBooks (classe contabilità →
  settore diverso, nessun conflitto reale).
- **Astratto/brandabile**: nessun significato che incastri il prodotto; facile
  da rendere unico e riconoscibile.
- **Nota grafica**: la "Qw" è insolita → può essere un tratto distintivo (tipo
  "Qwerty"); in comunicazione conviene rinforzare la pronuncia le prime volte.
- Alternative scartate all'ultimo giro: **Virea** e **Miralo** (categoria pulita
  ma **org GitHub già occupate**).

> Prossimo: eseguire il **piano di rebrand in fasi** (§7–§9).

---

## 7. Architettura org GitHub — 3 repository

**Sì, la distribuzione ti torna.** È pulita, standard per GitHub Pages, e separa i tre "prodotti" con cicli di vita diversi.

| # | Repo consigliato | URL sito / ruolo | Cosa contiene |
|---|---|---|---|
| 1 | **`qwibo/qwibo`** | — | **App desktop Electron** (prodotto retail): `desktop-electron/`, backend Python (`src/`), script build/runtime, asset, installer. È il **repo principale** (source of truth del codice). |
| 2 | **`qwibo/qwibo-docker`** | — | **Deploy self-hosted** (mini PC, server casa, NAS): `Dockerfile`, `docker-compose.yml`, istruzioni. Builda l'immagine dal backend incluso nel repo. |
| 3 | **`qwibo/qwibo.github.io`** | **https://qwibo.github.io** | **Sito marketing** (Jekyll/static): landing, download, changelog, privacy, FAQ. Nome **obbligatorio** così per GitHub Pages org. |

### Perché questa suddivisione funziona

- **Desktop** e **Docker** condividono lo stesso backend Python ma hanno **packaging diverso** (installer NSIS vs container) → repo separati evitano confusione nelle release.
- Il **sito** ha ciclo proprio (testi marketing, screenshot, download link) senza rebuild dell'app.
- **Costo zero**: tutto su GitHub gratis (`qwibo.github.io` incluso).

### Cosa NON va in questi 3 repo

| Contenuto | Dove metterlo |
|---|---|
| Documentazione tecnica lunga (MkDocs) | Dentro `qwibo/qwibo` in `docs/` **oppure** sezione `/docs` sul sito `qwibo.github.io` |
| Release binarie (installer `.exe`) | **GitHub Releases** su `qwibo/qwibo` (o repo `qwibo/releases` dedicato solo binari — opzionale, non necessario all'alpha) |
| Lead generation API (Raspberry Pi) | **Fuori da GitHub** (self-hosted sul Pi) — vedi `PLAN_LEAD_GENERATION.md` |
| Repo vecchio `sbobinator` | Archiviato / privato dopo migrazione (redirect README → nuova org) |

### Nomi repo — raccomandazione finale

```
Org:     github.com/qwibo

Repo 1:  qwibo/qwibo              ← app desktop + backend (PRINCIPALE)
Repo 2:  qwibo/qwibo-docker       ← self-hosted Docker (+ mkdocs locale, non sul sito)
Repo 3:  qwibo/qwibo.github.io    ← sito (nome fisso per Pages)
```

**Alternative accettabili** (se preferisci più espliciti):
- `qwibo/desktop` al posto di `qwibo/qwibo` — più chiaro, ma perdi il repo "corto" `qwibo/qwibo` che è bello come brand.
- `qwibo/self-hosted` al posto di `qwibo/docker` — più descrittivo per utenti non tecnici.

**Raccomandazione:** tieni `qwibo`, `docker`, `qwibo.github.io` — brevi, chiari, coerenti.

### Legame tra `qwibo` e `docker`

Il repo `docker` non duplica tutto il codice. Opzioni (scegliere una in Fase 1):

1. **Git submodule** — `docker` include `qwibo` come submodule in `backend/`; `docker-compose` builda da lì. *(Consigliata: aggiornamenti backend = un submodule bump.)*
2. **Build da release** — `Dockerfile` scarica tarball/tag da `qwibo/qwibo` Releases. *(Più semplice per utenti finali, meno comodo in sviluppo.)*

---

## 8. Fase 2 — Rebrand applicazione (Sbobinator → Qwibo)

L'app **non può più chiamarsi Sbobinator** né mostrarlo da nessuna parte. Checklist completa.

### 8.1 Identità visiva e packaging

- [ ] `productName`: **Qwibo** (finestra, taskbar, installer)
- [ ] `appId`: `net.antoniotrento.qwibo.desktop` (era `...sbobinator...`)
- [ ] Installer: `Qwibo-Setup-0.1.0-alpha.1.exe` (era `Sbobinator-Setup-...`)
- [ ] Icona `.ico` / tray icon — nuovo logo Qwibo (o adattamento temporaneo del logo esistente)
- [ ] Cartelle utente: `%APPDATA%/Qwibo/` (era `Sbobinator/` — prevedere migrazione o coesistenza alpha)

### 8.2 Testi visibili all'utente

- [ ] Titolo finestra Electron, menu, dialoghi
- [ ] Wizard primo avvio / model setup (`setup/index.html`)
- [ ] UI web (FastAPI + HTMX) — header, titoli pagina, footer
- [ ] Messaggi errore e log user-facing
- [ ] EULA / licenza nel installer NSIS
- [ ] Stringhe "Sbobinator" in `README`, `WINDOWS-RELEASE-FIXES.md`, docs

### 8.3 Codice e configurazione (interno)

- [ ] `package.json`: `name`, `description`
- [ ] Variabili env: `SBOBINATOR_*` → `QWIBO_*` (con alias temporaneo per compatibilità se serve)
- [ ] Pacchetto Python `src/sbobinator/` → `src/qwibo/` (rename modulo + import)
- [ ] `pyproject.toml`, entrypoint CLI (`sbobina` → `qwibo` o mantieni comando `qwibo` come unico)
- [ ] Path log, SQLite DB, cartelle dati
- [ ] `build_runtime.py`, `verify_runtime.py`, script build

### 8.4 Definition of Done — rebrand app

- [x] `productName`: **Qwibo** (finestra, taskbar, installer)
- [x] `appId`: `net.antoniotrento.qwibo.desktop`
- [x] Installer: `Qwibo-Setup-0.1.0-alpha.1.exe`
- [ ] Icona `.ico` / tray icon — nuovo logo Qwibo (o adattamento temporaneo del logo esistente)
- [ ] Cartelle utente: `%APPDATA%/Qwibo/` (era `Sbobinator/` — prevedere migrazione o coesistenza alpha)
- [x] Titolo finestra Electron, menu, dialoghi
- [x] Wizard primo avvio / model setup (`setup/index.html`)
- [x] UI web (FastAPI + HTMX) — header, titoli pagina, footer
- [x] Messaggi errore e log user-facing (codice operativo)
- [ ] EULA / licenza nel installer NSIS
- [x] `package.json`: `name`, `description`
- [x] Variabili env: `QWIBO_*` (con fallback legacy `SBOBINATOR_*`)
- [x] Pacchetto Python `src/qwibo/` (rename modulo + import)
- [x] `pyproject.toml`, entrypoint CLI (`qwibo`)
- [ ] Path log desktop: `%APPDATA%\qwibo-desktop\` (nuovo; legacy `sbobinator-desktop` da migrare)
- [x] `build_runtime.py`, `verify_runtime.py`, script build (testi)
- [x] Docker: immagini `qwibo:cpu`/`qwibo:gpu`, servizi `qwibo-cpu`/`qwibo-gpu`, env `QWIBO_*`

**Stato repo attuale (2026-07-04):** rebrand codice operativo completato in `src/qwibo/`,
`docker/`, `desktop-electron/`, `scripts/`, `pyproject.toml`, `start.bat`, `.env.example`,
`README.md`. Restano: logo, migrazione cartelle utente, docs MkDocs, sito.

---

## 9. Fase 3 — UX: miglioramento sostanziale

**Stato attuale:** funziona, ma l'esperienza utente **non è ancora al livello retail** che vuoi (WinRAR moderno). Questa fase è **separata dal rebrand nominale** ma va pianificata subito dopo (o in parallelo al sito).

### 9.1 Problemi UX tipici da risolvere (alpha → beta)

| Area | Problema probabile | Obiettivo |
|---|---|---|
| **Primo avvio** | Download modelli, permessi, tempi lunghi senza feedback chiaro | Wizard guidato: cosa sta succedendo, quanto manca, cosa serve (RAM, spazio disco) |
| **Caricamento job** | Utente non capisce se sta elaborando o è bloccato | Progress bar reale, stato testuale ("Trascrizione 45%…", "Riassunto in corso…"), log collassabile |
| **Flusso principale** | Troppi passi o UI "da sviluppatore" (HTMX grezzo) | Flusso lineare: **carica audio → scegli lingua → avvia → leggi risultato** in pochi click |
| **Risultati** | Trascrizione e riassunto poco leggibili | Layout pulito, tipografia, copia/esporta (TXT, DOCX) evidente |
| **Errori** | Messaggi tecnici (exit code, traceback) | Messaggi umani + "cosa fare" (es. RAM insufficiente, modello mancante) |
| **Aspetto** | Estetica non coerente col brand Qwibo | Design system minimo: colori, font, spaziature, iconografia Qwibo |

### 9.2 Priorità suggerite (ordine di impatto)

1. **Feedback durante elaborazione** — l'utente alpha ha già chiesto "sta elaborando o no?"; va risolto in modo definitivo.
2. **Wizard primo avvio** — modelli, licenza, (futuro) opt-in email lead gen.
3. **Schermata job/risultato** — la parte che l'utente usa ogni giorno.
4. **Pulizia visiva globale** — CSS, layout, rimozione elementi debug.

### 9.3 Definition of Done — UX beta-ready

- [ ] Un utente non tecnico completa trascrizione+riassunto **senza istruzioni esterne**
- [ ] Durante elaborazione lunga, sempre visibile **stato + progresso** (mai schermo "fermo" senza spiegazione)
- [ ] Primo avvio completato in **< 5 minuti** con messaggi chiari (anche se download modelli richiede più tempo, il wizard spiega)
- [ ] Screenshot del flusso principale utilizzabili sul sito `qwibo.github.io` senza vergogna

> Dettaglio implementativo UX: promuovere a `PLAN_UX_DESKTOP.md` quando si apre lo sprint dedicato.

---

## 10. Piano di rebrand — fasi e ordine

```
Fase 0 — Setup org          Creare org qwibo + 3 repo vuoti
     ↓
Fase 1 — Migrazione codice  Spostare codice nei repo giusti (qwibo, docker, sito)
     ↓
Fase 2 — Rebrand app        Sbobinator → Qwibo ovunque (§8)
     ↓
Fase 3 — UX                 Miglioramento esperienza utente (§9)
     ↓
Fase 4 — Sito live          qwibo.github.io con download + changelog
     ↓
Fase 5 — Release alpha      Qwibo-Setup-*.exe su GitHub Releases
```

### Fase 0 — Setup org GitHub
- [ ] Creare org **`qwibo`**
- [ ] Creare repo **`qwibo`**, **`docker`**, **`qwibo.github.io`**
- [ ] Abilitare GitHub Pages su `qwibo.github.io` (branch `main`, root o `/docs`)

**DoD:** i 3 repo esistono; Pages risponde (anche pagina placeholder).

### Fase 1 — Migrazione codice
- [ ] **`qwibo/qwibo`**: da repo attuale → `desktop-electron/`, `src/`, `scripts/`, `requirements/`, `assets/`, `docs/` tecnici
- [ ] **`qwibo/docker`**: da `docker/` + README deploy; submodule o istruzioni build verso `qwibo`
- [ ] **`qwibo/qwibo.github.io`**: da `sbobinator.github.io` → rebrand testi, logo, link download
- [ ] Repo vecchio `sbobinator`: README con redirect "Progetto rinominato → Qwibo" + link org; poi **archiviare** o rendere privato

**DoD:** push sui 3 repo; clone fresco permette build desktop e `docker compose up`.

### Fase 2 — Rebrand applicazione
- [ ] Eseguire checklist §8
- [ ] Rebuild installer `Qwibo-Setup-0.1.0-alpha.1.exe`
- [ ] Field test su mini PC

**DoD:** checklist §8.4 tutta spuntata.

### Fase 3 — UX
- [ ] Eseguire priorità §9.2 (almeno punti 1–3 per alpha pubblica)
- [ ] Screenshot aggiornati per il sito

**DoD:** checklist §9.3 (almeno i primi 3 punti per soft-launch).

### Fase 4 — Sito live
- [ ] Landing Qwibo: cosa fa, screenshot, requisiti, bottone download
- [ ] Link a GitHub Releases + SHA256 installer
- [ ] Nota "alpha", SmartScreen non firmato
- [ ] Privacy policy aggiornata (Qwibo, non Sbobinator)

**DoD:** `https://qwibo.github.io` pronto per condividere sui canali marketing.

### Fase 5 — Release alpha pubblica
- [ ] Tag `v0.1.0-alpha.1` su `qwibo/qwibo`
- [ ] Upload installer su Releases
- [ ] Soft-launch (vedi `strategia-release/02-MARKETING-E-LANCIO.md`)

**DoD:** link download funzionante da sito; alpha installabile su PC pulito.

---

## 11. Cosa resta del vecchio nome

- **"Sbobinator"** nel repo archiviato: solo come nota storica / redirect.
- Opzionale per mercato IT: una riga sul sito tipo *"Conosciuto in Italia anche come evoluzione del progetto Sbobinator"* — **non** come brand ufficiale.
- Comando CLI storico `sbobina`: valutare alias `qwibo` come comando principale; deprecare `sbobina` dopo beta.

---

## Migrazione (sintesi — sostituita da §7–§10)

Vedi sezioni **§7** (architettura repo), **§8** (rebrand app), **§9** (UX), **§10** (fasi).

## ⛔ Vincoli (fissati dall'autore, 2026-07-04)

1. **Zero soldi**: **NON si compra alcun dominio** (`.com`/`.app`/altro). Troppi
   domini comprati in passato per prodotti falliti. Qui si investe **solo tempo**.
2. **Sito e brand = `<nome>.github.io`** (GitHub Pages gratuito).
3. **Conseguenza diretta:** il nome scelto **deve essere disponibile come
   org/username GitHub** (perché l'URL del sito è `nome.github.io`). Questo è il
   **filtro numero uno**.
4. Deve inoltre **non collidere** con app della stessa categoria (trascrizione/
   voce) su App Store / Play Store / marchi, per evitare confusione e C&D.

---

## 🔴 Esito ricerca (2026-07-04): TUTTI i candidati bocciati

I nomi valutati finora sono **scartati**: o non liberi su GitHub, o in conflitto
con prodotti identici.

| Nome | Esito | Motivo |
|---|---|---|
| **Offscribe** | ⛔ Bocciato | Esiste già **"OffScribe"** (GiganTech, LLC) su App Store: **stesso identico prodotto** (trascrizione offline, privacy, multilingua), **gratis** con ads. Inoltre "Offscript" (Freeville) simile e **OFFSCRIPT, LLC** ha marchio USA. Categoria "off-scri*" affollata → confusione + SEO + rischio C&D. |
| **Vaultvoice** | ⛔ Bocciato | Esiste **"VaultVoice Recorder"** (App Store, registratore vocale privato) + **Verint VoiceVault** (biometria vocale, azienda affermata) + VoiceVault Ltd (India). Nome/categoria presidiati. |
| **PrivScribe** | ⛔ Bocciato | "Priv" abbreviazione gergale; percepito come tool di nicchia. |
| Scriba, Scribo, Notate, Verbatim | ⛔ | Troppo comuni / probabilmente non liberi su GitHub. |
| Voxa, Voxscribe, Echoscript, Sonora, Vocalis | ⛔ | Non disponibili su GitHub / nomi già in uso. |
| Quietscribe, Recanto, Quillo, Quill, Kribo, Skribo, Verba | ⛔ | Non disponibili su GitHub. |
| **Qwibo** | ✅ **Scelto** | Org GitHub libera; categoria pulita; unico omonimo = app Shopify contabilità (classe diversa). |

**Lezione appresa:** i nomi **descrittivi** (off/vault/voice/scribe/script) sono
proprio quelli che tutti usano in questo settore → sempre occupati o in
conflitto. Serve un nome **coniato/distintivo** (parola inventata), molto più
probabile che sia libero su GitHub e privo di gemelli.

---

## Perché rebrandizzare (contesto)

"Sbobinator" è **forte in Italia** (da *sbobinare*) ma **debole all'estero**:
opaco, difficile da pronunciare per anglofoni, "-ator" datato, SEO nulla fuori
dall'Italia. Per la visione *"un WinRAR moderno"* con adozione globale serve un
nome leggibile internazionalmente → **Qwibo**.
