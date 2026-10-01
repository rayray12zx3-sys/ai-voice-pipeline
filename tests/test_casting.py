import json
from pathlib import Path
import tempfile
import unittest

from ai_voice_pipeline.casting import CastingPlan, load_casting_plan, safe_filename


class CastingTests(unittest.TestCase):
    def test_plan_builds_fair_single_speaker_requests(self):
        plan = CastingPlan(
            role="MOM",
            logical_voice_alias="MOM_VOICE_V1",
            model="gemini-3.8-flash-tts",
            text="固定測試句",
            style="自然、溫暖",
            candidates=("voice_a", "voice_b"),
        )
        a = plan.request_for("voice_a")
        b = plan.request_for("voice_b")
        self.assertEqual(a.turns, b.turns)
        self.assertEqual(a.voices["MOM_VOICE_V1"], "voice_a")
        self.assertEqual(b.voices["MOM_VOICE_V1"], "voice_b")
        self.assertEqual(plan.safe_summary()["candidate_count"], 2)
        self.assertNotIn("固定測試句", repr(plan.safe_summary()))

    def test_duplicate_candidates_rejected(self):
        with self.assertRaises(ValueError):
            CastingPlan(
                role="MOM",
                logical_voice_alias="MOM_VOICE_V1",
                model="gemini-3.8-flash-tts",
                text="test",
                style=None,
                candidates=("same", "same"),
            )

    def test_load_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "cast.json"
            path.write_text(json.dumps({
                "role": "SON",
                "logical_voice_alias": "SON_VOICE_V1",
                "model": "gemini-3.8-flash-tts",
                "text": "test",
                "style": "young",
                "candidates": ["voice_1"],
            }), encoding="utf-8")
            plan = load_casting_plan(path)
            self.assertEqual(plan.role, "SON")

    def test_safe_filename(self):
        self.assertEqual(safe_filename("voice/foo bar"), "voice-foo-bar")


if __name__ == "__main__":
    unittest.main()
