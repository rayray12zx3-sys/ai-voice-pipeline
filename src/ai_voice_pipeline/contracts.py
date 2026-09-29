"""Provider-neutral voice request contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


SUPPORTED_MODELS = frozenset({
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
})


@dataclass(frozen=True)
class DialogueTurn:
    text: str
    speaker: str | None = None
    style: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("turn text must be non-empty")
        if self.speaker is not None and not self.speaker.strip():
            raise ValueError("speaker must be non-empty when provided")


@dataclass(frozen=True)
class VoiceRequest:
    model: str
    turns: tuple[DialogueTurn, ...]
    voices: Mapping[str, str]
    output_mime_type: str = "audio/wav"

    def __post_init__(self) -> None:
        if self.model not in SUPPORTED_MODELS:
            raise ValueError(f"unsupported model: {self.model}")
        if not self.turns:
            raise ValueError("at least one dialogue turn is required")
        if not self.voices:
            raise ValueError("at least one voice binding is required")

        speakers = {turn.speaker for turn in self.turns if turn.speaker is not None}
        if speakers:
            if len(speakers) > 2:
                raise ValueError("single-request conversational mode supports at most two speakers")
            if any(turn.speaker is None for turn in self.turns):
                raise ValueError("every turn must specify speaker in multi-speaker mode")
            if speakers != set(self.voices):
                raise ValueError("speaker names must exactly match voice bindings")
        elif len(self.voices) != 1:
            raise ValueError("single-speaker mode requires exactly one voice")

    @property
    def multi_speaker(self) -> bool:
        return any(turn.speaker is not None for turn in self.turns)
