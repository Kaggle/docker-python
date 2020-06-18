import unittest

from pydub import AudioSegment


class TestPydub(unittest.TestCase):    
    def test_import(self):
        sound = AudioSegment.from_file('/input/tests/data/test.wav')

        self.assertEqual(1810, len(sound))

