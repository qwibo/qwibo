# Microevolutive — Qwibo

Piani **corti ed eseguibili**: fasi, prerequisiti, Definition of Done, ordine di implementazione.

---

## Documenti

| File | Focus | Priorità |
|------|--------|----------|
| [PLAN_MULTILANG_SUMMARY.md](./PLAN_MULTILANG_SUMMARY.md) | Riassunto LLM multilingua | **1** |
| [PLAN_MULTILANG_ASR.md](./PLAN_MULTILANG_ASR.md) | **ASR NeMo: IT EN FR ES DE** (5 lingue core) | **2** |
| [PLAN_DESKTOP_ELECTRON.md](./PLAN_DESKTOP_ELECTRON.md) | **Desktop Electron** (Win + Mac) | **3** |
| [DESKTOP_CONFRONTO.md](./DESKTOP_CONFRONTO.md) | Decisione architetturale desktop | riferimento |
| [PLAN_BACKLOG.md](./PLAN_BACKLOG.md) | Licenza, watch folder, editor, … | **4** |
| [PLAN_LEAD_GENERATION.md](./PLAN_LEAD_GENERATION.md) | **Lead generation**: email primo avvio → FastAPI su Raspberry Pi (Cloudflare Tunnel) | **5** |
| [PLAN_BRANDING.md](./PLAN_BRANDING.md) | **Branding & nome**: rebrand da "Qwibo" → **Qwibo** (deciso) | riferimento |

**Desktop:** scelta ufficiale **Electron** — embedded Python v1, Nuitka opzionale v2.

**ASR multilingua:** Parakeet v3 già multilingue — serve esporre scelta lingua (5 core: IT EN FR ES DE). Vedi `PLAN_MULTILANG_ASR.md`.

---

## Relazione con altre cartelle

| Cartella | Ruolo |
|----------|--------|
| `bug-fix/` | Cosa è rotto **oggi** |
| `evolutive/` | Scenari utente + idee remote (snello) |
| `evolutive/old/` | Roadmap storica (Streamlit v0.2) |
| `microevolutive/old/` | Piano desktop Tauri (alternativa scartata) |
| `docs/` | Documentazione utente (MkDocs) |

---

## Ordine di esecuzione consigliato

```
PLAN_MULTILANG_SUMMARY  →  PLAN_MULTILANG_ASR
                              ↓
              PLAN_DESKTOP_ELECTRON — fase 2b (backend-ready)
                              ↓
              PLAN_DESKTOP_ELECTRON — fase 2a (wrapper dev)
                              ↓
                    PLAN_BACKLOG (licenza)
                              ↓
              Installer Win → Mac + signing + OTA (fase 2c)
```

---

## Stato base (luglio 2026)

Già in produzione:

- FastAPI + HTMX, coda job SQLite, worker separato
- Riassunto multi-provider, licenza + modal primo avvio
- Docker mini PC, sito `qwibo.github.io`, docs MkDocs

I piani partono da questo stato.
