# Gemini provider evidence

Captured: 2026-09-29

Authoritative sources:

- https://ai.google.dev/gemini-api/docs/speech-generation
- https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash-tts
- https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash-lite-tts
- https://ai.google.dev/gemini-api/docs/changelog

## Facts used by R0

- Current model codes are `gemini-3.8-flash-tts` and `gemini-3.8-flash-lite-tts`.
- The models share the same TTS request schema.
- The current primary examples use the Interactions API.
- Per-turn sustained delivery instructions belong in `speech_metadata.style`.
- Multi-speaker requests require explicit `speech_metadata.speaker` values.
- Single-request multi-speaker generation supports up to 2 speakers.
- Google documents single-request multi-speaker generation as using prebuilt voices. R0 therefore fails closed to the 30 curated Studio prebuilt voice names for conversational mode.
- Custom designed/replicated voices remain allowed by the R0 contract for single-speaker requests only.
- Unary default output is a complete WAV file.
- Default unary WAV characteristics are 24 kHz, mono, 16-bit signed little-endian PCM.
- Extended Voice Library access with the Python SDK requires `google-genai` 2.25.0 or newer.

## Conservative implementation choices

The live API may support additional prebuilt catalog voices beyond the 30 curated Studio names. R0 deliberately uses the smaller documented allowlist for multi-speaker mode because the repository has not yet performed a live Voice Library capability probe.

This file is evidence documentation, not a live capability probe. Real execution still requires a fresh smoke test.
