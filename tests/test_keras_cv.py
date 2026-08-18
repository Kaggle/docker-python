import unittest

import keras_cv
import keras
import numpy as np

from common import p100_exempt
from utils.kagglehub import create_test_kagglehub_server

class TestKerasCV(unittest.TestCase):
    # cuDNN 9.19 (pulled in by torch 2.11) dropped the Pascal (sm_60) kernels from
    # libcudnn_ops/cnn/adv and ships PTX for sm_121 only, so nothing can be JIT'd
    # down to sm_60 either. Every cuDNN convolution engine fails on P100 with
    # CUDNN_STATUS_EXECUTION_FAILED. Not fixable here: cuDNN 9.19 is a hard
    # requirement of torch 2.11, which comes from the Colab base image.
    @p100_exempt
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