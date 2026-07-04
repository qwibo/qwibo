# System requirements

Requirements depend on **what you use**: transcription only, cloud API summary, or offline local summary (Qwen).

## Operating system

| Requirement | Detail |
|-------------|--------|
| OS | **Windows 10 or 11** (64-bit) |
| Admin | Not required for normal use |
| Internet | Required for **first-run model download** and optional cloud summaries |

## Comparison by scenario

| Scenario | RAM | Free disk | Network at runtime |
|----------|-----|-----------|-------------------|
| **Transcription only** | 8 GB min · 16 GB recommended | ~8 GB | No (after setup) |
| **Transcription + API summary** | Same as above | Same | Yes during summary |
| **Transcription + local Qwen** | **≥ 16 GB** · 32 GB ideal | ~10–12 GB | No (after setup) |

!!! note "RAM and local summary"
    Before local summary the pipeline **unloads the ASR model from RAM**. Qwibo checks total physical RAM; below **16 GB** the local Qwen engine is not offered.

---

## Transcription only

| Resource | Detail |
|----------|--------|
| **RAM** | Minimum **8 GB**; **16 GB** recommended for long files (1 h+). |
| **Disk** | ~2.5 GB ASR model + app data + job output → **≥ 8 GB** free. |
| **CPU** | Modern x64; expect ~**2× realtime** on CPU (1 min audio ≈ 2 min processing). |
| **GPU** | Not used in the desktop alpha (CPU-only ASR). |

---

## Transcription + cloud summary

| Resource | Detail |
|----------|--------|
| **RAM** | Same as transcription — LLM runs in the cloud. |
| **Disk** | No extra model for summary. |
| **Network** | Required when generating summaries. |
| **API key** | Configure in app → **Summary settings**. |

Suitable for PCs with **8 GB RAM** if you use cloud providers only.

---

## Transcription + local summary (Qwen)

| Resource | Detail |
|----------|--------|
| **RAM** | **≥ 16 GB** (checked at setup). **32 GB** recommended for long texts. |
| **Disk** | Transcription footprint **+ ~2 GB** Qwen GGUF. |
| **CPU** | Summary is CPU-bound; long texts may take several minutes (map-reduce). |

See also [Models](models.md).

---

## Bundled dependencies (end user)

The installer includes **embedded Python**, **ffmpeg**, and the Qwibo backend. You do **not** need to install these separately.

---

## Self-hosted alternative

A Linux mini PC with more RAM/GPU can run [qwibo-docker](https://github.com/qwibo/qwibo-docker) instead. Hardware guidance for Docker is documented in that repository.
