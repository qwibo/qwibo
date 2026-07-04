# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

"""Provider LLM per riassunto trascritti."""

from qwibo.http_ssl import ensure_ssl

ensure_ssl()

from qwibo.summarize_providers.registry import (
    PROVIDER_IDS,
    get_provider,
    list_provider_capabilities,
    provider_label,
)

__all__ = [
    "PROVIDER_IDS",
    "get_provider",
    "list_provider_capabilities",
    "provider_label",
]
