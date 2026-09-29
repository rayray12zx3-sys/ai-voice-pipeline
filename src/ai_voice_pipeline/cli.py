"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

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

    qc = sub.add_parser("qc", help="Run offline technical QC on a WAV file")
    qc.add_argument("audio", help="WAV file")

    verify = sub.add_parser("verify", help="Verify a receipt against materialized audio")
    verify.add_argument("receipt", help="Receipt JSON")
    verify.add_argument("audio", help="Audio file referenced by the receipt")

    return parser


def _render(args: argparse.Namespace) -> int:
    request = load_request(args.config)
    provider = get_provider(args.provider)
    payload = provider.build_payload(request)

    if not args.execute:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY is required with --execute", file=sys.stderr)
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
