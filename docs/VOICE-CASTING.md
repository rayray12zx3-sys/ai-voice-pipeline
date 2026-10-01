# Voice Casting

Voice Casting is an audition workflow. It selects a provider-neutral logical voice identity without turning audition files into production-approved assets.

## 1. Discover the live Gemini Voice Library

The catalog comes from the current API project instead of a hard-coded UI list.

```powershell
$env:GEMINI_API_KEY = "..."
ai-voice voices --type prebuilt --page-size 500 --json
```

Optional filters:

```powershell
ai-voice voices --language-code zh-TW --context Conversational --type prebuilt --json
ai-voice voices --search warm --type prebuilt --json
```

Do not assume Google AI Studio and the API catalog expose identical labels at every moment. Treat the live API response as provider evidence for this pipeline.

## 2. Create a casting plan

Example:

```json
{
  "role": "MOM",
  "logical_voice_alias": "MOM_VOICE_V1",
  "model": "gemini-3.8-flash-tts",
  "text": "這是一句固定的試音句。",
  "style": "Natural Taiwanese Mandarin. Warm and conversational.",
  "candidates": [
    "VOICE_ID_FROM_LIVE_CATALOG_1",
    "VOICE_ID_FROM_LIVE_CATALOG_2"
  ]
}
```

Use the exact same text, style and model for every candidate in one plan. That keeps the A/B comparison fair.

## 3. Dry-run first

```powershell
ai-voice cast casting-mom.json
```

Dry-run prints each provider payload but makes no network call.

## 4. Generate audition WAVs deliberately

```powershell
ai-voice cast casting-mom.json --execute --out-dir output/casting
```

For each candidate, the command:

1. performs one TTS request
2. runs offline technical WAV QC
3. materializes the WAV atomically only after QC passes
4. writes the existing SHA-256 receipt
5. records the candidate in `casting-manifest.json`

The manifest is always marked:

```text
kind = VOICE_CASTING
approval_status = AUDITION
```

Audition output is not a canonical `ai-video-template` asset and must not be marked APPROVED merely because technical QC passed.

## 5. Human selection

Compare candidates using a stable rubric such as:

- Taiwan Mandarin / target accent naturalness
- role and age fit
- non-announcer / non-synthetic quality
- emotional control
- intelligibility at fast social-ad pacing
- consistency
- overall role fit

After selection, keep the canonical identity provider-neutral:

```text
MOM_VOICE_V1
  -> current provider binding: <Gemini voice ID>
```

The Gemini voice ID is a provider binding, not the canonical character identity.

## Security

- Never commit `GEMINI_API_KEY`.
- Generated audition WAVs and local manifests stay outside the public repository.
- Do not place private production scripts or company media in this public repository.
