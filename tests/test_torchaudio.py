import unittest

import torchaudio


class TestTorchaudio(unittest.TestCase):    
    def test_import(self):
        waveform, sample_rate = torchaudio.load('/input/tests/data/test.wav')

        self.assertEqual(2, len(waveform))
        self.assertEqual(44100, sample_rate)
