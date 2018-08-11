import unittest

import nltk

class TestNLTK(unittest.TestCase):
    def test_tokenize(self):
        tokens = nltk.word_tokenize("At eight o'clock")

        self.assertEqual(["At", "eight", "o'clock"], tokens)
