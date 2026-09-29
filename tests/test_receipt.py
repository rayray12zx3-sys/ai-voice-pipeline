import unittest

from ai_voice_pipeline.contracts import DialogueTurn, VoiceRequest
from ai_voice_pipeline.receipt import build_receipt


class ReceiptTests(unittest.TestCase):
    def test_receipt_hashes_audio(self):
        req = VoiceRequest(
            model="gemini-3.8-flash-tts",
            turns=(DialogueTurn("Hello"),),
            voices={"Narrator": "Kore"},
        )
        receipt = build_receipt(req, b"audio-bytes", "output/test.wav")
        self.assertEqual(receipt["provider"], "GEMINI")
        self.assertEqual(len(receipt["request_sha256"]), 64)
        self.assertEqual(len(receipt["output_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
