import unittest

import json
import math
import keras_cv
import tensorflow as tf
import tensorflow_datasets as tfds
import keras
from keras import losses
import numpy as np
from keras import optimizers
from tensorflow.keras.optimizers import schedules
from keras import metrics

class TestKerasCV(unittest.TestCase):
    def test_inference(self):
        classifier = keras_cv.models.ImageClassifier.from_preset(
            'efficientnetv2_b0_imagenet_classifier'
        )
        image = keras.utils.load_img('/input/tests/data/cat.jpg')
        image = np.array(image)
        keras_cv.visualization.plot_image_gallery(
            [image], rows=1, cols=1, value_range=(0, 255), show=True, scale=4
        )
        predictions = classifier.predict(np.expand_dims(image, axis=0))
        top_classes = predictions[0].argsort(axis=-1)

        with open('/input/tests/data/ImagenetClassnames.json', "rb") as f:
            classes = json.load(f)

        top = [classes[str(i)] for i in top_classes[-1:]]
        self.assertEqual(top[0], 'Egyptian cat') 
