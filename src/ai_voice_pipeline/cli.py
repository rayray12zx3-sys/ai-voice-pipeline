"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .casting import load_casting_plan, safe_filename
from .io import load_request, write_bytes_atomic
from .providers.registry import get_provider, provider_names
from .qc import qc_wav_bytes, qc_wav_file
from .receipt import build_receipt, load_receipt, verify_output, write_receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Voice Pipeline")
    sub = parser.add_subparsers(dest="command", required=True)

    render = sub.add_parser("render", help="Validate/dry-run or execute a TTS request")
    render.add_argument("config", help="JSON request configuration")
    render.add_argument(
        "--provider",
        default="GEMINI",
        choices=provider_names(),
        help="Voice provider",
    )
    render.add_argument(
        "--execute",
        action="store_true",
        help="Actually call the provider. Omit for a network-free dry-run.",
    )
    render.add_argument("--out", default="output/out.wav", help="Output WAV path")

    voices = sub.add_parser(
        "voices",
        help="List voices available to the live provider project",
    )
    voices.add_argument(
        "--provider",
        default="GEMINI",
        choices=provider_names(),
        help="Voice provider",
    )
    voices.add_argument("--language-code", action="append", default=[])
    voices.add_argument("--gender", action="append", default=[])
    voices.add_argument("--pitch", action="append", default=[])
    voices.add_argument("--context", action="append", default=[])
    voices.add_argument(
        "--type",
        dest="voice_type",
        action="append",
        default=[],
        help="Voice type filter such as prebuilt, prompted or replicated. "
        "Defaults to prebuilt.",
    )
    voices.add_argument("--search")
    voices.add_argument("--page-size", type=int, default=200)
    voices.add_argument(
        "--json",
        action="store_true",
        help="Emit normalized JSON instead of a compact text table.",
    )

    cast = sub.add_parser(
        "cast",
        help="Dry-run or generate comparable audition WAVs for one casting plan",
    )
    cast.add_argument("config", help="Casting-plan JSON")
    cast.add_argument(
        "--provider",
        default="GEMINI",
        choices=provider_names(),
        help="Voice provider",
    )
    cast.add_argument(
        "--execute",
        action="store_true",
        help="Actually generate every audition candidate. Omit for dry-run.",
    )
    cast.add_argument(
        "--out-dir",
        default="output/casting",
        help="Root directory for audition WAVs, receipts and manifest",
    )

    qc = sub.add_parser("qc", help="Run offline technical QC on a WAV file")
    qc.add_argument("audio", help="WAV file")

    verify = sub.add_parser("verify", help="Verify a receipt against materialized audio")
    verify.add_argument("receipt", help="Receipt JSON")
    verify.add_argument("audio", help="Audio file referenced by the receipt")

    return parser


def _require_gemini_key() -> bool:
    if os.environ.get("GEMINI_API_KEY"):
        return True
    print("ERROR: GEMINI_API_KEY is required for live Gemini access", file=sys.stderr)
    return False


def _render(args: argparse.Namespace) -> int:
    request = load_request(args.config)
    provider = get_provider(args.provider)
    payload = provider.build_payload(request)

    if not args.execute:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.provider == "GEMINI" and not _require_gemini_key():
        return 2

    output = Path(args.out)
    if output.suffix.lower() != ".wav":
        print("ERROR: R0 execution requires a .wav output path", file=sys.stderr)
        return 2

    audio = provider.generate(request)
    qc = qc_wav_bytes(audio)
    if not qc.ok:
        print(json.dumps(qc.to_dict(), ensure_ascii=False, indent=2), file=sys.stderr)
        print("ERROR: generated audio failed technical QC; output was not materialized", file=sys.stderr)
        return 2

    output = write_bytes_atomic(output, audio)
    receipt = build_receipt(request, audio, output, qc=qc.to_dict())
    receipt_path = Path(str(output) + ".receipt.json")
    write_receipt(receipt_path, receipt)

    print(str(output))
    print(str(receipt_path))
    return 0


def _voices(args: argparse.Namespace) -> int:
    if args.page_size < 1 or args.page_size > 1000:
        raise ValueError("--page-size must be between 1 and 1000")
    if args.provider == "GEMINI" and not _require_gemini_key():
        return 2

    provider = get_provider(args.provider)
    voices = provider.list_voices(
        language_code=tuple(args.language_code),
        gender=tuple(args.gender),
        pitch=tuple(args.pitch),
        contexts=tuple(args.context),
        type_=tuple(args.voice_type or ["prebuilt"]),
        search=args.search,
        page_size=args.page_size,
    )
    if args.json:
        print(json.dumps(list(voices), ensure_ascii=False, indent=2))
        return 0

    for voice in voices:
        parts = [
            str(voice.get("id") or "UNKNOWN"),
            str(voice.get("display_name") or ""),
            str(voice.get("language_code") or ""),
            str(voice.get("accent") or ""),
            str(voice.get("gender") or ""),
            str(voice.get("pitch") or ""),
            str(voice.get("description") or ""),
        ]
        print(" | ".join(parts))
    return 0


def _cast(args: argparse.Namespace) -> int:
    plan = load_casting_plan(args.config)
    provider = get_provider(args.provider)

    dry_run = {
        **plan.safe_summary(),
        "status": "AUDITION",
        "candidates": [
            {
                "voice_id": voice_id,
                "payload": provider.build_payload(plan.request_for(voice_id)),
            }
            for voice_id in plan.candidates
        ],
    }
    if not args.execute:
        print(json.dumps(dry_run, ensure_ascii=False, indent=2))
        return 0

    if args.provider == "GEMINI" and not _require_gemini_key():
        return 2

    root = Path(args.out_dir) / safe_filename(plan.role)
    root.mkdir(parents=True, exist_ok=True)
    results = []

    for voice_id in plan.candidates:
        request = plan.request_for(voice_id)
        audio = provider.generate(request)
        qc = qc_wav_bytes(audio)
        if not qc.ok:
            results.append({
                "voice_id": voice_id,
                "status": "TECHNICAL_QC_FAILED",
                "qc": qc.to_dict(),
            })
            continue

        stem = safe_filename(voice_id)
        output = write_bytes_atomic(root / f"{stem}.wav", audio)
        receipt = build_receipt(request, audio, output, qc=qc.to_dict())
        receipt_path = Path(str(output) + ".receipt.json")
        write_receipt(receipt_path, receipt)
        results.append({
            "voice_id": voice_id,
            "status": "AUDITION",
            "output": str(output),
            "receipt": str(receipt_path),
            "qc": qc.to_dict(),
        })

    manifest = {
        "schema_version": "0.1",
        "kind": "VOICE_CASTING",
        "approval_status": "AUDITION",
        **plan.safe_summary(),
        "results": results,
    }
    manifest_path = root / "casting-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(str(manifest_path))
    return 0 if all(item["status"] == "AUDITION" for item in results) else 2


def _qc(args: argparse.Namespace) -> int:
    result = qc_wav_file(args.audio)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.ok else 2


def _verify(args: argparse.Namespace) -> int:
    receipt = load_receipt(args.receipt)
    audio = Path(args.audio).read_bytes()
    ok, errors = verify_output(receipt, audio)
    result = {"ok": ok, "errors": list(errors)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 2


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "render":
            return _render(args)
        if args.command == "voices":
            return _voices(args)
        if args.command == "cast":
            return _cast(args)
        if args.command == "qc":
            return _qc(args)
        if args.command == "verify":
            return _verify(args)
        raise RuntimeError("unreachable command")
    except (OSError, ValueError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
