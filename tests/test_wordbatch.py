import unittest

import wordbatch

from wordbatch.extractors import WordBag

class TestWordBatch(unittest.TestCase):
    def test_wordbatch(self):
        wordbatch.WordBatch(extractor=(WordBag, {
            "hash_ngrams":2, 
            "hash_ngrams_weights":[0.5, -1.0], 
            "hash_size":2**23, 
            "norm":'l2', 
            "tf":'log', 
            "idf":50.0}))
