# AI Voice Pipeline

[![CI](https://github.com/rayray12zx3-sys/ai-voice-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/rayray12zx3-sys/ai-voice-pipeline/actions/workflows/ci.yml)

Provider-neutral AI voice/TTS pipeline, starting with Google Gemini TTS.

## Status

**Phase:** R0 offline foundation complete / R1 live validation pending

This repository is intentionally separate from `ai-video-template`. R0 now provides a CI-validated, network-safe foundation; the next gate is deliberate live Gemini validation before any integration into the larger video pipeline.

## Current scope

- Gemini 3.8 Flash TTS
- Gemini 3.8 Flash-Lite TTS
- Single-speaker generation
- Two-speaker conversational generation
- Provider-neutral request contract
- JSON Schema for request configs
- Dry-run payload generation by default
- Explicit opt-in API execution
- Atomic WAV materialization
- Offline WAV technical QC
- SHA-256 receipt generation and verification
- Python 3.11–3.14 CI matrix
- Offline unit tests

## Next gated work

- [R1 live Gemini validation](https://github.com/rayray12zx3-sys/ai-voice-pipeline/issues/2)
- [R2 semantic/editorial Audio QC](https://github.com/rayray12zx3-sys/ai-voice-pipeline/issues/3)
- [R3 provider-neutral voice identity](https://github.com/rayray12zx3-sys/ai-voice-pipeline/issues/4)
- [R4 ai-video-template integration](https://github.com/rayray12zx3-sys/ai-voice-pipeline/issues/5)
- [License decision](https://github.com/rayray12zx3-sys/ai-voice-pipeline/issues/6)

## Not in scope yet

- Voice replication / voice cloning
- Lip sync
- Premiere / After Effects automation
- Transcript/pronunciation Audio QC
- Integration into `ai-video-template`

## Safety defaults

- No API call occurs unless `--execute` is explicitly supplied.
- `GEMINI_API_KEY` is read only from the environment.
- Missing API credentials fail before a provider request.
- Core tests are offline and do not contact Google.
- Generated audio must pass technical WAV QC before it is materialized as the requested output.
- Receipts contain hashes and technical metadata, not API keys or transcript text.
- Generated media, receipts and environment files are ignored by Git.

## Requirements

- Windows / macOS / Linux
- Python 3.11+
- No administrator rights required

## Install

Offline development:

```powershell
python -m pip install -e . --no-deps
```

Gemini execution support:

```powershell
python -m pip install -e ".[gemini]"
```

The Gemini optional dependency requires `google-genai>=2.25.0,<3`, matching the current SDK baseline needed by the Gemini 3.8 voice ecosystem.

## Dry-run first

Single speaker:

```powershell
ai-voice render examples/single-speaker.json
```

Two speakers:

```powershell
ai-voice render examples/dialogue.json
```

Dry-run prints the provider request and makes no network call.

## Execute deliberately

```powershell
$env:GEMINI_API_KEY = "..."
ai-voice render examples/single-speaker.json --execute --out output/narration.wav
```

A successful execution writes:

- the WAV file
- `<wav>.receipt.json` with provider/model/request/output hashes
- technical QC metadata

R0 expects Gemini 3.8 unary default WAV output: **24 kHz, mono, 16-bit PCM**.

## QC an existing WAV

```powershell
ai-voice qc output/narration.wav
```

## Verify materialization

```powershell
ai-voice verify output/narration.wav.receipt.json output/narration.wav
```

This detects replaced or corrupted output.

## Offline validation

```powershell
python -m compileall -q src tests
python -m unittest discover -s tests -v
git diff --check
```

Windows helper:

```powershell
.\scripts\validate.ps1
```

## Architecture

```text
JSON config
   ↓
VoiceRequest
   ↓
provider-neutral validation
   ↓
provider registry
   ↓
Gemini adapter
   ├─ dry-run → request payload only
   └─ execute → Gemini Interactions API
                 ↓
            in-memory WAV
                 ↓
          technical Audio QC
                 ↓
        atomic materialization
                 ↓
          SHA-256 receipt
```

See:

- [Architecture](docs/ARCHITECTURE.md)
- [Operations](docs/OPERATIONS.md)
- [Provider evidence](docs/PROVIDER-EVIDENCE.md)
- [Future integration boundary](docs/INTEGRATION-NOTES.md)
- [Roadmap](ROADMAP.md)

## Future integration

The intended `ai-video-template` boundary is:

```text
AUDIO_GENERATE ticket
        ↓
voice provider routing
        ↓
ai-voice-pipeline
        ↓
WAV + receipt
        ↓
Audio QC / asset materialization
        ↓
video / lip-sync / post workflow
```

Canonical video-project state should describe voice intent and logical voice aliases, not hard-code a Gemini-specific voice ID.

## Repository visibility and license

This repository is public. Do not commit company/private scripts, real credentials, or private voice reference/consent audio.

No open-source license has been selected yet. Until one is selected, normal copyright applies.
