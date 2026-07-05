# Evolutive — Qwibo

Documentazione **snella** su scenari utente e idee non prioritarie.

I **piani eseguibili** (desktop, backlog, lead gen) sono in **[microevolutive/](../microevolutive/README.md)**.

---

## Documenti attivi

| File | Contenuto | Superfluo? |
|------|-----------|------------|
| [CASI-D-USO.md](./CASI-D-USO.md) | Scenari utente (CU-01…CU-08) e lacune prodotto | **No** — guida il *perché* delle feature |
| [EVOLUTIVE-REMOTE.md](./EVOLUTIVE-REMOTE.md) | Idee utili ma **fuori sprint** (es. diarizzazione) | **No** — evita di reinserirle nel backlog per sbaglio |

**Trascrizione multilingua:** implementata — vedi [microevolutive/done/PLAN_MULTILANG_ASR.md](../microevolutive/done/PLAN_MULTILANG_ASR.md) e [CU-08](./CASI-D-USO.md#cu-08--audio-in-lingua-straniera-mercato-mondiale).

---

## Archivio (`old/`)

Roadmap e analisi dell'**era Streamlit v0.2**. Utili solo come contesto storico; la maggior parte è già nel codice o duplicata in `microevolutive/active/PLAN_BACKLOG.md`.

| File | Verdetto |
|------|----------|
| `ROADMAP-EVOLUTIVE.md` | Storico P1–P5; Fase 1 già shipped |
| `ARCHITETTURA-FUTURA.md` | Migrazione Streamlit → worker — **completata** |
| `ANALISI-DIARIZZAZIONE-SPEAKER.md` | Dettaglio tecnico; sintesi in `EVOLUTIVE-REMOTE.md` |

Non cancellare: costa poco tenerli. Non usarli per pianificare sprint.

---

## Desktop

**Scelta ufficiale:** Electron + Python embedded (Windows + macOS).

- Piano: [microevolutive/active/PLAN_DESKTOP_ELECTRON.md](../microevolutive/active/PLAN_DESKTOP_ELECTRON.md)
- Decisione: [microevolutive/reference/DESKTOP_CONFRONTO.md](../microevolutive/reference/DESKTOP_CONFRONTO.md)

---

## Altre cartelle

| Cartella | Ruolo |
|----------|--------|
| [`tracker/`](../tracker/) + [GitHub Issues](https://github.com/qwibo/qwibo/issues) | Tracciamento attivo bug e task |
| `bug-fix/` | Archivio bug risolti e specifiche storiche |
| `microevolutive/active/` | **Prossimi sprint** (dettaglio piani) |
| `strategia-release/` | Alpha: hosting, marketing, build Mac |
| `docs/` | Documentazione utente |
