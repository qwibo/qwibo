# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""i18n leggero per la UI: dizionari JSON per locale + helper Jinja ``t()``.

Chiavi mancanti in un locale ricadono sull'italiano, poi sulla chiave stessa,
così l'app non si rompe mai anche con traduzioni incomplete.
"""

from __future__ import annotations

import json
import locale as _locale
import os
import sys
from functools import lru_cache
from pathlib import Path

import jinja2

LOCALES_DIR = Path(__file__).parent / "ui" / "locales"
DEFAULT_LOCALE = "it"
SUPPORTED_LOCALES = ("it", "en", "fr", "es", "de")


def normalize_locale(locale: str | None) -> str:
    code = (locale or "").strip().lower()[:2]
    return code if code in SUPPORTED_LOCALES else DEFAULT_LOCALE


@lru_cache(maxsize=None)
def _load(locale: str) -> dict[str, str]:
    path = LOCALES_DIR / f"{locale}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def translate(locale: str, key: str) -> str:
    loc = normalize_locale(locale)
    value = _load(loc).get(key)
    if value is None and loc != DEFAULT_LOCALE:
        value = _load(DEFAULT_LOCALE).get(key)
    return value if value is not None else key


# --- Rilevamento lingua del sistema operativo (primo avvio) -----------------

# LCID → codice lingua per le 5 lingue core (Windows GetUserDefaultUILanguage).
_WIN_PRIMARY_LANG = {0x09: "en", 0x0A: "es", 0x0C: "fr", 0x07: "de", 0x10: "it"}


def _first_supported(*candidates: str | None) -> str | None:
    for cand in candidates:
        if not cand:
            continue
        code = str(cand).strip().lower().replace("_", "-")[:2]
        if code in SUPPORTED_LOCALES:
            return code
    return None


def detect_os_locale(default: str = "en") -> str:
    """Lingua del SO tra le 5 core, altrimenti ``default`` (EN).

    Priorità: env ``QWIBO_UI_LOCALE`` (Electron può passare ``app.getLocale()``)
    → lingua UI di Windows → locale POSIX / variabili d'ambiente.
    """
    found = _first_supported(
        os.environ.get("QWIBO_UI_LOCALE"),
        os.environ.get("QWIBO_OS_LOCALE"),
    )
    if found:
        return found

    if sys.platform == "win32":
        try:
            import ctypes

            lcid = ctypes.windll.kernel32.GetUserDefaultUILanguage()  # type: ignore[attr-defined]
            win = _WIN_PRIMARY_LANG.get(lcid & 0x3FF)
            if win in SUPPORTED_LOCALES:
                return win
        except Exception:  # noqa: BLE001
            pass

    try:
        posix = _locale.getlocale()[0]
    except Exception:  # noqa: BLE001
        posix = None
    found = _first_supported(
        posix,
        os.environ.get("LANG"),
        os.environ.get("LC_ALL"),
        os.environ.get("LANGUAGE"),
    )
    return found or default


@jinja2.pass_context
def t(context: jinja2.runtime.Context, key: str) -> str:
    """Helper da usare nei template: ``{{ t('nav.home') }}``.

    Il locale è preso da ``ui_locale`` nel contesto di render (fallback IT).
    """
    try:
        locale = context.get("ui_locale") or DEFAULT_LOCALE
    except Exception:  # noqa: BLE001
        locale = DEFAULT_LOCALE
    return translate(str(locale), key)
