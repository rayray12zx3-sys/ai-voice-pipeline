"""Voice-casting plans and audition helpers."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from .contracts import DialogueTurn, VoiceRequest


_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(value: str) -> str:
    cleaned = _SAFE.sub("-", value.strip()).strip("-._")
    if not cleaned:
        raise ValueError("voice identifier cannot produce an empty filename")
    return cleaned[:120]


@dataclass(frozen=True)
class CastingPlan:
    role: str
    logical_voice_alias: str
    model: str
    text: str
    style: str | None
    candidates: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (
            ("role", self.role),
            ("logical_voice_alias", self.logical_voice_alias),
            ("model", self.model),
            ("text", self.text),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if self.style is not None and (not isinstance(self.style, str) or not self.style.strip()):
            raise ValueError("style must be a non-empty string when supplied")
        if not self.candidates:
            raise ValueError("at least one casting candidate is required")
        if len(set(self.candidates)) != len(self.candidates):
            raise ValueError("casting candidates must be unique")
        if any(not isinstance(item, str) or not item.strip() for item in self.candidates):
            raise ValueError("casting candidate IDs must be non-empty strings")

    @property
    def test_fingerprint(self) -> str:
        payload = {
            "model": self.model,
            "text": self.text,
            "style": self.style,
        }
        raw = json.dumps(
            payload,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def request_for(self, voice_id: str) -> VoiceRequest:
        if voice_id not in self.candidates:
            raise ValueError(f"voice is not in casting plan: {voice_id}")
        return VoiceRequest(
            model=self.model,
            turns=(DialogueTurn(self.text, style=self.style),),
            voices={self.logical_voice_alias: voice_id},
        )

    def safe_summary(self) -> dict:
        return {
            "role": self.role,
            "logical_voice_alias": self.logical_voice_alias,
            "model": self.model,
            "candidate_count": len(self.candidates),
            "test_fingerprint": self.test_fingerprint,
        }


def load_casting_plan(path: str | Path) -> CastingPlan:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("casting config root must be a JSON object")
    candidates = raw.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a JSON array")
    return CastingPlan(
        role=raw["role"],
        logical_voice_alias=raw["logical_voice_alias"],
        model=raw["model"],
        text=raw["text"],
        style=raw.get("style"),
        candidates=tuple(candidates),
    )
