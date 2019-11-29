import unittest

import torchaudio


class TestTorchaudio(unittest.TestCase):    
    def test_import(self):
        waveform, sample_rate = torchaudio.load('/input/tests/data/test.wav')

        self.assertEquals(2, len(waveform))
        self.assertEquals(44100, sample_rate)
