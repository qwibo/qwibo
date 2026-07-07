# Piano microevolutivo — Lead Generation (raccolta email al primo avvio)

> **Data**: 2026-07-04 · **Stato**: 🔄 Fase 1–2 ✅ · Fase 3–4 da fare (app Electron)
> **Obiettivo**: costruire una base dati di utenti reali che installano l'app,
> raccogliendo **con consenso esplicito** l'email al primo avvio e archiviandola
> su un servizio FastAPI self-hosted (Raspberry Pi + Cloudflare Tunnel).
> **Server:** repository privato `qwibo-leads` (non in questo monorepo).
> **Segreti (token):** solo nel repo privato `qwibo-leads/secret/` — **non** in questo piano.
> **Uso:** feature indipendente dall'installer Qwibo.

---

## 0. Perché

Il prodotto è **gratuito e a codice aperto**: l'asset strategico che ti riservi è
la **relazione con gli utenti**. Una lista email di installatori attivi serve per:
- annunciare aggiornamenti (l'app all'alpha non è ancora firmata → riavvisare è
  prezioso),
- misurare l'adozione reale (quanti installano, con che OS/lingua/versione),
- costruire la leva verso il B2B ("le aziende parlano" → sapere chi ti usa),
- eventuale futura monetizzazione / versione Pro.

Visione di riferimento: *"un WinRAR moderno"* → grande adozione consumer, poi le
aziende arrivano. La lista è il ponte tra le due fasi.

---

## 1. Principio: opt-in trasparente e conforme (GDPR)

La raccolta è **facoltativa, chiara e conforme**. Gli utenti che arrivano al
primo avvio sono già motivati: con una buona proposta di valore il tasso di
iscrizione è alto **senza inganni**.

Requisiti di conformità (non negoziabili):
- **Consenso libero, specifico, informato, inequivocabile** → checkbox **NON**
  pre-spuntata, con testo esplicito.
- **Motivo concreto e onesto**: *"Ricevi una mail SOLO quando esce un
  aggiornamento importante o una correzione di sicurezza."*
- **Nessun dark pattern**: bottone primario "Tienimi aggiornato" e bottone
  secondario **visibile** "Salta per ora". Saltare deve essere facile.
- **Rassicurazione privacy**: *"Nessuno spam. Cancellazione con un click."* +
  link alla privacy.
- **Minimizzazione dati**: si salva solo ciò che serve; niente IP (o hashato).
- **Diritto all'opt-out**: link di cancellazione nelle email.

> Coerenza col posizionamento del prodotto ("privacy, tutto in locale"): la
> raccolta email è trasparente esattamente come il resto dell'app.

---

## 2. Dove intercettare l'utente

| Punto | Fattibilità | Note |
|---|---|---|
| Pagina custom nell'installer NSIS | ❌ complessa | Input+chiamata API async in NSIS è fragile; niente retry/offline. |
| **Modal al primo avvio dell'app** | ✅ consigliata | Facile in Electron, validazione, retry, offline-friendly, consenso GDPR pulito. |

**Decisione:** modal **al primo avvio** (non nell'installer). Più semplice, più
robusta e legalmente più solida.

---

## 3. Architettura

```
[App Electron]  --HTTPS POST /v1/leads-->  [Cloudflare Tunnel]  -->  [Raspberry Pi]
   modal primo avvio                          qwiboleads.antoniotrento.net    Docker :8080
   (email + consenso)                                                              + SQLite
```

| Componente | Stato (2026-07-05) |
|------------|-------------------|
| API + Docker sul Pi | ✅ |
| Tunnel HTTPS pubblico | ✅ `https://qwiboleads.antoniotrento.net` |
| Modal + client Electron | 📋 da implementare |

- **Client**: modal Electron → POST JSON all'endpoint. Se fallisce (offline,
  server giù) → **non blocca l'app**, salva in coda locale e ritenta al prossimo
  avvio.
- **Trasporto**: Cloudflare Tunnel (tunnel esistente sul Pi, ingress dedicato).
- **Server**: vedi README nel repository privato `qwibo-leads`.

---

## 4. Specifiche per l'app Electron (Fase 3–4)

> Implementazione in `desktop-electron/`. I **token non vanno committati** nel repo
> `qwibo` — si iniettano a build time o via config locale dev.

### 4.1 URL produzione

| Costante | Valore |
|----------|--------|
| Base URL API | `https://qwiboleads.antoniotrento.net` |
| Health check | `GET https://qwiboleads.antoniotrento.net/health` |
| Registrazione lead | `POST https://qwiboleads.antoniotrento.net/v1/leads` |

Nessun altro endpoint è richiesto dall'app in v1.

### 4.2 Configurazione app (nomi, non valori)

