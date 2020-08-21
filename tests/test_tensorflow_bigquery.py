import unittest

from google.cloud import bigquery
import tensorflow as tf


class TestTensorflowBigQuery(unittest.TestCase):
    def test_addition(self):        
        result = tf.add(2, 3)
        self.assertEqual(5, result.numpy())