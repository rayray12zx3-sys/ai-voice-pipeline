import io
import struct
import unittest
import wave

from ai_voice_pipeline.qc import qc_wav_bytes


def make_wav(*, sample_rate=24000, channels=1, sample_width=2, frames=2400):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as handle:
        handle.setnchannels(channels)
        handle.setsampwidth(sample_width)
        handle.setframerate(sample_rate)
        if sample_width != 2:
            handle.writeframes(b"\x00" * frames * channels * sample_width)
        else:
            samples = [1000, -1000] * ((frames * channels + 1) // 2)
            samples = samples[: frames * channels]
            handle.writeframes(struct.pack("<" + "h" * len(samples), *samples))
    return buffer.getvalue()


class QCTests(unittest.TestCase):
    def test_default_gemini_wav_passes(self):
        result = qc_wav_bytes(make_wav())
        self.assertTrue(result.ok)
        self.assertEqual(result.metadata.sample_rate, 24000)
        self.assertEqual(result.metadata.channels, 1)
        self.assertEqual(result.metadata.sample_width_bytes, 2)

    def test_invalid_container_fails(self):
        result = qc_wav_bytes(b"not-a-wav")
        self.assertFalse(result.ok)
        self.assertIn("INVALID_WAV", result.errors)

    def test_wrong_sample_rate_fails(self):
        result = qc_wav_bytes(make_wav(sample_rate=48000))
        self.assertFalse(result.ok)
        self.assertIn("UNEXPECTED_SAMPLE_RATE", result.errors)

    def test_wrong_channels_fails(self):
        result = qc_wav_bytes(make_wav(channels=2))
        self.assertFalse(result.ok)
        self.assertIn("UNEXPECTED_CHANNEL_COUNT", result.errors)


if __name__ == "__main__":
    unittest.main()
