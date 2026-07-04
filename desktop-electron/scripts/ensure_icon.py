#!/usr/bin/env python3
"""Genera assets/icon.ico da icon.png (richiesto da NSIS/electron-builder)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PNG = ROOT / "assets" / "icon.png"
ICO = ROOT / "assets" / "icon.ico"


def main() -> int:
    if ICO.is_file() and ICO.stat().st_size > 1024:
        print(f"Icona OK: {ICO.name}")
        return 0
    if not PNG.is_file():
        raise SystemExit(f"Manca {PNG}")

    from PIL import Image

    im = Image.open(PNG).convert("RGBA").resize((256, 256), Image.Resampling.LANCZOS)
    im.save(ICO, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Creato: {ICO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
