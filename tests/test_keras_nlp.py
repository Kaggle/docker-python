import unittest

import keras_nlp
import keras
import numpy as np

class TestKerasNLP(unittest.TestCase):
    def test_inference(self):
        classifier = keras_nlp.models.BertClassifier.from_preset(
            'bert_tiny_en_uncased_sst2',
            load_weights=False, # load randomly initialized model from preset architecture with weights
        )
        predictions = classifier.predict(['I love modular workflows in keras-nlp!'])
        self.AssertEqual(2, len(predictions))