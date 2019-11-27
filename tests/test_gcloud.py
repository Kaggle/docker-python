import os
import subprocess
import unittest

class TestGcloud(unittest.TestCase):
    def test_version(self):
        result = subprocess.run([
                'gcloud',
                '--version',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print("gloud version: ", result)

        self.assertEqual(0, result.returncode)
        self.assertIn(b'Google Cloud SDK', result.stdout)
