# Microevolutive — Qwibo

Piani **corti ed eseguibili**: fasi, prerequisiti, Definition of Done, ordine di implementazione.

---

## Struttura

| Cartella | Cosa contiene |
|----------|----------------|
| [`active/`](./active/) | Prossimi sprint — da fare o in corso |
| [`done/`](./done/) | Piani chiusi (codice v1 consegnato) |
| [`reference/`](./reference/) | Decisioni architetturali (non sono task) |
| [`old/`](./old/) | Alternative scartate (es. Tauri) |

---

## Stato rapido (luglio 2026)

| Piano | Stato | Note |
|-------|--------|------|
| Multilang summary | ✅ fatto | [`done/PLAN_MULTILANG_SUMMARY.md`](./done/PLAN_MULTILANG_SUMMARY.md) |
| Multilang ASR (IT EN FR ES DE) | ✅ fatto | [`done/PLAN_MULTILANG_ASR.md`](./done/PLAN_MULTILANG_ASR.md) |
| Desktop Electron | 🔄 in corso | Alpha Win installer — [`done/PLAN_DESKTOP_ELECTRON.md`](./done/PLAN_DESKTOP_ELECTRON.md) |
| **UI desktop (menu, tema)** | 📋 da fare | [`active/PLAN_UI_DESKTOP.md`](./active/PLAN_UI_DESKTOP.md) |
| **App multilingua (UI + default)** | 📋 da fare | [`active/PLAN_APP_I18N.md`](./active/PLAN_APP_I18N.md) |
| Branding Qwibo | 🔄 parziale | Nome + codice ok — [`done/PLAN_BRANDING.md`](./done/PLAN_BRANDING.md) |
| Backlog (licenza, doctor, watch folder…) | 📋 da prioritizzare | [`done/PLAN_BACKLOG.md`](./done/PLAN_BACKLOG.md) |
| Lead generation | 🔄 Fase 1–2 ✅ server live · Fase 3 app | [`active/PLAN_LEAD_GENERATION.md`](./active/PLAN_LEAD_GENERATION.md) · API `qwiboleads.antoniotrento.net` |
| Electron vs Tauri | ✅ deciso | [`reference/DESKTOP_CONFRONTO.md`](./reference/DESKTOP_CONFRONTO.md) |

---

## Prossimo lavoro suggerito

```
1. active/PLAN_UI_DESKTOP   →  layout, menu Windows, tema light/dark
2. active/PLAN_APP_I18N     →  wizard lingua install + UI 5 lingue + default ASR/summary
3. done/PLAN_DESKTOP_ELECTRON →  Mac, signing, OTA (dopo polish UI)
4. done/PLAN_BACKLOG        →  licenza commerciale o qwibo doctor
5. active/PLAN_LEAD_GENERATION →  dopo alpha stabile
```

I piani in `done/` restano come riferimento storico; non vanno riaperti salvo regressioni.

---

## Relazione con altre cartelle

| Cartella | Ruolo |
|----------|--------|
| `bug-fix/` | Cosa è rotto **oggi** (registro bug + fix puntuali) |
| `evolutive/` | **Perché** — scenari utente e idee non in sprint |
| `strategia-release/` | Go-to-market alpha (hosting, marketing, build Mac) |
| `desktop-electron/` | Codice installer + `WINDOWS-RELEASE-FIXES.md` |
| repository privato **`qwibo-leads`** | **Server lead email** (Docker mini PC, non nell'installer; repo privato) |
| `docs/` | Documentazione utente MkDocs |

---

## Baseline prodotto (già in repo)

- FastAPI + HTMX, coda job SQLite, worker separato
- Riassunto multi-provider, licenza personal + modal primo avvio
- ASR multilingua 5 lingue core, summary multilingua
- Installer Windows alpha (`desktop-electron/`)
- Sito `qwibo.github.io`, docs MkDocs

I nuovi piani partono da questo stato.
