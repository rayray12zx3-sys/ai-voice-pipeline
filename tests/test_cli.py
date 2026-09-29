import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ai_voice_pipeline.cli import main


class CLITests(unittest.TestCase):
    def _config(self, root: Path) -> Path:
        path = root / "request.json"
        path.write_text(
            json.dumps({
                "model": "gemini-3.8-flash-tts",
                "voices": {"Narrator": "Kore"},
                "turns": [{"text": "Hello"}],
            }),
            encoding="utf-8",
        )
        return path

    def test_render_defaults_to_dry_run(self):
        with tempfile.TemporaryDirectory() as temp:
            config = self._config(Path(temp))
            stream = io.StringIO()
            with patch("sys.stdout", stream):
                code = main(["render", str(config)])
            self.assertEqual(code, 0)
            payload = json.loads(stream.getvalue())
            self.assertEqual(payload["model"], "gemini-3.8-flash-tts")

    def test_execute_without_api_key_fails_before_network(self):
        with tempfile.TemporaryDirectory() as temp:
            config = self._config(Path(temp))
            env = dict(os.environ)
            env.pop("GEMINI_API_KEY", None)
            with patch.dict(os.environ, env, clear=True):
                with patch("sys.stderr", io.StringIO()):
                    code = main(["render", str(config), "--execute"])
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
