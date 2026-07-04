# Copyright (c) 2024-2026 Antonio Trento
# Script di setup backend — cartella desktop-electron autonoma.

"""Copia il codice qwibo in backend/vendor/ (una tantum o aggiornamento).

Uso (da desktop-electron/):
  python scripts/sync_backend.py
  python scripts/sync_backend.py --source C:\\path\\to\\qwibo\\src\\qwibo
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENDOR_PKG = ROOT / "backend" / "vendor" / "qwibo"
DEFAULT_SOURCE = ROOT.parent / "src" / "qwibo"


def sync(source: Path) -> None:
    if not source.is_dir():
        raise SystemExit(
            f"Sorgente non trovata: {source}\n"
            "Passa --source con il percorso a src/qwibo del repo Qwibo."
        )
    if VENDOR_PKG.exists():
        shutil.rmtree(VENDOR_PKG)
    VENDOR_PKG.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source,
        VENDOR_PKG,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )
    print(f"Backend sincronizzato: {VENDOR_PKG} ({len(list(VENDOR_PKG.rglob('*')))} voci)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Copia qwibo in backend/vendor/")
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Cartella src/qwibo da copiare",
    )
    args = parser.parse_args()
    sync(args.source.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
