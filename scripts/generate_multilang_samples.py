#!/usr/bin/env python3
# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
"""Genera campioni audio multilingua (WAV 16 kHz) da testi in data/input/testi/."""

from __future__ import annotations

import argparse
import asyncio
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_DIR = ROOT / "data" / "input" / "testi"
OUT_DIR = ROOT / "data" / "input"
sys.path.insert(0, str(ROOT / "src"))

LANGS = ("it", "en", "fr", "es", "de")
LEVELS = ("medio", "lungo")

# Voci neurali Microsoft Edge (edge-tts)
VOICES = {
    "it": "it-IT-ElsaNeural",
    "en": "en-US-JennyNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "de": "de-DE-KatjaNeural",
}


def require_tools() -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg non trovato nel PATH.")


def require_edge_tts() -> None:
    try:
        import edge_tts  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Pacchetto edge-tts mancante. Installa con:\n  pip install edge-tts"
        ) from exc


async def _synthesize(text: str, voice: str, mp3_path: Path) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(mp3_path))


def text_to_wav(text_path: Path, wav_path: Path, voice: str) -> float:
    tmp_mp3 = wav_path.with_suffix(".mp3")
    asyncio.run(_synthesize(text_path.read_text(encoding="utf-8"), voice, tmp_mp3))
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(tmp_mp3),
            "-ar",
            "16000",
            "-ac",
            "1",
            str(wav_path),
        ],
        check=True,
        capture_output=True,
    )
    tmp_mp3.unlink(missing_ok=True)
    dur = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(wav_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(dur.stdout.strip())


def write_readme() -> None:
    lines = [
        "Campioni audio multilingua (TTS edge-tts)",
        "========================================",
        "",
        "Rigenera con: python scripts/generate_multilang_samples.py",
        "",
    ]
    for lang in LANGS:
        for level in LEVELS:
            name = f"campione-{lang}-{level}"
            lines.append(f"{name}.wav  ←  testi/{name}.txt  ({VOICES[lang]})")
    lines.append("")
    lines.append("Italiano voce reale (Wikimedia): python scripts/generate_samples.py")
    (OUT_DIR / "CAMPIONI-MULTILANG.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera WAV multilingua da testi")
    parser.add_argument(
        "--lingua",
        choices=[*LANGS, "tutte"],
        default="tutte",
        help="Lingua da generare (default: tutte)",
    )
    parser.add_argument(
        "--livello",
        choices=[*LEVELS, "tutti"],
        default="tutti",
        help="medio (~2 min) o lungo (~5-6 min)",
    )
    args = parser.parse_args()

    try:
        require_tools()
        require_edge_tts()
    except RuntimeError as exc:
        print(f"ERRORE: {exc}", file=sys.stderr)
        return 1

    from qwibo.http_ssl import ensure_ssl

    ensure_ssl()

    langs = list(LANGS) if args.lingua == "tutte" else [args.lingua]
    levels = list(LEVELS) if args.livello == "tutti" else [args.livello]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Qwibo - campioni multilingua (edge-tts)")
    print(f"Testi: {TEXT_DIR}")
    print(f"Output: {OUT_DIR}\n")

    for lang in langs:
        voice = VOICES[lang]
        for level in levels:
            stem = f"campione-{lang}-{level}"
            text_path = TEXT_DIR / f"{stem}.txt"
            if not text_path.is_file():
                print(f"  SKIP {stem}: manca {text_path}", file=sys.stderr)
                continue
            wav_path = OUT_DIR / f"{stem}.wav"
            print(f">> {stem}.wav ({voice})")
            try:
                dur = text_to_wav(text_path, wav_path, voice)
            except subprocess.CalledProcessError as exc:
                print(f"   ERRORE ffmpeg: {exc.stderr.decode(errors='replace')}", file=sys.stderr)
                return 1
            mb = wav_path.stat().st_size / (1024 * 1024)
            print(f"   OK {dur:.1f}s · {mb:.2f} MB")

    write_readme()
    print("\nFatto. Vedi data/input/CAMPIONI-MULTILANG.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
