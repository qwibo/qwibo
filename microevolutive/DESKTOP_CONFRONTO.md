# Desktop — decisione architetturale

> **Data**: 2026-07-02 · **Stato**: ✅ **deciso**  
> **Scelta:** **Electron** + backend Python **embedded** (v1). Nuitka opzionale in v2.  
> **Piano attivo:** [PLAN_DESKTOP_ELECTRON.md](./PLAN_DESKTOP_ELECTRON.md)

---

## Decisione

| | Scelta | Note |
|---|--------|------|
| **Shell** | Electron | Standard industria (VS Code, Slack, Discord) |
| **UI** | FastAPI + HTMX in `BrowserWindow` | Nessuna riscrittura |
| **Backend v1** | Python embedded (`python-build-standalone`) | Affidabile con PyTorch/NeMo |
| **Backend v2** | Nuitka (opzionale) | Solo se serve anti-tampering post-lancio |
| **Piattaforme** | Windows + macOS (ARM64 prioritario) | Prodotto mondiale |
| **Alternativa scartata** | Tauri | Archiviata in [old/PLAN_DESKTOP_TAURI.md](./old/PLAN_DESKTOP_TAURI.md) |

### Motivazioni

1. **Percezione professionale** — stack desktop consumer riconosciuto globalmente.
2. **Win + Mac** dallo stesso progetto (`electron-builder`, `electron-updater`).
3. **Comunicazione semplice** — spawn backend + `localhost` HTTP (come `start.bat` oggi).
4. **Time-to-market** — embedded Python in v1 evita il rischio Nuitka+NeMo al lancio.
5. **RAM Electron** — irrilevante con NeMo su laptop 16 GB.

---

## Confronto storico (per riferimento)

| Criterio | Tauri (scartata) | Electron (scelta) |
|----------|------------------|-------------------|
| Ecosistema retail | Buono | **Eccellente** |
| Win + Mac | Sì | Sì |
| Packaging ML v1 | Embedded | **Embedded** (stessa strategia) |
| Auto-update | Tauri updater | **electron-updater** |
| Shell leggera | ✅ ~20 MB | ⚠️ ~100 MB (accettato) |

Tauri restava valida tecnicamente; Electron vince su **ecosistema, updater e percezione mercato** per un prodotto retail mondiale.

---

## Sequenza di implementazione

```
Fase 2b — backend desktop-ready     1–2 sett
         ↓
Fase 2a — Electron dev wrapper      2–3 sett
         ↓
Fase 2c — Installer Windows         3–4 sett
         ↓
Fase 2c — Installer Mac (ARM64)     4–6 sett
         ↓
Fase 2d — Licenza commerciale       1–2 sett
         ↓
Fase 2e — Nuitka (opzionale)        post-v1
```

---

## Documenti

| File | Ruolo |
|------|--------|
| [PLAN_DESKTOP_ELECTRON.md](./PLAN_DESKTOP_ELECTRON.md) | **Piano esecutivo** |
| [old/PLAN_DESKTOP_TAURI.md](./old/PLAN_DESKTOP_TAURI.md) | Alternativa archiviata |