| Chiave | Dove | Note |
|--------|------|------|
| `LEADS_API_URL` | build / env Electron | Default: `https://qwiboleads.antoniotrento.net/v1/leads` |
| `LEADS_APP_TOKEN` | build / env Electron | Header `X-App-Token` — valore nel repo privato `qwibo-leads/secret/` |

**Build release:** token embedded nell'installer (accettato come anti-spam base; vedi §7).
**Dev locale:** file `.env` o variabile d'ambiente non committata.

### 4.3 `POST /v1/leads` — richiesta

**Headers obbligatori:**

```
Content-Type: application/json
X-App-Token: <LEADS_APP_TOKEN>
```

**Body JSON:**

| Campo | Tipo | Obbligatorio | Descrizione |
|-------|------|--------------|-------------|
| `email` | string | sì | Email valida (RFC) |
| `consent` | boolean | sì | Deve essere `true` (checkbox utente spuntata) |
| `install_id` | string | sì | UUID v4, generato al primo avvio, persistito |
| `app_version` | string | sì | Es. `0.1.0-alpha.1` da `package.json` |
| `os` | string | sì | Es. `win32-10.0.26200` (`process.platform` + release) |
| `locale
` | string | sì | Es. `it-IT` (`app.getLocale()`) |
| `source` | string | no | Default `"first-run-modal"` |
| `consent_text_ver` | string | no | Versione testo consenso mostrato (prova GDPR), es. `"2026-07"` |

**Esempio body (senza segreti):**

```json
{
  "email": "utente@example.com",
  "consent": true,
  "install_id": "550e8400-e29b-41d4-a716-446655440000",
  "app_version": "0.1.0-alpha.1",
  "os": "win32-10.0.26200",
  "locale": "it-IT",
  "source": "first-run-modal",
  "consent_text_ver": "2026-07"
}
```

### 4.4 `POST /v1/leads` — risposte

| HTTP | Body | Azione client |
|------|------|---------------|
| `201` | `{"ok": true}` | Successo — segna lead come inviato |
| `200` | `{"ok": true, "dup": true}` | Email/install già nota — tratta come successo |
| `401` | `{"detail": "..."}` | Token errato — log, non bloccare app; non ritentare all'infinito |
| `422` | validation error | Email non valida o `consent: false` — mostra errore in modal |
| `429` | rate limit | Ritenta più tardi (coda offline) |
| rete / timeout | — | Coda offline + retry (Fase 4) |

**Timeout consigliato:** 8–12 secondi. **Mai bloccare** l'avvio app se il POST fallisce.

### 4.5 Persistenza locale (Electron)

| File / chiave | Contenuto |
|---------------|-----------|
| `%APPDATA%/Qwibo/install_id` o in `preferences.json` | UUID v4, creato una volta |
| `leads_prompt_completed` | `true` dopo invio riuscito o dopo "Salta per ora" |
| `leads_pending.json` (Fase 4) | Coda `{ email, consent, install_id, … }` se POST fallito |

`install_id` è distinto da eventuale `preferences.json` di UI — può vivere nello stesso file prefs.

### 4.6 Flusso UI (modal primo avvio)

Ordine suggerito rispetto al wizard esistente:

```
Primo avvio Electron
    ↓
Wizard download modelli (esistente) — oppure prima del wizard, da decidere in UX
    ↓
Modal lead opt-in (NUOVO)
    ├─ "Tienimi aggiornato" + checkbox consenso (non pre-spuntata) → POST /v1/leads
    └─ "Salta per ora" → nessun POST, flag completed
    ↓
App principale
```

**Copy minimo:** aggiornamenti importanti / sicurezza only · link privacy · opt-out.

### 4.7 File da toccare (bozza)

| File | Modifica |
|------|----------|
| `desktop-electron/src/main.js` | Mostra modal; chiama `submitLead()` |
| `desktop-electron/src/leads.js` (nuovo) | HTTP client, coda, retry |
| `desktop-electron/src/preload.js` | Bridge se modal in renderer separato |
| `desktop-electron/package.json` / build | `LEADS_API_URL`, `LEADS_APP_TOKEN` a build time |

### 4.8 Test manuale app (prima del merge)

1. `GET https://qwiboleads.antoniotrento.net/health` → `ok: true`
2. Modal → iscrizione → verifica lead in DB (export admin sul Pi, repo privato)
3. "Salta" → nessuna chiamata di rete per lead
4. Secondo avvio → modal non ripresentato
5. Server spento → app parte; lead in coda; al ripristino server → retry ok

---

## 5. Contratto API (riferimento server)

### `POST /v1/leads`
Header:
- `X-App-Token: <token>` — vedi repo privato `qwibo-leads/secret/` (non in `qwibo`).

Body (JSON):
```json
{
  "email": "utente@example.com",
  "consent": true,
  "install_id": "uuid-v4-generato-al-primo-avvio",
  "app_version": "0.1.0-alpha.1",
  "os": "win32-10.0.26200",
  "locale": "it-IT",
  "source": "first-run-modal"
}
```

