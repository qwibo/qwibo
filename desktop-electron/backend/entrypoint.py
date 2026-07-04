#!/usr/bin/env python3
"""Entrypoint backend per app desktop — avvia FastAPI su localhost."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Robustezza universale (qualsiasi Windows, qualsiasi lingua/codepage): con lo
# stdout rediretto Python userebbe la codepage locale (cp1252, cp932, ...) e
# crasherebbe con UnicodeEncodeError sui caratteri fuori codepage (→, —, ≥).
# Forziamo UTF-8 con errors="replace": non può crashare su nessun carattere.
# L'env PYTHONUTF8=1 impostato da Electron copre anche uvicorn/worker; questo
# è la rete di sicurezza per il processo entrypoint stesso.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

BACKEND = Path(__file__).resolve().parent
VENDOR = BACKEND / "vendor"
if str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))


def _prepare_desktop_runtime() -> None:
    """Vendor installato in bundle: salta verify_runtime del monorepo dev."""
    try:
        from qwibo.ui import process_guard

        process_guard.verify_runtime = lambda: None  # noqa: ARG005
    except ImportError:
        pass


def main() -> int:
    _prepare_desktop_runtime()

    port = int(os.environ.get("QWIBO_PORT") or os.environ.get("QWIBO_PORT") or "8765")
    host = os.environ.get("QWIBO_UI_HOST") or os.environ.get("QWIBO_UI_HOST") or "127.0.0.1"
    data = (os.environ.get("QWIBO_DATA") or os.environ.get("QWIBO_DATA") or "").strip()
    if data:
        os.environ["QWIBO_DATA"] = data
    models = os.environ.get("NEMO_CACHE_DIR", "").strip()
    if models:
        os.environ["NEMO_CACHE_DIR"] = models

    try:
        from qwibo.ui.launch import launch_ui
    except ImportError as exc:
        print("ERRORE: backend Qwibo non trovato nel pacchetto.", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 1

    print(f"Qwibo desktop backend → http://{host}:{port}", flush=True)
    launch_ui(port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
