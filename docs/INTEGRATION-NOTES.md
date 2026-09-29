# Integration notes for ai-video-template-v2

This repository must remain independently testable before integration.

## Intended boundary

`ai-video-template-v2` already models an `AUDIO_GENERATE` execution operation. Future integration should treat this repository as an audio provider/execution layer rather than embedding Gemini-specific fields into canonical shot semantics.

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
- transcript/dialogue text
- delivery intent
- timing intent
- QC requirements
- expected output role

## What should stay adapter-local

- Gemini model code
- Gemini prebuilt/custom voice identifier
- Interactions API request schema
- API authentication
- provider-specific response fields
- future provider-specific retry semantics

## Receipt mapping

The current local receipt is not automatically a canonical `ai-video-template-v2` receipt. Integration must explicitly map and validate fields rather than copying the JSON wholesale.

At minimum, the integration layer should bind:

- generation ticket identity
- provider/runtime/capability evidence
- request fingerprint
- materialized output hash
- output media metadata
- QC result
- provider task/trace identifiers when available

## Voice identity rule

A canonical character should reference a logical voice alias such as `STUDENT_VOICE_V1`.

A provider binding can map that alias to a Gemini prebuilt/custom voice. The Gemini voice ID itself should not become the character's canonical identity.

## Lip-sync rule

Lip sync is a downstream media operation, not part of TTS generation. Keep it as a separate ticket/adapter step so audio can be regenerated or routed to a different lip-sync provider independently.

## Integration gate

Do not merge this project into `ai-video-template-v2` until:

1. Hosted/offline validation evidence is current.
2. One Traditional Chinese single-speaker Gemini smoke test succeeds.
3. One English single-speaker Gemini smoke test succeeds.
4. One two-speaker Gemini smoke test succeeds.
5. Generated WAV imports correctly in Premiere Pro.
6. Receipts contain no secrets or transcript text.
7. Audio QC requirements beyond container/format validation are defined.
8. Failure/retry/stop-loss behavior is explicit.
