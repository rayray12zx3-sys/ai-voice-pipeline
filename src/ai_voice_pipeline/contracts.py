"""Provider-neutral voice request contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


SUPPORTED_MODELS = frozenset({
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
})
SUPPORTED_MIME_TYPES = frozenset({"audio/wav"})
MAX_SPEAKERS = 2


def _nonempty(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True)
class DialogueTurn:
    text: str
    speaker: str | None = None
    style: str | None = None

    def __post_init__(self) -> None:
        _nonempty(self.text, "turn text")
        if self.speaker is not None:
            _nonempty(self.speaker, "speaker")
        if self.style is not None:
            _nonempty(self.style, "style")


@dataclass(frozen=True)
class VoiceRequest:
    """Canonical request used before provider translation."""

    model: str
    turns: tuple[DialogueTurn, ...]
    voices: Mapping[str, str]
    output_mime_type: str = "audio/wav"

    def __post_init__(self) -> None:
        if self.model not in SUPPORTED_MODELS:
            raise ValueError(f"unsupported model: {self.model}")
        if not self.turns:
            raise ValueError("at least one dialogue turn is required")
        if not isinstance(self.voices, Mapping) or not self.voices:
            raise ValueError("at least one voice binding is required")
        for alias, voice in self.voices.items():
            _nonempty(alias, "voice alias")
            _nonempty(voice, "provider voice")
        if self.output_mime_type not in SUPPORTED_MIME_TYPES:
            raise ValueError(
                "R0 supports audio/wav only; add a format adapter before using another mime type"
            )

        speakers = {turn.speaker for turn in self.turns if turn.speaker is not None}
        if speakers:
            if len(speakers) > MAX_SPEAKERS:
                raise ValueError(
                    f"single-request conversational mode supports at most {MAX_SPEAKERS} speakers"
                )
            if any(turn.speaker is None for turn in self.turns):
                raise ValueError("every turn must specify speaker in multi-speaker mode")
            if speakers != set(self.voices):
                raise ValueError("speaker names must exactly match voice bindings")
        elif len(self.voices) != 1:
            raise ValueError("single-speaker mode requires exactly one voice binding")

    @property
    def multi_speaker(self) -> bool:
        return any(turn.speaker is not None for turn in self.turns)

    def safe_summary(self) -> dict:
        """Metadata safe for logs; deliberately excludes transcript text."""
        return {
            "model": self.model,
            "turn_count": len(self.turns),
            "speaker_count": len(self.voices),
            "multi_speaker": self.multi_speaker,
            "output_mime_type": self.output_mime_type,
        }
