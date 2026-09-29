import json
from pathlib import Path
import tempfile
import unittest

from ai_voice_pipeline.io import load_request, write_bytes_atomic


class IOTests(unittest.TestCase):
    def test_load_request(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "request.json"
            path.write_text(
                json.dumps({
                    "model": "gemini-3.8-flash-tts",
                    "voices": {"Narrator": "Kore"},
                    "turns": [{"text": "Hello"}],
                }),
                encoding="utf-8",
            )
            request = load_request(path)
            self.assertEqual(request.model, "gemini-3.8-flash-tts")
            self.assertEqual(request.turns[0].text, "Hello")

    def test_atomic_write_replaces_target(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "out.bin"
            path.write_bytes(b"old")
            write_bytes_atomic(path, b"new")
            self.assertEqual(path.read_bytes(), b"new")
            self.assertEqual(list(Path(temp).glob("*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
