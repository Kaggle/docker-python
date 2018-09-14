import unittest

from gensim import corpora

class TestGensim(unittest.TestCase):
    def test_dictionary(self):
        dic = corpora.Dictionary([['lorem', 'ipsum']])

        self.assertEqual(2, len(dic.token2id))
