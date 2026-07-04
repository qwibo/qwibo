# Dove ospitare la prima release (alpha) — Hosting & Distribuzione

Documento decisionale per pubblicare `Qwibo-Setup-0.1.0-alpha.1.exe`
(~662 MB) proteggendo il codice e servendo il download in modo rapido e
affidabile.

Aggiornato: 2026-07-04 · Stadio: **alpha**.

---

## 0. TL;DR (la raccomandazione)

Per l'**alpha**, la combinazione migliore costo/velocità/protezione è:

1. **Sorgente → repo GitHub PRIVATO.** Rendi privato l'attuale repo pubblico
   `qwibo` (protezione legale + rimuove la navigazione casuale del codice).
2. **Binario (installer) → GitHub Releases su un repo PUBBLICO separato**
   (es. `qwibo-releases`, senza codice) *oppure* **Cloudflare R2** con
   dominio custom. Entrambi: CDN veloce, gratis o quasi, link diretto.
3. **Pagina di download → il sito già esistente `qwibo.github.io`**
   con un bottone "Scarica per Windows" che punta al binario.
4. **Accetta (per ora) che il backend Python spedito sia leggibile** — vedi §4.
   Non sovra-investire in offuscamento all'alpha.

> Regola d'oro: **codice sorgente e file scaricabile sono due cose separate.**
> Puoi tenere il codice privato e distribuire comunque un binario pubblico.

---

## 1. Requisito: proteggere/oscurare il codice

### Situazione attuale
- Il repo `qwibo` è **pubblico** su GitHub.
- La licenza è già **proprietaria** (`LICENSE`: "All rights reserved",
  Antonio Trento) → chi copia il codice viola la licenza. Protezione *legale*
  già presente; manca la protezione *tecnica* (nasconderlo).

### Cosa fare
1. **Rendi il repo privato** (Settings → Danger Zone → Change visibility →
   Private). Immediato, gratis, reversibile. Nasconde: codice, cronologia
   commit, script di build, issue.
2. **Sposta la distribuzione dei binari** fuori dal repo sorgente (vedi §2).

### ⚠️ Verità tecnica importante (da sapere)
L'app è **Electron + Python**: l'installer contiene i sorgenti Python **in
chiaro** dentro `resources/backend/vendor/qwibo/*.py` e l'intero
`resources/runtime-venv`. Chiunque può aprire l'installer con 7-Zip e **leggere
quel codice**, anche se il repo GitHub è privato.

Quindi "repo privato" protegge il *progetto* (build scripts, storia, tutto), ma
**non** nasconde il codice che viaggia nell'installer.

