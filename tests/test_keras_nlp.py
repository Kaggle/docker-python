import unittest

import keras_nlp
import keras
import numpy as np

from utils.kagglehub import create_test_kagglehub_server

class TestKerasNLP(unittest.TestCase):
    def test_fit(self):
        with create_test_kagglehub_server():
            classifier = keras_nlp.models.BertClassifier.from_preset(
                'bert_tiny_en_uncased',
                load_weights=False, # load randomly initialized model from preset architecture with weights
                num_classes=2,
                activation="softmax",
            )
            result = classifier.predict(['What an amazing movie!'])
            self.assertEqual((1, 2), result.shape)