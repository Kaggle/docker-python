import os
import subprocess
import unittest

class TestGcloud(unittest.TestCase):
    def test_version(self):
        result = subprocess.run([
                'gcloud',
                'version',
            ],
            stdout=subprocess.PIPE,
        )

        self.assertIn(b'Google Cloud SDK', result.stdout)
