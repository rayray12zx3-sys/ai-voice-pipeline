"""Small explicit provider registry."""

from __future__ import annotations

from .gemini import GeminiTTSProvider


_PROVIDERS = {
    "GEMINI": GeminiTTSProvider,
}


def get_provider(name: str):
    try:
        return _PROVIDERS[name.upper()]
    except (AttributeError, KeyError) as exc:
        raise ValueError(f"unknown provider: {name}") from exc


def provider_names() -> tuple[str, ...]:
    return tuple(sorted(_PROVIDERS))
