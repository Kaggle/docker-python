import unittest

import json
import keras_cv
import keras
import numpy as np

class TestKerasCV(unittest.TestCase):
    def test_inference(self):
        classifier = keras_cv.models.ImageClassifier.from_preset(
            'efficientnetv2_b0_imagenet_classifier',
            load_weights=False, # load randomly initialized model from preset architecture with weights
        )
        image = keras.utils.load_img('/input/tests/data/face.jpg')
        image = np.array(image)
        keras_cv.visualization.plot_image_gallery(
            [image], rows=1, cols=1, value_range=(0, 255), show=True, scale=4
        )
        predictions = classifier.predict(np.expand_dims(image, axis=0))
        top_classes = predictions[0].argsort(axis=-1)
        self.assertEqual(1000, len(top_classes))