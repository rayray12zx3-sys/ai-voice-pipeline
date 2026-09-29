"""Minimal local receipt for generated audio."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .contracts import VoiceRequest
from .providers.gemini import GeminiTTSProvider


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_json(value: object) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return _sha256_bytes(raw)


def build_receipt(request: VoiceRequest, audio: bytes, output_path: str | Path) -> dict:
    payload = GeminiTTSProvider.build_payload(request)
    return {
        "schema_version": "0.1",
        "provider": GeminiTTSProvider.provider_name,
        "model": request.model,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "request_sha256": _sha256_json(payload),
        "output_sha256": _sha256_bytes(audio),
        "output_path": str(output_path),
        "output_mime_type": request.output_mime_type,
    }


def write_receipt(path: str | Path, receipt: dict) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target
