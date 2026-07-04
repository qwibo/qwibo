# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Lingue supportate per ASR (NeMo) e riassunto LLM."""

from __future__ import annotations

from enum import Enum

DEFAULT_LANGUAGE = "it"

CORE_LANGUAGE_CODES: tuple[str, ...] = ("it", "en", "fr", "es", "de")

LANGUAGE_LABELS_IT: dict[str, str] = {
    "it": "Italiano",
    "en": "Inglese",
    "fr": "Francese",
    "es": "Spagnolo",
    "de": "Tedesco",
}

LANGUAGE_LABELS_SHORT: dict[str, str] = {
    "it": "IT",
    "en": "EN",
    "fr": "FR",
    "es": "ES",
    "de": "DE",
}


class ContentLanguage(str, Enum):
    it = "it"
    en = "en"
    fr = "fr"
    es = "es"
    de = "de"


def normalize_language(code: str | None, *, default: str = DEFAULT_LANGUAGE) -> str:
    if not code:
        return default
    value = code.strip().lower()
    if value in LANGUAGE_LABELS_IT:
        return value
    return default


def language_label(code: str | None, *, short: bool = False) -> str:
    lang = normalize_language(code)
    labels = LANGUAGE_LABELS_SHORT if short else LANGUAGE_LABELS_IT
    return labels.get(lang, lang.upper())


def language_options() -> list[dict[str, str]]:
    return [
        {"code": code, "label": LANGUAGE_LABELS_IT[code], "short": LANGUAGE_LABELS_SHORT[code]}
        for code in CORE_LANGUAGE_CODES
    ]
