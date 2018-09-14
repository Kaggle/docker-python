import unittest

from essentia.standard import Windowing

class TestEssentia(unittest.TestCase):
    def test_windowing(self):
        Windowing(type = 'hann')
