import unittest

from ai_voice_pipeline.contracts import DialogueTurn, VoiceRequest
from ai_voice_pipeline.receipt import build_receipt, verify_output


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.req = VoiceRequest(
            model="gemini-3.8-flash-tts",
            turns=(DialogueTurn("Hello"),),
            voices={"Narrator": "Kore"},
        )

    def test_receipt_hashes_audio_without_transcript(self):
        receipt = build_receipt(self.req, b"audio-bytes", "output/test.wav")
        self.assertEqual(receipt["provider"], "GEMINI")
        self.assertEqual(len(receipt["request_sha256"]), 64)
        self.assertEqual(len(receipt["output_sha256"]), 64)
        self.assertNotIn("Hello", repr(receipt))

    def test_verify_output_passes(self):
        audio = b"audio-bytes"
        receipt = build_receipt(self.req, audio, "output/test.wav")
        ok, errors = verify_output(receipt, audio)
        self.assertTrue(ok)
        self.assertEqual(errors, ())

    def test_verify_output_detects_replacement(self):
        receipt = build_receipt(self.req, b"original", "output/test.wav")
        ok, errors = verify_output(receipt, b"changed")
        self.assertFalse(ok)
        self.assertIn("OUTPUT_HASH_MISMATCH", errors)


if __name__ == "__main__":
    unittest.main()
