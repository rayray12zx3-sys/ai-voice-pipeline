"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .io import load_request, write_bytes
from .providers.gemini import GeminiTTSProvider
from .receipt import build_receipt, write_receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI Voice Pipeline")
    parser.add_argument("config", help="JSON request configuration")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually call Gemini. Without this flag the command is dry-run only.",
    )
    parser.add_argument("--out", default="output/out.wav", help="Output WAV path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    request = load_request(args.config)
    payload = GeminiTTSProvider.build_payload(request)

    if not args.execute:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is required with --execute")

    audio = GeminiTTSProvider.generate(request)
    output = write_bytes(args.out, audio)
    receipt = build_receipt(request, audio, output)
    receipt_path = Path(str(output) + ".receipt.json")
    write_receipt(receipt_path, receipt)

    print(str(output))
    print(str(receipt_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
