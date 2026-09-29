# Integration notes for ai-video-template-v2

This repository must remain independently testable before integration.

## Intended boundary

`ai-video-template-v2` already models an `AUDIO_GENERATE` execution operation. The future integration should treat this repository as an audio provider/execution layer rather than embedding Gemini-specific fields into canonical shot semantics.

Target flow:

```text
canonical voice intent
        ↓
AUDIO_GENERATE ticket
        ↓
voice provider routing
        ↓
ai-voice-pipeline
        ↓
WAV + provider receipt
        ↓
materialized audio asset
        ↓
Audio QC
        ↓
video/lip-sync/post workflow
```

## What should stay provider-neutral

- character/voice alias
- language
- delivery intent
- dialogue text
- timing intent
- QC requirements

## What should stay adapter-local

- Gemini model code
- Gemini prebuilt voice name
- Gemini custom voice ID
- API request schema
- API authentication
- provider response fields

## Integration gate

Do not merge this project into `ai-video-template-v2` until:

1. Offline tests pass.
2. One single-speaker Gemini smoke test succeeds.
3. One English/Taiwan Traditional Chinese test succeeds.
4. One two-speaker test succeeds.
5. Receipts contain no secrets.
6. Audio QC requirements are defined.
7. Failure/retry behavior is explicit.
