# Qwibo — desktop app

Offline audio transcription and local LLM summaries for Windows.

## Repository layout

| Path | Content |
|------|---------|
| `desktop-electron/` | Electron app + Windows installer |
| `src/qwibo/` | Python backend |
| `docs/` | MkDocs for **desktop** (published to qwibo.github.io) |
| `microevolutive/` | Sprint plans: `active/`, `done/`, `reference/` |
| `evolutive/` | User scenarios + deferred ideas (`old/` = Streamlit era archive) |
| `tracker/` | GitHub Issues setup — [Issues](https://github.com/qwibo/qwibo/issues) (source of truth) |
| `strategia-release/` | Alpha release strategy (hosting, marketing, Mac build) |
| repository privato **`qwibo-leads`** | Lead collection API (Docker on mini PC — not in this repo; see private `qwibo-leads` repo) |

Related repos:

- [qwibo.github.io](https://github.com/qwibo/qwibo.github.io) — marketing site
- [qwibo-docker](https://github.com/qwibo/qwibo-docker) — self-hosted Docker (docs local only)

## Documentation

```bash
pip install -r docs/requirements.txt
mkdocs serve
python scripts/publish_docs.py   # copies to ../qwibo.github.io/docs/
```

## Build installer (dev)

See `desktop-electron/README.md`.
