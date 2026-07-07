# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Preferenze utente persistite in ``preferences.json`` (data_dir).

Solo impostazioni non segrete (lingue, tema, default job). Le API key restano
in ``.secrets/summary_keys.json`` via ``summary_config`` — mai qui.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qwibo.config import data_dir
from qwibo.i18n import detect_os_locale

PREFERENCES_FILE = "preferences.json"

# Default = comportamento storico dell'app (nessuna regressione finché l'utente non cambia).
DEFAULT_PREFERENCES: dict[str, Any] = {
    "ui_theme": "dark",                 # "dark" | "light" | "system"
    "ui_locale": "it",
    "default_asr_language": "it",
    "default_summary_language": "it",
    "default_summary_enabled": True,
    "default_summary_length": "auto",   # auto | short | normal | detailed
    "default_summary_provider": "",     # "" => primo provider disponibile
    "setup_completed_at": "",           # ISO timestamp del primo avvio (seeding lingua SO)
}

_ALLOWED_KEYS = set(DEFAULT_PREFERENCES)


def preferences_path() -> Path:
    return data_dir() / PREFERENCES_FILE


def load_preferences() -> dict[str, Any]:
    """Preferenze correnti (default + file, se presente e valido)."""
    prefs = dict(DEFAULT_PREFERENCES)
    path = preferences_path()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return prefs
    if isinstance(raw, dict):
        for key, value in raw.items():
            if key in _ALLOWED_KEYS:
                prefs[key] = value
    return prefs


def ensure_preferences_initialized() -> dict[str, Any]:
    """Primo avvio: se ``preferences.json`` non esiste, lo crea impostando
    **lingua UI + trascrizione + riassunto** sulla lingua del sistema operativo
    (fallback inglese). Se il file esiste già, non tocca nulla (rispetta l'utente).
    """
    path = preferences_path()
    if path.exists():
        return load_preferences()

    os_lang = detect_os_locale()  # una delle 5 core, altrimenti "en"
    prefs = dict(DEFAULT_PREFERENCES)
    prefs["ui_locale"] = os_lang
    prefs["default_asr_language"] = os_lang
    prefs["default_summary_language"] = os_lang
    prefs["setup_completed_at"] = datetime.now(timezone.utc).isoformat()

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prefs, indent=2, ensure_ascii=False), encoding="utf-8")
    return prefs


def save_preferences(updates: dict[str, Any]) -> dict[str, Any]:
    """Aggiorna solo le chiavi note e riscrive il file. Ritorna le prefs risultanti."""
    prefs = load_preferences()
    for key, value in updates.items():
        if key in _ALLOWED_KEYS:
            prefs[key] = value
    path = preferences_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(prefs, indent=2, ensure_ascii=False), encoding="utf-8")
    return prefs
