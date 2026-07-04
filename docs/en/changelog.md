# Changelog

## 0.1.0-alpha.1

- First **Windows desktop installer** (Electron + embedded Python)
- Offline transcription with NVIDIA NeMo Parakeet
- Optional local Qwen summary (RAM ≥ 16 GB) or cloud LLM providers
- Rebrand from Sbobinator to **Qwibo**
- Documentation published at [qwibo.github.io/docs](https://qwibo.github.io/docs/)

### Known limitations (alpha)

- Installer **unsigned** — SmartScreen warning
- CPU-only ASR in desktop build
- Model setup wizard (progress UI improvements planned)
- Mac build not yet available

## Roadmap (high level)

- Code signing (Authenticode)
- In-app model download progress
- Mac DMG + notarization
- UX polish (Phase 3 branding plan)

See `evolutive/` in the repository for longer-term ideas.