Risposte:
- `201 Created` → `{ "ok": true }`
- `200 OK` (già presente, dedup su `install_id`/email) → `{ "ok": true, "dup": true }`
- `422` → validazione (email non valida / consent=false)
- `401` → token mancante/errato
- `429` → rate limit

### `GET /unsubscribe?token=...`
Link di cancellazione nelle email → segna il lead come `unsubscribed`
(diritto GDPR alla cancellazione/opt-out). Base URL pubblica: `https://qwiboleads.antoniotrento.net`.

### Endpoint solo admin (non usati dall'app)

| Metodo | Path | Header |
|--------|------|--------|
| `GET` | `/v1/stats` | `X-Admin-Token` |
| `GET` | `/v1/export.csv` | `X-Admin-Token` |

---

## 6. Schema DB (SQLite, minimale)

```sql
CREATE TABLE leads (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  email        TEXT NOT NULL,
  install_id   TEXT,
  consent      INTEGER NOT NULL DEFAULT 0,
  app_version  TEXT,
  os           TEXT,
  locale       TEXT,
  source       TEXT,
  created_at   TEXT NOT NULL DEFAULT (datetime('now')),
  unsubscribed INTEGER NOT NULL DEFAULT 0
);
CREATE UNIQUE INDEX idx_leads_email ON leads(email);
```

> **GDPR minimo:** salva solo ciò che serve. **Non** salvare l'IP (o hashalo).
> Tieni prova del consenso (`consent`, `created_at`, testo/versione mostrata).

---

## 7. Fasi & Definition of Done

### Fase 1 — Server FastAPI sul Raspberry Pi
- [x] App FastAPI con `POST /v1/leads` (pydantic `EmailStr`, validazione).
- [x] SQLite con schema §5, dedup su email / install_id.
- [x] Token `X-App-Token` + **rate limit** (slowapi) + `GET /health`.
- [x] Export CSV + stats admin (`X-Admin-Token`).
- [x] Docker Compose nel repository privato `qwibo-leads`.
- **DoD:** `curl` locale crea/deduplica un lead; input non validi → 422.

### Fase 2 — Esposizione Cloudflare Tunnel
- [x] Ingress `qwiboleads.antoniotrento.net` → `http://127.0.0.1:8080`
- [x] DNS CNAME sul tunnel esistente
- [x] `cloudflared` servizio systemd (già attivo sul Pi)
- **DoD:** `GET https://qwiboleads.antoniotrento.net/health` OK da rete esterna ✅

### Fase 3 — Modal primo avvio nell'app Electron
- [ ] Costanti `LEADS_API_URL` + `LEADS_APP_TOKEN` (build, no commit token)
- [ ] Genera `install_id` (UUID) al primo avvio, persistito localmente.
- [ ] Modal con: campo email, **checkbox consenso non pre-spuntata**, testo
      valore + privacy, bottoni "Tienimi aggiornato" / "Salta per ora".
- [ ] Validazione email lato client; invio `POST` come §4.3.
- [ ] Flag locale "già chiesto" → non riproporre (salvo skip: eventuale re-prompt
      soft dopo N avvii, non invasivo).
- **DoD:** al primo avvio compare il modal; iscrizione → lead via HTTPS pubblico;
      "Salta" → app usabile, nessun invio.

### Fase 4 — Robustezza & offline
- [ ] Se l'invio fallisce → coda locale + retry al prossimo avvio.
- [ ] Timeout breve, **mai bloccante** per l'uso dell'app.
- **DoD:** con server spento l'app funziona; alla riaccensione il lead arriva.

### Fase 5 — Conformità piena
- [ ] Link `unsubscribe` nelle email + endpoint relativo.
- [ ] Pagina privacy dedicata (cosa raccogli, perché, come cancellare).
- [ ] (Opzionale) **double opt-in**: mail di conferma prima di considerare valido
      il lead (massima solidità GDPR; richiede SMTP).

---

## 8. Sicurezza & rischi

| Rischio | Mitigazione |
|---|---|
| Spam/bot verso l'endpoint | Token app + rate limit + validazione |
| Token estraibile dall'app | Accettato (anti-spam base, non auth forte); rate limit come rete di sicurezza |
| Pi/tunnel giù | Coda locale + retry lato client |
| Dato personale (GDPR) | Consenso esplicito, minimizzazione dati, unsubscribe, no IP |

---

## 9. Stima

- Server FastAPI + SQLite: **mezza giornata**.
- Cloudflare Tunnel: **1-2 ore** (già hai il Pi online).
- Modal Electron + retry: **mezza/una giornata**.
- Totale realistico: **1-2 giorni** per una v1 funzionante e pulita.
