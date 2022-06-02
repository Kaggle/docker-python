"""
Computes embeddings test
"""


import unittest
from sentence_transformers import SentenceTransformer
import numpy as np

class ComputeEmbeddingsTest(unittest.TestCase):
    def setUp(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def test_encode_token_embeddings(self):
        """
        Test that encode(output_value='token_embeddings') works
        :return:
        """
        sent = ["Hello Word, a test sentence", "Here comes another sentence", "My final sentence", "Sentences", "Sentence five five five five five five five"]
        emb = self.model.encode(sent, output_value='token_embeddings', batch_size=2)
        assert len(emb) == len(sent)
        for s, e in zip(sent, emb):
            assert len(self.model.tokenize([s])['input_ids'][0]) == e.shape[0]


    def test_encode_single_sentences(self):
        #Single sentence
        emb = self.model.encode("Hello Word, a test sentence")
        assert emb.shape == (384,)
        assert abs(np.sum(emb) - 0.19781652) < 0.001

        # Single sentence as list
        emb = self.model.encode(["Hello Word, a test sentence"])
        assert emb.shape == (1, 384)
        assert abs(np.sum(emb) - 0.19781652) < 0.001

        # Sentence list
        emb = self.model.encode(["Hello Word, a test sentence", "Here comes another sentence", "My final sentence"])
        assert emb.shape == (3, 384)
        assert abs(np.sum(emb) - 0.46673426) < 0.001

    def test_encode_normalize(self):
        emb = self.model.encode(["Hello Word, a test sentence", "Here comes another sentence", "My final sentence"], normalize_embeddings=True)
        assert emb.shape == (3, 384)
        for norm in np.linalg.norm(emb, axis=1):
            assert abs(norm - 1) < 0.001

    def test_encode_tuple_sentences(self):
        # Input a sentence tuple
        emb = self.model.encode([("Hello Word, a test sentence", "Second input for model")])
        assert emb.shape == (1, 384)
        assert abs(abs(np.sum(emb)) - 0.20839658) < 0.001

        # List of sentence tuples
        emb = self.model.encode([("Hello Word, a test sentence", "Second input for model"), ("My second tuple", "With two inputs"), ("Final tuple", "final test")])
        assert emb.shape == (3, 384)
        assert abs(np.sum(emb) - 0.27391744) < 0.001
