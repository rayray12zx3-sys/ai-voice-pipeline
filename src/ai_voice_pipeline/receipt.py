"""Minimal auditable receipt for generated audio."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from .contracts import VoiceRequest
from .providers.gemini import GeminiTTSProvider


RECEIPT_SCHEMA_VERSION = "0.2"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_json(value: object) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256_bytes(raw)


def build_receipt(
    request: VoiceRequest,
    audio: bytes,
    output_path: str | Path,
    *,
    qc: dict | None = None,
) -> dict:
    payload = GeminiTTSProvider.build_payload(request)
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "provider": GeminiTTSProvider.provider_name,
        "model": request.model,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "request_sha256": sha256_json(payload),
        "output_sha256": sha256_bytes(audio),
        "output_size_bytes": len(audio),
        "output_path": str(output_path),
        "output_mime_type": request.output_mime_type,
        "request_summary": request.safe_summary(),
        "qc": qc,
    }


def verify_output(receipt: dict, audio: bytes) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    if receipt.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        errors.append("RECEIPT_SCHEMA_MISMATCH")
    expected = receipt.get("output_sha256")
    if not isinstance(expected, str) or expected != sha256_bytes(audio):
        errors.append("OUTPUT_HASH_MISMATCH")
    if receipt.get("output_size_bytes") != len(audio):
        errors.append("OUTPUT_SIZE_MISMATCH")
    return not errors, tuple(errors)


def write_receipt(path: str | Path, receipt: dict) -> Path:
    from .io import write_bytes_atomic

    encoded = (
        json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode("utf-8")
    return write_bytes_atomic(path, encoded)


def load_receipt(path: str | Path) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("receipt root must be an object")
    return value
