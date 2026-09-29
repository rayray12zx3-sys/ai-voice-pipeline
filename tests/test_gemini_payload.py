import base64
import unittest

from ai_voice_pipeline.contracts import DialogueTurn, VoiceRequest
from ai_voice_pipeline.providers.gemini import GeminiTTSProvider


class GeminiPayloadTests(unittest.TestCase):
    def test_single_speaker_payload(self):
        req = VoiceRequest(
            model="gemini-3.8-flash-tts",
            turns=(DialogueTurn("Hello", style="friendly"),),
            voices={"Narrator": "Kore"},
        )
        payload = GeminiTTSProvider.build_payload(req)
        self.assertEqual(payload["model"], "gemini-3.8-flash-tts")
        self.assertEqual(
            payload["generation_config"]["speech_config"],
            [{"voice": "Kore"}],
        )
        self.assertEqual(
            payload["input"][0]["content"][0]["annotations"][0]["style"],
            "friendly",
        )

    def test_single_speaker_without_style_has_no_empty_annotation(self):
        req = VoiceRequest(
            model="gemini-3.8-flash-tts",
            turns=(DialogueTurn("Hello"),),
            voices={"Narrator": "Kore"},
        )
        block = GeminiTTSProvider.build_payload(req)["input"][0]["content"][0]
        self.assertNotIn("annotations", block)

    def test_multi_speaker_payload(self):
        req = VoiceRequest(
            model="gemini-3.8-flash-lite-tts",
            turns=(
                DialogueTurn("Hi", speaker="A", style="warm"),
                DialogueTurn("Hello", speaker="B", style="calm"),
            ),
            voices={"A": "Kore", "B": "Puck"},
        )
        payload = GeminiTTSProvider.build_payload(req)
        speech = payload["generation_config"]["speech_config"]
        self.assertEqual(speech["mode"], "conversational")
        self.assertEqual(len(speech["speakers"]), 2)
        self.assertEqual(
            payload["input"][0]["content"][1]["annotations"][0]["speaker"],
            "B",
        )

    def test_decode_output_audio(self):
        raw = b"RIFFfake"
        encoded = base64.b64encode(raw).decode("ascii")
        self.assertEqual(GeminiTTSProvider.decode_output_audio(encoded), raw)

    def test_decode_rejects_invalid_base64(self):
        with self.assertRaises(RuntimeError):
            GeminiTTSProvider.decode_output_audio("%%%not-base64%%%")


if __name__ == "__main__":
    unittest.main()
