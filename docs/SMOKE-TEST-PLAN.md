# Live Gemini smoke-test plan

This plan is intentionally separate from offline CI. Do not run it automatically.

## Preconditions

- R0 offline CI is green.
- Operator has consciously decided to use Gemini API quota.
- `google-genai>=2.25.0,<3` is installed.
- `GEMINI_API_KEY` is present only in the process/user environment.
- Test scripts contain no private/company text.

## Case A — Traditional Chinese narration

Config: `examples/single-speaker.json`

Verify:

1. Request succeeds.
2. WAV passes local technical QC.
3. WAV is 24 kHz / mono / 16-bit PCM.
4. Chinese (Hant) pronunciation is manually reviewed.
5. Receipt exists.
6. Receipt contains no transcript/API key.
7. WAV imports into Premiere Pro.

## Case B — English single speaker

Create a safe fixture with short natural English dialogue.

Verify the same technical checks plus pronunciation and pacing.

## Case C — Two-speaker conversation

Config: `examples/dialogue.json`

Verify:

1. Both logical speakers remain distinct.
2. Turn ordering is correct.
3. Voice identity does not drift materially.
4. No speaker-label text is spoken aloud.
5. WAV and receipt checks pass.

## Evidence to record

- date/time
- exact commit SHA
- Python version
- `google-genai` version
- model ID
- provider voice IDs/names
- command used, excluding secrets
- WAV SHA-256
- technical QC result
- human pronunciation/creative notes

## Stop conditions

Stop and do not integrate into `ai-video-template-v2` when:

- API/schema behavior differs from the documented contract,
- returned audio fails technical QC,
- receipt leaks transcript/secrets,
- Traditional Chinese quality is not acceptable,
- multi-speaker identity is unstable.
