import unittest

import tensorflow_text as tf_text


class TestTensorflowText(unittest.TestCase):
    def test_tokenizer(self):
        word_tokenizer = tf_text.WhitespaceTokenizer()

        tokens = word_tokenizer.tokenize("I love Kaggle!")

        self.assertEqual((3,), tokens.shape)
