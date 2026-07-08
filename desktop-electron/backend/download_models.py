#!/usr/bin/env python3
"""Download modelli desktop — progresso JSON su stdout per wizard Electron."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

# UTF-8 forzato su qualsiasi Windows: emit() stampa JSON con caratteri non-ASCII
# (≥, —, …) e con lo stdout rediretto la codepage locale crasherebbe il print.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BACKEND = Path(__file__).resolve().parent
VENDOR = BACKEND / "vendor"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

ASR_URL = (
    "https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/resolve/main/parakeet-tdt-0.6b-v3.nemo"
)
ASR_MIN_BYTES = 2_200_000_000
ASR_ESTIMATE_BYTES = 2_600_000_000
QWEN_MIN_BYTES = 4_000_000_000  # 7B q4_k_m ~4.68 GB: sotto = download incompleto
QWEN_ESTIMATE_BYTES = 4_683_074_240  # dimensione reale del GGUF 7B q4_k_m (bartowski)
MIN_RAM_GB = 16


def emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def _curl_bin() -> str:
    win_curl = Path(r"C:\Windows\System32\curl.exe")
    if sys.platform == "win32" and win_curl.is_file():
        return str(win_curl)
    found = shutil.which("curl")
    if not found:
        raise RuntimeError("curl non trovato.")
    return found


def _system_ram_gb() -> float | None:
    try:
        import psutil

        return psutil.virtual_memory().total / (1024**3)
    except Exception:
        return None


def _asr_path() -> Path:
    from qwibo.config import DEFAULT_MODEL, models_dir

    name = DEFAULT_MODEL.split("/")[-1]
    return models_dir() / f"{name}.nemo"


def _qwen_path() -> Path:
    from qwibo.config import LOCAL_LLM_GGUF_FILE, local_llm_dir

    return local_llm_dir() / LOCAL_LLM_GGUF_FILE


def _asr_ok(path: Path) -> bool:
    return path.is_file() and path.stat().st_size >= ASR_MIN_BYTES


def _qwen_ok(path: Path) -> bool:
    return path.is_file() and path.stat().st_size >= QWEN_MIN_BYTES


def download_asr() -> None:
    from qwibo.config import models_dir

    out = _asr_path()
    models_dir().mkdir(parents=True, exist_ok=True)

    if _asr_ok(out):
        emit({"event": "skip", "id": "asr", "reason": "Già presente"})
        return

    if out.is_file() and out.stat().st_size > 50_000_000:
        emit({"event": "phase", "id": "asr", "label": "Ripresa download modello vocale"})
    else:
        out.unlink(missing_ok=True)
        emit(
            {
                "event": "phase",
                "id": "asr",
                "label": "Download modello vocale Parakeet (~2,5 GB)",
                "total_mb": round(ASR_ESTIMATE_BYTES / (1024 * 1024)),
            }
        )

    cmd = [
        _curl_bin(),
        *(["--ssl-no-revoke"] if sys.platform == "win32" else []),
        "-L",
        "-C",
        "-",
        "-o",
        str(out),
        ASR_URL,
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    stop = threading.Event()

    def poll() -> None:
        while not stop.is_set():
            if out.is_file():
                size = out.stat().st_size
                pct = min(99.0, 100.0 * size / ASR_ESTIMATE_BYTES)
                emit(
                    {
                        "event": "progress",
                        "id": "asr",
                        "pct": round(pct, 1),
                        "mb": round(size / (1024 * 1024)),
                    }
                )
            time.sleep(0.4)

    t = threading.Thread(target=poll, daemon=True)
    t.start()
    code = proc.wait()
    stop.set()
    t.join(timeout=1)

    if code != 0 or not _asr_ok(out):
        raise RuntimeError("Download modello vocale fallito o incompleto.")

    emit({"event": "progress", "id": "asr", "pct": 100.0, "mb": round(out.stat().st_size / (1024 * 1024))})
    emit({"event": "done", "id": "asr"})


def download_qwen() -> None:
    ram = _system_ram_gb()
    if ram is not None and ram < MIN_RAM_GB:
        emit(
            {
                "event": "skip",
                "id": "qwen",
                "reason": f"RAM {ram:.0f} GB — riassunto locale richiede ≥ {MIN_RAM_GB} GB. Usa API cloud.",
            }
        )
        return

    out = _qwen_path()
    if _qwen_ok(out):
        emit({"event": "skip", "id": "qwen", "reason": "Già presente"})
        return

    from qwibo.config import LOCAL_LLM_GGUF_FILE, local_llm_dir, models_dir
    from qwibo.local_llm_download import HF_REPO

    dest_dir = local_llm_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    models_dir().mkdir(parents=True, exist_ok=True)

    # Download diretto con curl (come l'ASR): scrive nel file finale, così la
    # barra di progresso vede crescere i byte in tempo reale. hf_hub_download
    # scriveva invece in un file temporaneo nascosto e mostrava 0% fino alla
    # fine, sembrando "bloccato". Niente più dipendenza da hf_xet/hf_hub qui.
    url = f"https://huggingface.co/{HF_REPO}/resolve/main/{LOCAL_LLM_GGUF_FILE}"

    if out.is_file() and out.stat().st_size > 50_000_000:
        emit({"event": "phase", "id": "qwen", "label": "Ripresa download modello riassunto locale"})
    else:
        out.unlink(missing_ok=True)
        emit(
            {
                "event": "phase",
                "id": "qwen",
                "label": "Download modello riassunto locale Qwen (~4.7 GB)",
                "total_mb": round(QWEN_ESTIMATE_BYTES / (1024 * 1024)),
            }
        )

    cmd = [
        _curl_bin(),
        *(["--ssl-no-revoke"] if sys.platform == "win32" else []),
        "-L",
        "-C",
        "-",
        "-o",
        str(out),
        url,
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    stop = threading.Event()

    def poll() -> None:
        while not stop.is_set():
            if out.is_file():
                size = out.stat().st_size
                pct = min(99.0, 100.0 * size / QWEN_ESTIMATE_BYTES)
                emit(
                    {
                        "event": "progress",
                        "id": "qwen",
                        "pct": round(pct, 1),
                        "mb": round(size / (1024 * 1024)),
                    }
                )
            time.sleep(0.5)

    t = threading.Thread(target=poll, daemon=True)
    t.start()
    code = proc.wait()
    stop.set()
    t.join(timeout=1)

    if code != 0 or not _qwen_ok(out):
        raise RuntimeError("Download modello riassunto locale fallito o incompleto.")

    emit({"event": "progress", "id": "qwen", "pct": 100.0, "mb": round(out.stat().st_size / (1024 * 1024))})
    emit({"event": "done", "id": "qwen"})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--setup-all", action="store_true", help="ASR + Qwen (se RAM ok)")
    parser.add_argument("--asr-only", action="store_true")
    parser.add_argument("--qwen-only", action="store_true")
    args = parser.parse_args()

    try:
        emit({"event": "start", "ram_gb": _system_ram_gb()})
        if args.asr_only:
            download_asr()
        elif args.qwen_only:
            download_qwen()
        else:
            # ASR è obbligatorio: se fallisce, l'app non può trascrivere → errore fatale.
            download_asr()
            # Qwen (riassunto locale) è opzionale: se fallisce, si usano le API cloud.
            # Non deve mai impedire l'avvio dell'app.
            try:
                download_qwen()
            except Exception as exc:  # noqa: BLE001
                emit(
                    {
                        "event": "skip",
                        "id": "qwen",
                        "reason": f"Riassunto locale non disponibile ({exc}). "
                        "Potrai usare le API cloud (OpenAI/Anthropic/Gemini) dalle impostazioni.",
                    }
                )
                print(f"Qwen non scaricato (non bloccante): {exc}", file=sys.stderr)
        emit({"event": "complete"})
        return 0
    except Exception as exc:
        emit({"event": "error", "message": str(exc)})
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
