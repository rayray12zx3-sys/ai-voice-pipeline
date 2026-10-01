# Handoff contract for ai-video-template

Until direct integration exists, `ai-voice-pipeline` acts as an external audio execution subsystem. It may generate and validate audio, but it does not own canonical production state.

An approved audio asset handed to `ai-video-template` should carry:

- stable `asset_id`
- script segment ID and script revision
- speaker alias and provider-neutral logical voice alias
- transcript and delivery/style intent
- provider, model and provider voice binding
- execution surface
- provider task/trace ID when actually supplied; otherwise explicit `UNKNOWN`
- duration
- sample rate, channel count and bit depth
- SHA-256 of the materialized audio
- durable locator outside the public repository
- technical/semantic QC status
- human approval status

## Boundary

```text
ai-video-template
   ↓ voice intent / AUDIO_GENERATE
external execution
   ↓
ai-voice-pipeline or approved Web workflow
   ↓
WAV + handoff metadata
   ↓
ai-video-template canonical adoption
```

The local receipt produced by this repository is supporting evidence. It must be mapped into the canonical `ai-video-template` contracts rather than treated as canonical state by itself.

Lip sync remains a downstream media operation and is not part of the TTS handoff.
