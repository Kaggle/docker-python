import unittest

from pyfasttext import FastText

class TestPyFasttext(unittest.TestCase):
    def test_vector(self):
        model = FastText()

        model.supervised(input='/input/tests/data/text.txt', output='model', epoch=1, lr=0.7)
