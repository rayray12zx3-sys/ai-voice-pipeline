# AI Voice Pipeline

Provider-neutral AI voice/TTS pipeline, starting with Google Gemini TTS.

## Status

**Phase:** foundation / safe dry-run

This repository is intentionally separate from `ai-video-template-v2`. The first goal is to validate a small, auditable voice-generation workflow before integrating it into the larger video pipeline.

## Current scope

- Gemini 3.8 Flash TTS
- Gemini 3.8 Flash-Lite TTS
- Single-speaker generation
- Two-speaker conversational generation
- Provider-neutral request contract
- Dry-run payload generation by default
- Optional explicit API execution
- WAV materialization
- SHA-256 receipt generation
- Offline unit tests

## Not in scope yet

- Voice replication / voice cloning
- Lip sync
- Premiere / After Effects automation
- Automatic Audio QC
- Hosted CI
- Integration into `ai-video-template-v2`

## Safety defaults

- No API call occurs unless `--execute` is explicitly supplied.
- `GEMINI_API_KEY` is read only from the environment.
- Secrets must never be committed.
- Tests are offline and do not contact Google.
- Generated media and receipts are ignored by Git by default.

## Requirements

- Windows / macOS / Linux
- Python 3.11+
- No administrator rights required

## Install

Offline development:

```powershell
python -m pip install -e .
```

Gemini execution support:

```powershell
python -m pip install -e ".[gemini]"
```

Set the API key only when you are ready to execute:

```powershell
$env:GEMINI_API_KEY = "..."
```

## Dry-run first

```powershell
ai-voice examples/single-speaker.json
```

This prints the request that would be sent but does not call Gemini.

Two-speaker example:

```powershell
ai-voice examples/dialogue.json
```

## Execute deliberately

```powershell
ai-voice examples/single-speaker.json --execute --out output/narration.wav
```

The command writes:

- the WAV file
- a JSON receipt with provider/model/request hash/output hash

## Test

```powershell
python -m unittest discover -s tests -v
```

## Architecture

```text
JSON config
   ↓
VoiceRequest
   ↓
Provider-neutral validation
   ↓
Gemini adapter
   ├─ dry-run → request payload only
   └─ execute → Gemini API
                 ↓
               WAV
                 ↓
             receipt
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/INTEGRATION-NOTES.md](docs/INTEGRATION-NOTES.md).

## Future integration

The intended integration boundary with `ai-video-template-v2` is:

```text
AUDIO_GENERATE ticket
        ↓
ai-voice-pipeline
        ↓
WAV + receipt
        ↓
audio asset / QC
```

The canonical video project should describe voice intent, not hard-code a Gemini-specific voice ID.

## License

No open-source license has been selected yet.
