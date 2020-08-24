import unittest

from vowpalwabbit import pyvw

class TestVowpalwabbit(unittest.TestCase):
    def test_basic(self):
        vw = pyvw.vw(quiet=True)
        ex = vw.example('1 | a b c')
        vw.learn(ex)
        self.assertGreater(vw.predict(ex), 0)
