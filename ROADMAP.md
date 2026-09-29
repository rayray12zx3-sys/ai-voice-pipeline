# Roadmap

## R0 — Foundation and hardening

- [x] Independent repository
- [x] Provider-neutral request contract
- [x] Gemini payload adapter
- [x] Provider registry boundary
- [x] JSON request schema
- [x] Dry-run CLI by default
- [x] Explicit execution gate
- [x] API-key preflight before network use
- [x] Atomic WAV materialization
- [x] SHA-256 output receipt
- [x] Receipt/output verification
- [x] Offline WAV technical QC
- [x] Offline unit-test suite
- [x] GitHub CI workflow for Python 3.11–3.14
- [x] Public-repository security guidance
- [x] Current Gemini provider-evidence note
- [x] Hosted CI observed green on hardening PR #1 — run 36600912339; Python 3.11/3.12/3.13/3.14 all passed compile, unit tests and diff check

R0 offline/foundation scope is complete. This does **not** imply live Gemini API, pronunciation quality, Premiere import, or downstream lip-sync validation.

## R1 — Real Gemini smoke tests

Requires deliberate approval to use API quota and a real `GEMINI_API_KEY`.

- [ ] Single-speaker Traditional Chinese narration
- [ ] Single-speaker English dialogue
- [ ] Two-speaker conversational dialogue
- [ ] Confirm returned WAV is 24 kHz / mono / 16-bit PCM
- [ ] Verify WAV imports correctly in Premiere Pro
- [ ] Record exact SDK/model/voice behavior
- [ ] Confirm receipt contains no secret or transcript text

## R2 — Audio QC

Offline technical QC is already in R0. R2 adds semantic/creative checks.

- [ ] Duration / leading/trailing silence policy
- [ ] Transcript-vs-source verification
- [ ] Language/pronunciation checks
- [ ] Loudness policy for downstream editing
- [ ] Human creative review fields
- [ ] Retry/stop-loss policy

## R3 — Voice identity

- [ ] Provider-neutral voice aliases
- [ ] Extended Voice Library discovery
- [ ] Voice Design experiment
- [ ] Voice selection metadata/provenance
- [ ] Consent and provenance policy before any voice replication work

## R4 — ai-video-template-v2 integration

Do not start until R1 evidence exists.

- [ ] Map to `AUDIO_GENERATE`
- [ ] Capability snapshot contract
- [ ] Execution receipt mapping
- [ ] Materialized audio asset mapping
- [ ] Audio QC gate mapping
- [ ] Lip-sync routing as a separate downstream operation
- [ ] Keep provider voice IDs outside canonical character identity

## Deferred

- Voice replication
- Automatic lip sync
- Premiere automation
- Streaming TTS
- Non-WAV output formats
