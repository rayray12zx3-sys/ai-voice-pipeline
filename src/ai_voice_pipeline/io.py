"""Configuration and safe materialization helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from .contracts import DialogueTurn, VoiceRequest


def load_request(path: str | Path) -> VoiceRequest:
    source = Path(path)
    raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("request config root must be a JSON object")

    turns_raw = raw.get("turns")
    if not isinstance(turns_raw, list):
        raise ValueError("turns must be a JSON array")

    voices = raw.get("voices")
    if not isinstance(voices, dict):
        raise ValueError("voices must be a JSON object")

    turns = tuple(
        DialogueTurn(
            text=item["text"],
            speaker=item.get("speaker"),
            style=item.get("style"),
        )
        for item in turns_raw
        if isinstance(item, dict)
    )
    if len(turns) != len(turns_raw):
        raise ValueError("every turn must be a JSON object")

    return VoiceRequest(
        model=raw["model"],
        turns=turns,
        voices=voices,
        output_mime_type=raw.get("output_mime_type", "audio/wav"),
    )


def write_bytes_atomic(path: str | Path, data: bytes) -> Path:
    """Write bytes in the destination directory and replace atomically."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(target.parent),
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise
    return target
