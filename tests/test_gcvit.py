import unittest


import tensorflow as tf
from gcvit import GCViTTiny
from skimage.data import chelsea


class TestGCViT(unittest.TestCase):
    def test_prediction(self):
        model = GCViTTiny(pretrain=True)
        img = tf.keras.applications.imagenet_utils.preprocess_input(chelsea(), mode='torch') # Chelsea the cat
        img = tf.image.resize(img, (224, 224))[None,] # resize & create batch
        pred = model(img).numpy()
        print(tf.keras.applications.imagenet_utils.decode_predictions(pred)[0])