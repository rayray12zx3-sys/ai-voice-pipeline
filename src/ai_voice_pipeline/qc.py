"""Offline technical QC for PCM WAV output."""

from __future__ import annotations

from array import array
from dataclasses import asdict, dataclass
import io
from pathlib import Path
import sys
import wave


DEFAULT_SAMPLE_RATE = 24_000
DEFAULT_CHANNELS = 1
DEFAULT_SAMPLE_WIDTH_BYTES = 2


@dataclass(frozen=True)
class WavMetadata:
    sample_rate: int
    channels: int
    sample_width_bytes: int
    frame_count: int
    duration_seconds: float
    compression_type: str
    peak_abs_sample: int | None
    full_scale_sample_count: int | None


@dataclass(frozen=True)
class QCResult:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    metadata: WavMetadata | None

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "metadata": asdict(self.metadata) if self.metadata else None,
        }


def _scan_pcm16(handle: wave.Wave_read) -> tuple[int, int]:
    peak = 0
    full_scale = 0
    while True:
        raw = handle.readframes(4096)
        if not raw:
            break
        samples = array("h")
        samples.frombytes(raw)
        if sys.byteorder != "little":
            samples.byteswap()
        for sample in samples:
            magnitude = abs(sample)
            if magnitude > peak:
                peak = magnitude
            if sample in (-32768, 32767):
                full_scale += 1
    return peak, full_scale


def inspect_wav_bytes(data: bytes) -> WavMetadata:
    if not isinstance(data, (bytes, bytearray)) or not data:
        raise ValueError("audio data must be non-empty bytes")

    try:
        with wave.open(io.BytesIO(data), "rb") as handle:
            channels = handle.getnchannels()
            sample_width = handle.getsampwidth()
            sample_rate = handle.getframerate()
            frame_count = handle.getnframes()
            compression = handle.getcomptype()
            duration = frame_count / sample_rate if sample_rate else 0.0
            peak = full_scale = None
            if compression == "NONE" and sample_width == 2:
                peak, full_scale = _scan_pcm16(handle)
    except (wave.Error, EOFError) as exc:
        raise ValueError("invalid or unsupported WAV container") from exc

    return WavMetadata(
        sample_rate=sample_rate,
        channels=channels,
        sample_width_bytes=sample_width,
        frame_count=frame_count,
        duration_seconds=duration,
        compression_type=compression,
        peak_abs_sample=peak,
        full_scale_sample_count=full_scale,
    )


def qc_wav_bytes(
    data: bytes,
    *,
    expected_sample_rate: int = DEFAULT_SAMPLE_RATE,
    expected_channels: int = DEFAULT_CHANNELS,
    expected_sample_width_bytes: int = DEFAULT_SAMPLE_WIDTH_BYTES,
) -> QCResult:
    try:
        metadata = inspect_wav_bytes(data)
    except ValueError:
        return QCResult(False, ("INVALID_WAV",), (), None)

    errors: list[str] = []
    warnings: list[str] = []

    if metadata.compression_type != "NONE":
        errors.append("WAV_NOT_PCM")
    if metadata.sample_rate != expected_sample_rate:
        errors.append("UNEXPECTED_SAMPLE_RATE")
    if metadata.channels != expected_channels:
        errors.append("UNEXPECTED_CHANNEL_COUNT")
    if metadata.sample_width_bytes != expected_sample_width_bytes:
        errors.append("UNEXPECTED_SAMPLE_WIDTH")
    if metadata.frame_count <= 0 or metadata.duration_seconds <= 0:
        errors.append("EMPTY_AUDIO")
    if metadata.full_scale_sample_count:
        warnings.append("FULL_SCALE_SAMPLES_PRESENT")

    return QCResult(not errors, tuple(errors), tuple(warnings), metadata)


def qc_wav_file(path: str | Path) -> QCResult:
    return qc_wav_bytes(Path(path).read_bytes())
