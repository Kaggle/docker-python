import unittest

import keras_nlp
import keras
import numpy as np
import tensorflow as tf

class TestKerasNLP(unittest.TestCase):
    def test_fit(self):
        # From https://keras.io/api/keras_nlp/models/bert/bert_classifier/
        features = {
            "token_ids": tf.ones(shape=(2, 12), dtype=tf.int64),
            "segment_ids": tf.constant(
                [[0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0]] * 2, shape=(2, 12)
            ),
            "padding_mask": tf.constant(
                [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]] * 2, shape=(2, 12)
            ),
        }
        labels = [0, 3]

        classifier = keras_nlp.models.BertClassifier.from_preset(
            'bert_tiny_en_uncased',
            load_weights=False, # load randomly initialized model from preset architecture with weights
            preprocessor=None, # to avoid downloading the vocabulary
            num_classes=4,
        )
        classifier.fit(x=features, y=labels, batch_size=2)