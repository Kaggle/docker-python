import os
import subprocess
import unittest

class TestTensorflowjs(unittest.TestCase):
    def test_version(self):
        result = subprocess.run([
                'tensorflowjs_converter',
                '--version',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print("tensorflowjs_converter version: ", result)

        self.assertEqual(0, result.returncode)
        self.assertIn(b'tensorflowjs', result.stdout)
