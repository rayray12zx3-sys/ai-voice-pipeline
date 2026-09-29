"""Provider interface used by future routers."""

from __future__ import annotations

from typing import Protocol

from ..contracts import VoiceRequest


class VoiceProvider(Protocol):
    provider_name: str

    @classmethod
    def build_payload(cls, request: VoiceRequest) -> dict: ...

    @classmethod
    def generate(cls, request: VoiceRequest) -> bytes: ...
