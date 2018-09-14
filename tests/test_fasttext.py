import unittest

import fastText

class TestFastText(unittest.TestCase):
    def test_tokenize(self):
        tokens = fastText.FastText.tokenize("Hello World")

        self.assertEqual(["Hello", "World"], tokens)
