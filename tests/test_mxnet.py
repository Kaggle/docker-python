import unittest
from common import gpu_test

import mxnet as mx
from gluonnlp import Vocab
from gluonnlp.data import count_tokens

from gluoncv.data.transforms.image import imresize


class TestMxNet(unittest.TestCase):
    def test_array(self):    
        x = mx.nd.array([[1, 2, 3], [4, 5, 6]])

        self.assertEqual((2, 3), x.shape)

    @gpu_test
    def test_array_gpu(self):
        x = mx.nd.array([2, 2, 2], ctx=mx.gpu(0))
        y = mx.nd.array([1, 1, 1], ctx=mx.gpu(0))
        self.assertEqual(3, ((x - y).sum().asscalar()))

    def test_gluon_nlp(self):
        # get corpus statistics
        counter = count_tokens(['alpha', 'beta', 'gamma', 'beta'])
        # create Vocab
        vocab = Vocab(counter)
        # find index based on token
        self.assertEqual(4, vocab['beta'])

    def test_gluon_cv(self):
        # create fake RGB image of 300x300 of shape: Height x Width x Channel as OpenCV expects
        img = mx.random.uniform(0, 255, (300, 300, 3)).astype('uint8')
        # resize image to 200x200. This call uses OpenCV
        # GluonCV is not of much use if OpenCV is not there or fails
        img = imresize(img, 200, 200)
        self.assertEqual((200, 200, 3), img.shape)
