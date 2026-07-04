# Copyright (c) 2024-2026 Antonio Trento
# Installa venv e dipendenze backend nella cartella desktop-electron.

"""Setup backend autonomo (venv + pip). Esegui da desktop-electron/."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
VENDOR_PKG = BACKEND / "vendor" / "qwibo"
VENV = BACKEND / ".venv"
SYNC = ROOT / "scripts" / "sync_backend.py"


def run(cmd: list[str], **kwargs) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.check_call(cmd, **kwargs)


def main() -> int:
    if not VENDOR_PKG.is_dir():
        if SYNC.is_file():
            print("Vendor assente — sincronizzazione da repo principale...")
            run([sys.executable, str(SYNC)])
        if not VENDOR_PKG.is_dir():
            print(
                "ERRORE: backend/vendor/qwibo mancante.\n"
                "Esegui: python scripts/sync_backend.py --source <path>/src/qwibo",
                file=sys.stderr,
            )
            return 1

    if not VENV.is_dir():
        print("Creazione virtualenv backend...")
        run([sys.executable, "-m", "venv", str(VENV)])

    if sys.platform == "win32":
        py = VENV / "Scripts" / "python.exe"
        pip = VENV / "Scripts" / "pip.exe"
    else:
        py = VENV / "bin" / "python"
        pip = VENV / "bin" / "pip"

    run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
    run(
        [
            str(pip),
            "install",
            "--no-cache-dir",
            "torch",
            "--index-url",
            "https://download.pytorch.org/whl/cpu",
        ]
    )
    run([str(pip), "install", "--no-cache-dir", "-e", str(BACKEND)])

    print("\nBackend pronto:", py)
    print("Avvia app: npm run dev")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
