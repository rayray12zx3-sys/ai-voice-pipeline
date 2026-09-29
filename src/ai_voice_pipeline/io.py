"""Configuration and materialization helpers."""

from __future__ import annotations

import json
from pathlib import Path

from .contracts import DialogueTurn, VoiceRequest


def load_request(path: str | Path) -> VoiceRequest:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    turns = tuple(
        DialogueTurn(
            text=item["text"],
            speaker=item.get("speaker"),
            style=item.get("style"),
        )
        for item in raw["turns"]
    )
    return VoiceRequest(
        model=raw["model"],
        turns=turns,
        voices=raw["voices"],
        output_mime_type=raw.get("output_mime_type", "audio/wav"),
    )


def write_bytes(path: str | Path, data: bytes) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target
