# Architecture

## Goal

Keep voice intent provider-neutral while isolating Gemini-specific API details inside one adapter.

## Layers

1. **Request contract**
   - model
   - transcript turns
   - logical speaker names
   - voice bindings
   - turn-level style
   - requested audio format

2. **Provider adapter**
   - converts the neutral request into Gemini's current TTS request shape
   - does not execute during payload compilation

3. **Execution**
   - requires an explicit `--execute` flag
   - requires `GEMINI_API_KEY`
   - imports the Google SDK lazily

4. **Materialization**
   - writes returned audio bytes directly
   - creates a local JSON receipt with SHA-256 hashes

## Deliberate limitations

- Single-request multi-speaker mode is limited to two speakers.
- Voice replication is not implemented.
- No provider-specific voice ID is intended to become canonical character identity.
- No network validation runs during unit tests.

## Future provider-neutral shape

A future version may generalize the current contract so that:

```text
VoiceIntent
   ↓
VoiceRouter
   ├─ Gemini
   ├─ ElevenLabs
   └─ Local TTS
```

The request contract should remain stable even if providers change.
