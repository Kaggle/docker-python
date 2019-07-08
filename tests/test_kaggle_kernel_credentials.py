import unittest

from kaggle_secrets import GcpTarget
from kaggle_gcp import KaggleKernelCredentials

class TestKaggleKernelCredentials(unittest.TestCase):

    def test_default_target(self):
        creds = KaggleKernelCredentials()
        self.assertEqual(GcpTarget.BIGQUERY, creds.target)
