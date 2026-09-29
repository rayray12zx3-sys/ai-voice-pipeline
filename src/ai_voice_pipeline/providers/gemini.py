"""Gemini 3.8 TTS adapter.

Importing this module does not import the Google SDK and does not make network calls.
"""

from __future__ import annotations

import base64

from ..contracts import VoiceRequest


class GeminiTTSProvider:
    provider_name = "GEMINI"

    @staticmethod
    def build_payload(request: VoiceRequest) -> dict:
        content = []
        for turn in request.turns:
            metadata = {"type": "speech_metadata"}
            if turn.speaker is not None:
                metadata["speaker"] = turn.speaker
            if turn.style:
                metadata["style"] = turn.style
            content.append({
                "type": "text",
                "text": turn.text,
                "annotations": [metadata],
            })

        if request.multi_speaker:
            speech_config = {
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
                "content": content,
            }],
            "response_format": {
                "type": "audio",
                "mime_type": request.output_mime_type,
            },
            "generation_config": {
                "speech_config": speech_config,
            },
        }

    @classmethod
    def generate(cls, request: VoiceRequest) -> bytes:
        """Execute one Gemini TTS request and return decoded audio bytes."""
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                'Gemini execution requires: python -m pip install -e ".[gemini]"'
            ) from exc

        client = genai.Client()
        interaction = client.interactions.create(**cls.build_payload(request))
        data = interaction.output_audio.data
        if not data:
            raise RuntimeError("Gemini returned no audio data")
        return base64.b64decode(data)
