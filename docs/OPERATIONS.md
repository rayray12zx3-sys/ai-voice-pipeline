# Operations

## 1. Offline validation

```powershell
python -m pip install -e . --no-deps
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

## 2. Dry-run a request

```powershell
ai-voice render examples/single-speaker.json
```

No network call occurs.

## 3. QC an existing WAV

```powershell
ai-voice qc path\to\audio.wav
```

R0 expects the Gemini 3.8 unary default: 24 kHz, mono, 16-bit PCM WAV.

## 4. Real Gemini execution

Install the optional provider dependency:

```powershell
python -m pip install -e ".[gemini]"
$env:GEMINI_API_KEY = "..."
ai-voice render examples/single-speaker.json --execute --out output\narration.wav
```

Execution writes the WAV only after the API returns decodable bytes, runs local WAV QC, and writes a receipt containing hashes and technical metadata. The API key is not included in the receipt.

## 5. Verify materialized output

```powershell
ai-voice verify output\narration.wav.receipt.json output\narration.wav
```

This detects output replacement/corruption after generation.

## Fail-closed boundaries

The CLI exits non-zero when:

- the request config is invalid,
- `--execute` is used without `GEMINI_API_KEY`,
- Gemini returns unusable audio,
- generated WAV fails required technical QC,
- receipt verification detects a mismatch.
