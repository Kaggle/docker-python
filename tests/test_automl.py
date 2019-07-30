import unittest

from google.cloud import automl_v1beta1 as automl

class TestAutoMl(unittest.TestCase):

    def test_version(self):
        self.assertIsNotNone(automl.auto_ml_client._GAPIC_LIBRARY_VERSION)

