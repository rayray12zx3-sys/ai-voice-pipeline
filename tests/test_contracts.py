import unittest

from ai_voice_pipeline.contracts import DialogueTurn, VoiceRequest


class ContractTests(unittest.TestCase):
    def test_single_speaker(self):
        req = VoiceRequest(
            model="gemini-3.8-flash-tts",
            turns=(DialogueTurn("Hello."),),
            voices={"Narrator": "Kore"},
        )
        self.assertFalse(req.multi_speaker)

    def test_two_speaker_requires_matching_bindings(self):
        with self.assertRaises(ValueError):
            VoiceRequest(
                model="gemini-3.8-flash-tts",
                turns=(
                    DialogueTurn("Hi", speaker="A"),
                    DialogueTurn("Hello", speaker="B"),
                ),
                voices={"A": "Kore"},
            )

    def test_more_than_two_speakers_rejected(self):
        with self.assertRaises(ValueError):
            VoiceRequest(
                model="gemini-3.8-flash-tts",
                turns=(
                    DialogueTurn("1", speaker="A"),
                    DialogueTurn("2", speaker="B"),
                    DialogueTurn("3", speaker="C"),
                ),
                voices={"A": "Kore", "B": "Puck", "C": "Charon"},
            )

    def test_r0_rejects_non_wav_output(self):
        with self.assertRaises(ValueError):
            VoiceRequest(
                model="gemini-3.8-flash-tts",
                turns=(DialogueTurn("Hello"),),
                voices={"Narrator": "Kore"},
                output_mime_type="audio/l16",
            )

    def test_safe_summary_excludes_transcript(self):
        req = VoiceRequest(
            model="gemini-3.8-flash-lite-tts",
            turns=(DialogueTurn("private transcript"),),
            voices={"Narrator": "Kore"},
        )
        summary = req.safe_summary()
        self.assertNotIn("private transcript", repr(summary))
        self.assertEqual(summary["turn_count"], 1)


if __name__ == "__main__":
    unittest.main()
