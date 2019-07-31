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
        )

        self.assertTrue(result.returncode == 0)
        self.assertTrue(b'Google Cloud SDK' in result.stdout)
