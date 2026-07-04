# Piano microevolutivo — Lead Generation (raccolta email al primo avvio)

> **Data**: 2026-07-04 · **Stato**: 📋 da implementare
> **Obiettivo**: costruire una base dati di utenti reali che installano l'app,
> raccogliendo **con consenso esplicito** l'email al primo avvio e archiviandola
> su un servizio FastAPI self-hosted (Raspberry Pi + Cloudflare Tunnel).
> **Uso:** feature indipendente, promuovibile a sprint dedicato.

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
   modal primo avvio                          sottodominio                FastAPI
   (email + consenso)                        (es. lead.tuodominio)        + SQLite
```

- **Client**: modal Electron → POST JSON all'endpoint. Se fallisce (offline,
  server giù) → **non blocca l'app**, salva in coda locale e ritenta al prossimo
  avvio.
- **Trasporto**: Cloudflare Tunnel espone il Pi con HTTPS su un sottodominio,
  senza aprire porte sul router.
- **Server**: FastAPI minimale, storage SQLite (basico, come richiesto).

---

## 4. Contratto API

### `POST /v1/leads`
Header:
- `X-App-Token: <token>` — segreto condiviso incluso nell'app (anti-spam base;
  non è sicurezza forte, ma alza l'asticella).

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
(diritto GDPR alla cancellazione/opt-out).

---

## 5. Schema DB (SQLite, minimale)

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

## 6. Fasi & Definition of Done

### Fase 1 — Server FastAPI sul Raspberry Pi
- [ ] App FastAPI con `POST /v1/leads` (pydantic `EmailStr`, validazione).
- [ ] SQLite con schema §5, dedup su email.
- [ ] Token `X-App-Token` + **rate limit** (es. slowapi) + logging.
- [ ] Endpoint `GET /health`.
- **DoD:** `curl` locale crea/deduplica un lead; input non validi → 422.

### Fase 2 — Esposizione Cloudflare Tunnel
- [ ] `cloudflared` sul Pi → sottodominio HTTPS che punta a FastAPI locale.
- [ ] Tunnel come servizio (parte al boot del Pi).
- **DoD:** `POST https://lead.<dominio>/v1/leads` funziona da rete esterna.

### Fase 3 — Modal primo avvio nell'app Electron
- [ ] Genera `install_id` (UUID) al primo avvio, persistito localmente.
- [ ] Modal con: campo email, **checkbox consenso non pre-spuntata**, testo
      valore + privacy, bottoni "Tienimi aggiornato" / "Salta per ora".
- [ ] Validazione email lato client; invio POST con token e metadati.
- [ ] Flag locale "già chiesto" → non riproporre (salvo skip: eventuale re-prompt
      soft dopo N avvii, non invasivo).
- **DoD:** al primo avvio compare il modal; iscrizione → lead nel DB del Pi;
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

## 7. Sicurezza & rischi

| Rischio | Mitigazione |
|---|---|
| Spam/bot verso l'endpoint | Token app + rate limit + validazione |
| Token estraibile dall'app | Accettato (anti-spam base, non auth forte); rate limit come rete di sicurezza |
| Pi/tunnel giù | Coda locale + retry lato client |
| Dato personale (GDPR) | Consenso esplicito, minimizzazione dati, unsubscribe, no IP |

---

## 8. Stima

- Server FastAPI + SQLite: **mezza giornata**.
- Cloudflare Tunnel: **1-2 ore** (già hai il Pi online).
- Modal Electron + retry: **mezza/una giornata**.
- Totale realistico: **1-2 giorni** per una v1 funzionante e pulita.
