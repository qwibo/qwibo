#!/usr/bin/env python3
"""Build runtime per installer retail — solo macchina di sviluppo/CI.

Scarica Python standalone, crea venv con torch+NeMo+UI, scarica ffmpeg statico.
Output: desktop-electron/build/  (incluso nell'installer NSIS)
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
BUILD = ROOT / "build"
SYNC = ROOT / "scripts" / "sync_backend.py"

# python-build-standalone (Windows x64, install_only)
PYTHON_URL = (
    "https://github.com/astral-sh/python-build-standalone/releases/download/20241016/"
    "cpython-3.12.7%2B20241016-x86_64-pc-windows-msvc-install_only.tar.gz"
)
PYTHON_DIR = BUILD / "runtime-venv"

# ffmpeg essentials (Windows)
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_DIR = BUILD / "ffmpeg"

# Toolchain C/C++ portatile (MinGW-w64 14 UCRT, GCC 16 — winlibs) come .zip puro:
# nessun .exe da eseguire (antivirus-friendly). Header mingw-w64 recenti necessari
# a ggml (es. THREAD_POWER_THROTTLING_STATE). Serve per compilare llama-cpp-python
# baseline (senza AVX) così il riassunto locale gira su QUALSIASI CPU Windows x64.
MINGW_URL = (
    "https://github.com/brechtsanders/winlibs_mingw/releases/download/"
    "16.1.0posix-14.0.0-ucrt-r3/"
    "winlibs-x86_64-posix-seh-gcc-16.1.0-mingw-w64ucrt-14.0.0-r3.zip"
)
# Lo zip contiene una cartella radice "mingw64/".
MINGW_DIR = BUILD / "mingw64"

# Versione llama-cpp-python compilata da sorgente (deve combaciare coi binding usati).
LLAMA_CPP_VERSION = "0.3.32"

# DLL del Visual C++ / OpenMP runtime richieste dalle DLL native di
# llama-cpp-python (llama.dll, ggml*.dll). msvcp140/vcomp140/concrt140 NON fanno
# parte di un Windows base: senza VC++ 2015-2022 Redistributable l'import di
# llama_cpp fallirebbe sul PC dell'utente. Le bundliamo accanto a llama.dll.
MSVC_RUNTIME_DLLS = (
    "msvcp140.dll",
    "msvcp140_1.dll",
    "vcomp140.dll",
    "concrt140.dll",
    "vcruntime140.dll",
    "vcruntime140_1.dll",
)


def run(cmd: list[str], *, check: bool = True, env: dict[str, str] | None = None, **kwargs) -> None:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    if check:
        subprocess.check_call(cmd, env=env, **kwargs)
    else:
        subprocess.call(cmd, env=env, **kwargs)


def _curl_bin() -> str | None:
    win_curl = Path(r"C:\Windows\System32\curl.exe")
    if sys.platform == "win32" and win_curl.is_file():
        return str(win_curl)
    return shutil.which("curl")


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 1024:
        print(f"Già presente: {dest.name}", flush=True)
        return
    print(f"Download: {url}", flush=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    curl = _curl_bin()
    if curl:
        cmd = [
            curl,
            *(["--ssl-no-revoke"] if sys.platform == "win32" else []),
            "-L",
            "-f",
            "-o",
            str(tmp),
            url,
        ]
        run(cmd)
        tmp.replace(dest)
        return
    try:
        import truststore  # type: ignore[import-untyped]

        truststore.inject_into_ssl()
    except ImportError:
        pass
    with urllib.request.urlopen(url, timeout=600) as resp, tmp.open("wb") as out:
        shutil.copyfileobj(resp, out)
    tmp.replace(dest)


def ensure_python() -> Path:
    if sys.platform != "win32":
        raise SystemExit("build_runtime.py v0.1 supporta solo Windows x64.")

    exe = PYTHON_DIR / "python.exe"
    if exe.is_file():
        return exe

    BUILD.mkdir(parents=True, exist_ok=True)
    archive = BUILD / "python-standalone.tar.gz"
    download(PYTHON_URL, archive)

    if PYTHON_DIR.exists():
        shutil.rmtree(PYTHON_DIR)
    PYTHON_DIR.mkdir(parents=True)

    with tarfile.open(archive, "r:gz") as tar:
        for member in tar.getmembers():
            parts = Path(member.name).parts
            if not parts:
                continue
            rel = Path(*parts[1:]) if len(parts) > 1 else Path(parts[0])
            target = PYTHON_DIR / rel
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with tar.extractfile(member) as src, target.open("wb") as dst:
                    if src:
                        shutil.copyfileobj(src, dst)

    if not exe.is_file():
        raise SystemExit(f"python.exe non trovato dopo estrazione: {exe}")
    return exe


def ensure_ffmpeg() -> Path:
    bin_dir = FFMPEG_DIR / "bin"
    ffmpeg_exe = bin_dir / "ffmpeg.exe"
    if ffmpeg_exe.is_file():
        return bin_dir

    BUILD.mkdir(parents=True, exist_ok=True)
    archive = BUILD / "ffmpeg-essentials.zip"
    download(FFMPEG_URL, archive)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(tmp_path)
        found = next(tmp_path.rglob("ffmpeg.exe"), None)
        if not found:
            raise SystemExit("ffmpeg.exe non trovato nello zip.")
        src_bin = found.parent
        if FFMPEG_DIR.exists():
            shutil.rmtree(FFMPEG_DIR)
        shutil.copytree(src_bin, bin_dir)
    return bin_dir


def ensure_mingw() -> Path:
    """Scarica ed estrae il toolchain MinGW-w64 portatile. Ritorna la dir bin/."""
    bin_dir = MINGW_DIR / "bin"
    gcc = bin_dir / "gcc.exe"
    if gcc.is_file():
        return bin_dir

    BUILD.mkdir(parents=True, exist_ok=True)
    archive = BUILD / "mingw64.zip"
    download(MINGW_URL, archive)

    # Lo zip contiene una cartella radice "mingw64/": estraendo in BUILD
    # otteniamo build/mingw64/bin/gcc.exe.
    if MINGW_DIR.exists():
        force_remove(MINGW_DIR)
    with zipfile.ZipFile(archive, "r") as zf:
        zf.extractall(BUILD)

    if not gcc.is_file():
        raise SystemExit(f"gcc non trovato dopo estrazione MinGW: {gcc}")
    return bin_dir


def force_remove(path: Path) -> None:
    if not path.exists():
        return

    def onerror(func, p, _exc_info) -> None:
        os.chmod(p, stat.S_IWUSR | stat.S_IREAD)
        func(p)

    shutil.rmtree(path, onerror=onerror)


def _pip_env() -> dict[str, str]:
    return {
        **os.environ,
        "PYTHONNOUSERSITE": "1",
        "PIP_TRUSTED_HOST": (
            "pypi.org pypi.python.org files.pythonhosted.org "
            "download.pytorch.org download-r2.pytorch.org huggingface.co "
            "abetlen.github.io"
        ),
    }


def _pip_base(py: Path) -> list[str]:
    return [
        str(py),
        "-m",
        "pip",
        "install",
        "--no-cache-dir",
        "--upgrade-strategy",
        "only-if-needed",
        "--extra-index-url",
        "https://download.pytorch.org/whl/cpu",
        "--trusted-host",
        "pypi.org",
        "--trusted-host",
        "pypi.python.org",
        "--trusted-host",
        "files.pythonhosted.org",
        "--trusted-host",
        "download.pytorch.org",
        "--trusted-host",
        "download-r2.pytorch.org",
        "--trusted-host",
        "huggingface.co",
        "--trusted-host",
        "abetlen.github.io",
    ]


def _pip_retry(cmd: list[str], *, env: dict[str, str], label: str) -> None:
    for attempt in range(1, 4):
        try:
            run(cmd, env=env)
            return
        except subprocess.CalledProcessError:
            if attempt == 3:
                raise
            print(f"{label} fallito (tentativo {attempt}/3), riprovo...", flush=True)
            import time

            time.sleep(5)


def build_llama_cpp(py: Path, w64_bin: Path) -> None:
    """Compila llama-cpp-python da sorgente in modalità BASELINE (nessun AVX).

    Motivazione retail: la wheel precompilata assume AVX2/AVX512 e crasha
    (0xC000001D STATUS_ILLEGAL_INSTRUCTION) su CPU che non le hanno. Compilando
    con GGML_NATIVE=OFF e AVX/AVX2/AVX512/FMA/F16C disattivati, ggml usa il suo
    baseline x86-64 (SSE4.2 + BMI2) supportato da tutte le CPU Windows moderne
    (Intel Haswell 2013+ / AMD Zen), evitando le istruzioni AVX che causavano il
    crash. Le poche DLL runtime MinGW (libgcc/libstdc++/libwinpthread) vengono
    copiate accanto a llama.dll da copy_mingw_runtime().
    """
    scripts_dir = py.parent / "Scripts"
    # CMake vuole il path ASSOLUTO del compilatore. Usiamo slash forward per
    # evitare problemi di escaping su Windows.
    w64_bin = w64_bin.resolve()
    gcc = (w64_bin / "gcc.exe").as_posix()
    gpp = (w64_bin / "g++.exe").as_posix()
    env = _pip_env()
    env["PATH"] = os.pathsep.join(
        [str(w64_bin), str(scripts_dir), env.get("PATH", "")]
    )
    env["CC"] = gcc
    env["CXX"] = gpp
    env["CMAKE_GENERATOR"] = "Ninja"
    env["FORCE_CMAKE"] = "1"
    # NB: niente "-static" globale: su MinGW rompe l'unwinding SEH nelle DLL
    # (multiple definition of _Unwind_Resume). Linkiamo dinamico e copiamo le
    # poche DLL runtime MinGW accanto a llama.dll (copy_mingw_runtime()).
    env["CMAKE_ARGS"] = " ".join(
        [
            "-DGGML_NATIVE=OFF",
            "-DGGML_AVX=OFF",
            "-DGGML_AVX2=OFF",
            "-DGGML_AVX512=OFF",
            "-DGGML_FMA=OFF",
            "-DGGML_F16C=OFF",
            "-DGGML_OPENMP=OFF",
            f"-DCMAKE_C_COMPILER={gcc}",
            f"-DCMAKE_CXX_COMPILER={gpp}",
            # MinGW punta di default a Windows 7: forziamo target Windows 10
            # (l'app richiede Win10+). Necessario a cpp-httplib/CreateFile2.
            "-DCMAKE_C_FLAGS=-D_WIN32_WINNT=0x0A00",
            "-DCMAKE_CXX_FLAGS=-D_WIN32_WINNT=0x0A00",
        ]
    )

    cmd = _pip_base(py) + [
        "--no-binary",
        "llama-cpp-python",
        "--no-build-isolation",
        f"llama-cpp-python=={LLAMA_CPP_VERSION}",
    ]
    _pip_retry(cmd, env=env, label="build llama-cpp-python (baseline)")


def copy_mingw_runtime(runtime: Path, mingw_bin: Path) -> None:
    """Copia le DLL runtime MinGW accanto a llama.dll/ggml*.dll.

    llama.dll è compilato con MinGW e dipende da poche DLL di runtime (libgcc,
    libstdc++, libwinpthread). Windows le risolve dalla stessa cartella della
    DLL caricata via ctypes: mettendole in llama_cpp/lib il pacchetto è
    self-contained su PC puliti (nessun redistributable da installare).
    """
    lib = runtime / "Lib" / "site-packages" / "llama_cpp" / "lib"
    if not lib.is_dir():
        print("llama_cpp/lib assente: salto copia runtime MinGW.", flush=True)
        return

    mingw_bin = mingw_bin.resolve()
    names = (
        "libgcc_s_seh-1.dll",
        "libstdc++-6.dll",
        "libwinpthread-1.dll",
    )
    copied: list[str] = []
    for name in names:
        src = mingw_bin / name
        dst = lib / name
        if src.is_file() and not dst.is_file():
            shutil.copy2(src, dst)
            copied.append(name)
    if copied:
        print(f"Runtime MinGW copiato in llama_cpp/lib: {', '.join(copied)}", flush=True)


def pip_install(py: Path, backend: Path, w64_bin: Path) -> None:
    """Install backend + deps into relocatable standalone Python."""
    pip_env = _pip_env()
    base = _pip_base(py)

    # 1) Tooling per setuptools e build da sorgente (scikit-build-core per llama).
    _pip_retry(
        base
        + [
            "--upgrade",
            "pip",
            "setuptools>=68",
            "wheel",
            "scikit-build-core",
            "cmake",
            "ninja",
        ],
        env=pip_env,
        label="pip bootstrap",
    )

    # 2) llama-cpp-python compilato da sorgente, baseline (compat. CPU totale).
    build_llama_cpp(py, w64_bin)

    # 3) Backend non-editable: niente path assoluti della macchina di build.
    #    llama-cpp-python è già soddisfatto dallo step 2 (non viene ricompilato).
    _pip_retry(
        base + [str(backend), "--no-build-isolation"],
        env=pip_env,
        label="pip backend",
    )


def ensure_vendor() -> None:
    vendor = BACKEND / "vendor" / "qwibo"
    if vendor.is_dir():
        return
    if not SYNC.is_file():
        raise SystemExit("sync_backend.py mancante.")
    run([sys.executable, str(SYNC)])


def validate_runtime(runtime: Path) -> None:
    """Blocca build con path assoluti o venv non relocabile."""
    pyvenv = runtime / "pyvenv.cfg"
    if pyvenv.is_file():
        raise SystemExit(
            "ERRORE: trovato pyvenv.cfg — il runtime non è relocabile.\n"
            "Elimina build/runtime-venv e rilancia build_runtime.py."
        )

    site = runtime / "Lib" / "site-packages"
    for pth in site.glob("__editable__*.pth"):
        raise SystemExit(f"ERRORE: pip editable residuo ({pth.name}) — path assoluti nel pacchetto.")

    py = runtime / "python.exe"
    if not py.is_file():
        raise SystemExit(f"ERRORE: manca {py}")

    vendor = BACKEND / "vendor"
    env = {**os.environ, "PYTHONPATH": str(vendor), "PYTHONNOUSERSITE": "1"}
    run(
        [
            str(py),
            "-c",
            "import qwibo, torch; from qwibo.config import models_dir; print('OK')",
        ],
        env=env,
    )
    print("Validazione runtime: OK (relocabile, import qwibo ok)", flush=True)


def bundle_msvc_runtime(runtime: Path) -> None:
    """Copia le DLL VC++/OpenMP accanto a llama.dll (self-contained su PC puliti)."""
    lib = runtime / "Lib" / "site-packages" / "llama_cpp" / "lib"
    if not lib.is_dir():
        print("llama_cpp/lib assente: salto bundling VC++ runtime.", flush=True)
        return

    system32 = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32"
    copied: list[str] = []
    missing: list[str] = []
    for name in MSVC_RUNTIME_DLLS:
        dst = lib / name
        if dst.is_file():
            continue
        src = system32 / name
        if src.is_file():
            shutil.copy2(src, dst)
            copied.append(name)
        else:
            missing.append(name)

    if copied:
        print(f"VC++ runtime bundlato in llama_cpp/lib: {', '.join(copied)}", flush=True)
    if missing:
        print(
            "ATTENZIONE: DLL VC++ non trovate in System32 "
            f"({', '.join(missing)}). Installa 'Visual C++ 2015-2022 Redistributable "
            "(x64)' sulla macchina di build e rilancia.",
            flush=True,
        )


def build_runtime(*, skip_pip: bool) -> Path:
    runtime = PYTHON_DIR
    py = runtime / "python.exe"
    if skip_pip and py.is_file():
        validate_runtime(runtime)
        return runtime

    force_remove(runtime)
    ensure_python()
    py = runtime / "python.exe"

    if skip_pip:
        return runtime

    mingw_bin = ensure_mingw()
    pip_install(py, BACKEND, mingw_bin)
    copy_mingw_runtime(runtime, mingw_bin)
    validate_runtime(runtime)
    return runtime


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepara runtime per installer Qwibo")
    parser.add_argument(
        "--skip-pip",
        action="store_true",
        help="Salta pip install (solo python+ffmpeg già in cache)",
    )
    args = parser.parse_args()

    print("=== Build runtime Qwibo Desktop ===\n")
    ensure_vendor()
    ffmpeg_bin = ensure_ffmpeg()
    runtime = build_runtime(skip_pip=args.skip_pip)
    # llama.dll è compilato con MinGW e runtime linkato staticamente (-static):
    # non dipende dalle DLL VC++ redistributable, quindi non serve bundlarle.

    print("\n=== Runtime pronto ===")
    print(f"  Python:  {runtime / 'python.exe'}")
    print(f"  ffmpeg:  {ffmpeg_bin / 'ffmpeg.exe'}")
    print("\nProssimo passo: npm run dist:win")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
