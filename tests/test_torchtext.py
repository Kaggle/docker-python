import unittest

from torchtext.data.metrics import bleu_score


class TestTorchtext(unittest.TestCase):
    def test_bleu_score(self):
        candidate = [['I', 'love', 'Kaggle', 'Notebooks']]
        refs = [[['Completely', 'Different']]]

        self.assertEqual(0, bleu_score(candidate, refs))

