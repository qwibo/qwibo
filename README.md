# Qwibo — desktop app

Offline audio transcription and local LLM summaries for Windows.

## Repository layout

| Path | Content |
|------|---------|
| `desktop-electron/` | Electron app + Windows installer |
| `src/qwibo/` | Python backend |
| `docs/` | MkDocs for **desktop** (published to qwibo.github.io) |
| `evolutive/` | Long-term product ideas and roadmap notes |

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
