import unittest

from google.cloud import bigquery
import tensorflow as tf


class TestTensorflowBigQuery(unittest.TestCase):

    # Some versions of bigquery crashed tensorflow, add this test to make sure that doesn't happen.
    # python -c "from google.cloud import bigquery; import tensorflow". This flow is common because bigquery is imported in kaggle_gcp.py
    # which is loaded at startup.
    def test_addition(self):
        result = tf.add(2, 3)
        self.assertEqual(5, result.numpy())