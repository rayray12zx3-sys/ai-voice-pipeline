"""Gemini 3.8 TTS adapter.

Importing this module does not import the Google SDK and does not make network calls.
"""

from __future__ import annotations

import base64

from ..contracts import VoiceRequest


class GeminiTTSProvider:
    provider_name = "GEMINI"

    @staticmethod
    def _turn_content(request: VoiceRequest) -> list[dict]:
        content: list[dict] = []
        for turn in request.turns:
            block: dict = {"type": "text", "text": turn.text}
            annotation: dict = {"type": "speech_metadata"}
            if turn.speaker is not None:
                annotation["speaker"] = turn.speaker
            if turn.style:
                annotation["style"] = turn.style
            if len(annotation) > 1:
                block["annotations"] = [annotation]
            content.append(block)
        return content

    @classmethod
    def build_payload(cls, request: VoiceRequest) -> dict:
        """Translate a provider-neutral request into the Gemini Interactions schema."""
        if request.multi_speaker:
            speech_config: dict | list[dict] = {
                "mode": "conversational",
                "speakers": [
                    {"speaker": speaker, "voice": voice}
                    for speaker, voice in request.voices.items()
                ],
            }
        else:
            voice = next(iter(request.voices.values()))
            speech_config = [{"voice": voice}]

        return {
            "model": request.model,
            "input": [{
                "type": "user_input",
                "content": cls._turn_content(request),
            }],
            "response_format": {
                "type": "audio",
                "mime_type": request.output_mime_type,
            },
            "generation_config": {
                "speech_config": speech_config,
            },
        }

    @staticmethod
    def decode_output_audio(encoded: str | bytes) -> bytes:
        if not encoded:
            raise RuntimeError("Gemini returned empty audio data")
        try:
            decoded = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            raise RuntimeError("Gemini returned invalid base64 audio data") from exc
        if not decoded:
            raise RuntimeError("Gemini returned zero decoded audio bytes")
        return decoded

    @classmethod
    def generate(cls, request: VoiceRequest) -> bytes:
        """Execute one Gemini TTS request and return decoded WAV bytes."""
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                'Gemini execution requires: python -m pip install -e ".[gemini]"'
            ) from exc

        client = genai.Client()
        interaction = client.interactions.create(**cls.build_payload(request))
        output_audio = getattr(interaction, "output_audio", None)
        data = getattr(output_audio, "data", None)
        return cls.decode_output_audio(data)
