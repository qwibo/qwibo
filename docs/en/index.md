# Qwibo

**Qwibo** is a Windows desktop app that transcribes audio and video to text **offline**, using the [NVIDIA NeMo Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) model. Optional LLM summaries run locally (Qwen) or via cloud APIs.

!!! info "Bilingual documentation"
    This site is also available in **Italiano**. Use the language selector in the top navigation bar.

## What it does

| Feature | Description |
|---------|-------------|
| **Transcription** | Audio/video → plain text + SRT subtitles |
| **Job queue** | Multiple files processed one at a time; history and detail pages in the app |
| **Summary** | Multi-provider LLM (DeepSeek, OpenAI, local Qwen, …) |
| **Desktop app** | Electron installer — no Python, no terminal, no Docker |
| **Privacy** | Audio stays on your PC during transcription |

## Who this is for

Qwibo is built for people who already have recordings — meetings, podcasts, interviews, lectures — and want usable text **without** uploading files to a cloud service or paying per minute.

For **self-hosted Docker** on a home server or NAS, see the separate [qwibo-docker](https://github.com/qwibo/qwibo-docker) repository.

## Quick start

1. Download `Qwibo-Setup-*.exe` from [GitHub Releases](https://github.com/qwibo/qwibo/releases).
2. Run the installer (see [SmartScreen](troubleshooting/smartscreen.md) if Windows blocks it).
3. Complete the **first-run setup** (~4–5 GB one-time model download).
4. Upload a file and click **Queue transcription**.

Details: [Download & install](getting-started/download.md) · [First run](getting-started/first-run.md)

## Hardware at a glance

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| Windows | 10/11 64-bit | 11 |
| RAM (transcription only) | 8 GB | 16 GB |
| RAM (local Qwen summary) | 16 GB | 32 GB |
| Free disk | 8 GB | 12 GB |
| GPU | Not required | NVIDIA optional (future) |

Full details: [System requirements](getting-started/system-requirements.md)

## Documentation map

| Section | Content |
|---------|---------|
| [Getting started](getting-started/overview.md) | Install, first run, models |
| [User guide](user-guide/app-interface.md) | UI, queue, summaries, formats |
| [Troubleshooting](troubleshooting/common-issues.md) | Common errors |
| [Reference](reference/faq.md) | FAQ, licenses |

## Build documentation locally

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

Preview at http://127.0.0.1:8000 — publish with `scripts\publish_docs.bat` (or `python scripts/publish_docs.py`), then `git push` in the sibling repo `qwibo.github.io`. **No GitHub Actions.**

## License

**Proprietary software** — Copyright © 2024-2026 [Antonio Trento](https://antoniotrento.net). Free for personal use; commercial use requires a [paid license](reference/commercial-license.md). See [Licenses](reference/licenses.md).
