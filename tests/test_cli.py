import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

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

    def _casting_config(self, root: Path) -> Path:
        path = root / "casting.json"
        path.write_text(
            json.dumps({
                "role": "MOM",
                "logical_voice_alias": "MOM_VOICE_V1",
                "model": "gemini-3.8-flash-tts",
                "text": "固定測試句",
                "style": "自然、溫暖",
                "candidates": ["voice_a", "voice_b"],
            }, ensure_ascii=False),
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

    def test_cast_defaults_to_network_free_dry_run(self):
        with tempfile.TemporaryDirectory() as temp:
            config = self._casting_config(Path(temp))
            provider = MagicMock()
            provider.build_payload.side_effect = lambda request: {
                "voice": next(iter(request.voices.values()))
            }
            with patch("ai_voice_pipeline.cli.get_provider", return_value=provider):
                stream = io.StringIO()
                with patch("sys.stdout", stream):
                    code = main(["cast", str(config)])
            self.assertEqual(code, 0)
            payload = json.loads(stream.getvalue())
            self.assertEqual(payload["status"], "AUDITION")
            self.assertEqual(
                [item["voice_id"] for item in payload["candidates"]],
                ["voice_a", "voice_b"],
            )
            provider.generate.assert_not_called()

    def test_cast_execute_without_api_key_fails_before_generation(self):
        with tempfile.TemporaryDirectory() as temp:
            config = self._casting_config(Path(temp))
            provider = MagicMock()
            provider.build_payload.return_value = {}
            env = dict(os.environ)
            env.pop("GEMINI_API_KEY", None)
            with patch("ai_voice_pipeline.cli.get_provider", return_value=provider):
                with patch.dict(os.environ, env, clear=True):
                    with patch("sys.stderr", io.StringIO()):
                        code = main(["cast", str(config), "--execute"])
            self.assertEqual(code, 2)
            provider.generate.assert_not_called()

    def test_voices_uses_live_catalog_filters(self):
        provider = MagicMock()
        provider.list_voices.return_value = ({
            "id": "voice_x",
            "display_name": "Voice X",
            "language_code": "zh-TW",
            "accent": "Taiwanese",
            "gender": "female",
            "pitch": "medium",
            "description": "Warm conversational voice",
        },)
        with patch("ai_voice_pipeline.cli.get_provider", return_value=provider):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
                stream = io.StringIO()
                with patch("sys.stdout", stream):
                    code = main([
                        "voices",
                        "--language-code", "zh-TW",
                        "--type", "prebuilt",
                        "--json",
                    ])
        self.assertEqual(code, 0)
        payload = json.loads(stream.getvalue())
        self.assertEqual(payload[0]["id"], "voice_x")
        provider.list_voices.assert_called_once()
        kwargs = provider.list_voices.call_args.kwargs
        self.assertEqual(kwargs["language_code"], ("zh-TW",))
        self.assertEqual(kwargs["type_"], ("prebuilt",))


if __name__ == "__main__":
    unittest.main()
