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


if __name__ == "__main__":
    unittest.main()
