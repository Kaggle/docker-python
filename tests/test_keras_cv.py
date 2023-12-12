import unittest

import keras_cv
import keras
import numpy as np

from utils.kagglehub import create_test_kagglehub_server

class TestKerasCV(unittest.TestCase):
    def test_inference(self):
        with create_test_kagglehub_server():
            classifier = keras_cv.models.ImageClassifier.from_preset(
                'efficientnetv2_b0_imagenet_classifier',
                load_weights=False, # load randomly initialized model from preset architecture with weights
            )
            image = keras.utils.load_img('/input/tests/data/face.jpg')
            image = np.array(image)
            predictions = classifier.predict(np.expand_dims(image, axis=0))
            top_classes = predictions[0].argsort(axis=-1)
            self.assertEqual(1000, len(top_classes))