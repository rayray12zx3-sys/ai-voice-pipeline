# Voice identity model

## Principle

Character identity and provider voice identity are different concepts.

Use a stable logical alias:

```text
STUDENT_VOICE_V1
```

and keep the provider mapping outside canonical character semantics:

```text
STUDENT_VOICE_V1
  -> provider: GEMINI
  -> provider voice: Kore / voice_...
```

## Why

This allows:

- replacing Gemini with another TTS provider,
- A/B testing voices,
- changing a provider custom-voice ID,
- regenerating audio without rewriting story/character identity,
- auditing which provider binding produced a specific output.

## Future binding record

A future binding should include:

- logical alias
- provider
- provider voice identifier
- language/region intent
- selection provenance
- created/verified timestamp
- optional consent/provenance reference for replicated voices

Do not store raw consent audio, API credentials, or private reference media in this public repository.

## Voice replication

Replication remains deferred. Before implementation, define:

- explicit consent requirements,
- provenance storage,
- allowed use scope,
- deletion/retention handling,
- provider TTL behavior,
- audit evidence.

A reference recording alone must never be treated as consent.
