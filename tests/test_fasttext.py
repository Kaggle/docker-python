import unittest

import fasttext

class TestFastText(unittest.TestCase):
    def test_tokenize(self):
        tokens = fasttext.FastText.tokenize("Hello World")

        self.assertEqual(["Hello", "World"], tokens)
