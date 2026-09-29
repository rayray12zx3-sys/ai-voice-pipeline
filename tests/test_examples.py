from pathlib import Path
import unittest

from ai_voice_pipeline.io import load_request


ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def test_single_speaker_example_loads(self):
        request = load_request(ROOT / "examples" / "single-speaker.json")
        self.assertFalse(request.multi_speaker)

    def test_dialogue_example_loads(self):
        request = load_request(ROOT / "examples" / "dialogue.json")
        self.assertTrue(request.multi_speaker)
        self.assertEqual(len(request.voices), 2)


if __name__ == "__main__":
    unittest.main()
