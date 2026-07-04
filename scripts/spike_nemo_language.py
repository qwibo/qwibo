#!/usr/bin/env python3
# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
"""Spike: verifica API lingua NeMo su Parakeet v3 (opzionale, richiede modello locale)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from qwibo.config import DEFAULT_MODEL, TranscribeConfig, local_model_path
from qwibo.languages import CORE_LANGUAGE_CODES


def main() -> int:
    parser = argparse.ArgumentParser(description="Test hint lingua NeMo/Parakeet")
    parser.add_argument("wav", type=Path, help="File WAV mono 16 kHz")
    parser.add_argument(
        "--language",
        "-l",
        default="en",
        choices=CORE_LANGUAGE_CODES,
        help="Lingua da testare",
    )
    args = parser.parse_args()
    if not args.wav.is_file():
        print(f"File non trovato: {args.wav}", file=sys.stderr)
        return 1
    if not local_model_path(DEFAULT_MODEL):
        print("Modello non trovato. Esegui: python scripts/download_model.py", file=sys.stderr)
        return 2

    from qwibo.transcribe import _apply_asr_language_hint, _get_model, _transcribe_file

    config = TranscribeConfig(language=args.language)
    model = _get_model(config)
    _apply_asr_language_hint(model, args.language)
    result = _transcribe_file(model, args.wav, language=args.language)
    print(f"language={args.language}")
    print(result.text[:500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
