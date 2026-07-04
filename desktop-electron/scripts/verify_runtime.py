#!/usr/bin/env python3
"""Verifica che build/runtime-venv sia pronto per l'installer (relocabile)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "build" / "runtime-venv"
PY = RUNTIME / "python.exe"
VENDOR = ROOT / "backend" / "vendor"
LLAMA_LIB = RUNTIME / "Lib" / "site-packages" / "llama_cpp" / "lib"
OBJDUMP = ROOT / "build" / "mingw64" / "bin" / "objdump.exe"


def fail(msg: str) -> int:
    print(f"FAIL: {msg}", file=sys.stderr)
    return 1


def check_llama_baseline() -> int | None:
    """Garanzia retail: le DLL ggml NON devono contenere istruzioni AVX.

    La wheel precompilata usava AVX2/FMA e andava in crash (0xC000001D
    STATUS_ILLEGAL_INSTRUCTION) su CPU senza quelle estensioni. Compiliamo
    baseline (SSE2). Qui lo verifichiamo disassemblando le DLL: la presenza di
    registri ymm/zmm indicherebbe AVX/AVX2/AVX512 → build da rifiutare.
    """
    ggml_dlls = sorted(LLAMA_LIB.glob("ggml*.dll")) if LLAMA_LIB.is_dir() else []
    if not ggml_dlls:
        return fail(
            f"nessuna DLL ggml in {LLAMA_LIB} — llama-cpp-python non compilato. "
            "Rilancia build_runtime.py."
        )

    if not OBJDUMP.is_file():
        print(
            f"ATTENZIONE: objdump non trovato ({OBJDUMP}); salto la verifica "
            "disassembly AVX (garanzia data dai flag di compilazione baseline).",
            file=sys.stderr,
        )
        return None

    for dll in ggml_dlls:
        try:
            asm = subprocess.check_output(
                [str(OBJDUMP), "-d", "--no-show-raw-insn", str(dll)],
                text=True,
                errors="ignore",
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as exc:
            return fail(f"objdump fallito su {dll.name}:\n{exc.output}")

        lowered = asm.lower()
        for reg in ("ymm", "zmm"):
            if reg in lowered:
                return fail(
                    f"{dll.name} contiene istruzioni AVX (registri {reg}): "
                    "la build NON è baseline e crasherà su CPU senza AVX. "
                    "Verifica i flag GGML_* in build_runtime.py."
                )
    print(f"  llama baseline: OK ({len(ggml_dlls)} DLL ggml, nessuna istruzione AVX)")
    return None


def check_llama_load() -> int | None:
    """Se è disponibile un GGUF, carica davvero il modello per intercettare qui
    (in build) eventuali crash di istruzione illegale, non sul PC dell'utente."""
    candidates: list[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "qwibo-desktop" / "models")
    candidates.append(ROOT.parent / "models")
    candidates.append(ROOT.parent / "models" / "qwen")

    gguf: Path | None = None
    for folder in candidates:
        if folder.is_dir():
            found = next(iter(sorted(folder.rglob("*.gguf"))), None)
            if found:
                gguf = found
                break

    if gguf is None:
        print(
            "  llama load: nessun GGUF trovato per lo smoke test "
            "(garanzia data da baseline + disassembly).",
        )
        return None

    code = (
        "from llama_cpp import Llama\n"
        f"llm = Llama(model_path=r'{gguf}', n_ctx=256, n_threads=2, verbose=False)\n"
        "out = llm.create_completion('ciao', max_tokens=8)\n"
        "print(out['choices'][0]['text'][:20])\n"
    )
    env = {**os.environ, "PYTHONPATH": str(VENDOR), "PYTHONNOUSERSITE": "1"}
    try:
        subprocess.check_output(
            [str(PY), "-c", code], text=True, stderr=subprocess.STDOUT, env=env
        )
    except subprocess.CalledProcessError as exc:
        return fail(f"caricamento GGUF ({gguf.name}) fallito:\n{exc.output}")
    print(f"  llama load: OK (modello {gguf.name} caricato ed eseguito)")
    return None


def main() -> int:
    # python-build-standalone tiene python.exe nella root. Un venv lo mette in
    # Scripts/ e ha pyvenv.cfg con path assoluti: non relocabile.
    if (RUNTIME / "pyvenv.cfg").is_file():
        return fail(
            "pyvenv.cfg presente: runtime è un venv (path assoluti della macchina "
            "di build), non uno standalone relocabile.\n"
            "Elimina build/runtime-venv e rilancia build_runtime.py senza --skip-pip."
        )

    if not PY.is_file():
        scripts_py = RUNTIME / "Scripts" / "python.exe"
        if scripts_py.is_file():
            return fail(
                "python.exe è in Scripts/ (layout venv), non nella root: non relocabile. "
                "Rigenera con build_runtime.py."
            )
        return fail(f"manca {PY} — esegui build_runtime.py")

    site = RUNTIME / "Lib" / "site-packages"
    for pth in site.glob("__editable__*.pth"):
        return fail(
            f"pip editable residuo: {pth.name} — punta a path assoluti della "
            "macchina di build. Reinstalla non-editable (build_runtime.py senza --skip-pip)."
        )

    # Le dipendenze pesanti devono importare dal runtime bundlato.
    try:
        deps = subprocess.check_output(
            [str(PY), "-c", "import torch, fastapi, uvicorn, nemo; print('deps OK')"],
            text=True,
            stderr=subprocess.STDOUT,
        ).strip()
    except subprocess.CalledProcessError as exc:
        return fail(f"import dipendenze fallito:\n{exc.output}")

    # A runtime qwibo viene caricato dal vendor bundlato via PYTHONPATH
    # (vedi src/backend-spawn.js). Deve essere presente e importabile così.
    vendor_pkg = VENDOR / "qwibo" / "config.py"
    if not vendor_pkg.is_file():
        return fail(f"vendor mancante: {vendor_pkg} — esegui sync_backend.py")

    env = {**os.environ, "PYTHONPATH": str(VENDOR)}
    try:
        loc = subprocess.check_output(
            [str(PY), "-c", "import qwibo; print(qwibo.__file__)"],
            text=True,
            stderr=subprocess.STDOUT,
            env=env,
        ).strip()
    except subprocess.CalledProcessError as exc:
        return fail(f"import qwibo (da vendor) fallito:\n{exc.output}")

    # llama-cpp-python: garanzia compatibilità CPU per il riassunto locale.
    rc = check_llama_baseline()
    if rc is not None:
        return rc
    rc = check_llama_load()
    if rc is not None:
        return rc

    print("OK runtime relocabile (standalone, non editable)")
    print(f"  python: {PY}")
    print(f"  deps:   {deps}")
    print(f"  qwibo (vendor): {loc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
