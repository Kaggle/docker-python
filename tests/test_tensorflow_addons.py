import unittest

import tensorflow as tf
import tensorflow_addons as tfa


class TestTensorflowAddons(unittest.TestCase):
    def test_tfa_image(self):
        img_raw = tf.io.read_file('/input/tests/data/dot.png')
        img = tf.io.decode_image(img_raw)
        img = tf.image.convert_image_dtype(img, tf.float32)
        mean = tfa.image.mean_filter2d(img, filter_shape=1)
        
        self.assertEqual(1, len(mean))