Se e quando vorrai nascondere *anche* quello (non necessario all'alpha):

| Tecnica | Efficacia | Costo/rischio |
|---|---|---|
| Spedire solo `.pyc` (bytecode) | Bassa (decompilabile) | Basso |
| **PyArmor** (offusca il pacchetto `qwibo`) | Media | Medio: può rompere import dinamici |
| **Nuitka** (compila Python → binario nativo) | Alta | Alto: complesso con torch/NeMo/llama |

**Consiglio:** all'alpha lascia stare. Il valore vero del prodotto è nel
packaging, nella UX e nell'integrazione (ASR locale + LLM + multilingua), non
nelle poche centinaia di righe di "colla" Python, che comunque sono coperte
dalla licenza proprietaria. Rivaluta a 1.0 se emergono cloni.

---

## 2. Requisito: servire il download rapidamente

### Opzioni a confronto

| Host | Costo | Velocità (CDN) | Limite file | Pro | Contro |
|---|---|---|---|---|---|
| **GitHub Releases** (repo pubblico) | Gratis (fair use) | Sì (CDN) | 2 GB/file | Zero setup, versionato, supporta auto-update | "Fair use" non contrattuale; niente dominio custom |
| **Cloudflare R2** | ~0,015 $/GB-mese storage, **egress gratis** | Sì | Enorme | Nessun costo di banda, dominio custom, S3-compatibile | Richiede setup (bucket + dominio) |
| **Backblaze B2 + Cloudflare** | Storage economico, egress gratis (Bandwidth Alliance) | Sì | Enorme | Molto economico | Setup |
| Server VPS proprio | Fisso mensile | No (a meno di CDN) | — | Controllo totale | Banda 662 MB × download = costosa/lenta |
| Google Drive / Dropbox link | Gratis-ish | Media | — | Zero setup | Link brutti, throttling, aspetto poco pro |

### Raccomandazione
- **Semplice e subito:** GitHub Releases su repo pubblico `qwibo-releases`
  (contiene solo i binari + note di versione, **nessun sorgente**).
- **Più "pro" e scalabile:** Cloudflare R2 con dominio custom
  (es. `download.qwibo.<tld>` o un path sul dominio del sito).

### Dettagli pratici
- Pubblica **sempre** accanto all'installer:
  - `SHA256` del file (integrità/anti-manomissione),
  - le **note di versione** (changelog),
  - il file `.blockmap` generato da electron-builder (serve agli update delta).
- 662 MB è grande: valuta di indicare la dimensione sul bottone di download
  ("Scarica · 662 MB") per gestire le aspettative.

---

## 3. Altri fattori (che non avevi elencato ma contano)

### 3.1 Firma del codice (Authenticode) — il fattore #1 per l'adozione
- **Ora l'installer NON è firmato** → Windows SmartScreen mostra
  *"Windows ha protetto il PC"* e molti utenti si spaventano/abbandonano.
- Opzioni:
  | Soluzione | Costo/anno | Note |
  |---|---|---|
  | **Azure Trusted Signing** | ~10 $/mese | La più economica; richiede identità verificata. Ottima per indie. |
  | Certificato **OV** (Sectigo/DigiCert) | ~200-400 € | Da giugno 2023 richiede token hardware/HSM cloud. Reputazione SmartScreen si costruisce nel tempo. |
  | Certificato **EV** | ~300-600 € | Reputazione SmartScreen **immediata**. Token hardware obbligatorio. |
- **All'alpha** puoi rimandare, ma metti istruzioni chiare ("clicca *Ulteriori
  informazioni → Esegui comunque*"). Per la **beta/1.0** la firma è quasi
  obbligatoria per il mass market.

### 3.2 Falsi positivi antivirus
- App non firmata + Python + DLL native compilate (llama) → possibili allarmi.
- Mitigazioni: firma del codice, invio a **VirusTotal** prima del lancio,
  eventuale whitelisting presso i vendor AV, checksum pubblico.

### 3.3 Aggiornamenti automatici
- `electron-updater` può leggere gli update da **GitHub Releases** o da un
  server generico (R2/S3) tramite `latest.yml` + `.blockmap` (update **delta**:
  scarica solo le differenze, non 662 MB ogni volta).
- Conviene predisporlo presto: aggiornare gli alpha-tester senza fargli
  riscaricare tutto è oro.

### 3.4 Licenza d'uso per l'utente finale (EULA)
- `desktop-electron/package.json` ha `"license": "UNLICENSED"`. Definisci una
  **EULA** breve mostrata dall'installer NSIS (già supporta la pagina licenza).
- Coerenza con `LICENSE` proprietaria del repo.

### 3.5 Privacy & telemetria
- Punto di forza del prodotto = **tutto in locale, niente cloud**. Se aggiungi
  telemetria (crash report, contatore installazioni), rendila **opt-in** e
  dichiarata, altrimenti tradisci la promessa di privacy.

### 3.6 Landing page & fiducia
- Usa `qwibo.github.io` come vetrina: cosa fa, screenshot, requisiti
  (Windows 10/11 64-bit, CPU SSE4.2+BMI2, ~consigliati 16 GB RAM), bottone
  download, checksum, changelog, nota "alpha / non firmato".

---

## 4. Checklist di pubblicazione (alpha)

- [ ] Repo sorgente reso **privato**.
- [ ] Creato repo/bucket pubblico per i **binari** (GitHub Releases o R2).
- [ ] Caricato `Qwibo-Setup-0.1.0-alpha.1.exe` + `.blockmap`.
- [ ] Pubblicato **SHA256** dell'installer.
- [ ] Scritte le **note di versione** (cosa funziona, cosa no, requisiti CPU).
- [ ] Landing page con bottone download + avviso "alpha, non firmato".
- [ ] (Opzionale) Inviato a VirusTotal, allegato l'esito.
- [ ] (Consigliato a breve) Predisposto `electron-updater`.
- [ ] (Beta/1.0) Attivata la **firma del codice**.

---

## 5. Come generare lo SHA256 (per le note di rilascio)

Su Windows PowerShell, nella cartella `desktop-electron/release`:

```powershell
Get-FileHash .\Qwibo-Setup-0.1.0-alpha.1.exe -Algorithm SHA256
```
