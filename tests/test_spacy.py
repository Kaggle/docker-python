import unittest

import spacy

class TestSpacy(unittest.TestCase):
    def test_model(self):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp('This is a sentence.')
        self.assertEqual(5, len(doc))
