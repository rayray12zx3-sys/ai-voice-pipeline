import unittest

from ai_voice_pipeline.providers.gemini import GeminiTTSProvider
from ai_voice_pipeline.providers.registry import get_provider, provider_names


class RegistryTests(unittest.TestCase):
    def test_gemini_is_registered(self):
        self.assertIn("GEMINI", provider_names())
        self.assertIs(get_provider("gemini"), GeminiTTSProvider)

    def test_unknown_provider_fails_closed(self):
        with self.assertRaises(ValueError):
            get_provider("unknown")


if __name__ == "__main__":
    unittest.main()
