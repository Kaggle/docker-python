import unittest
import subprocess

class TestTorchtune(unittest.TestCase):
    def test_help(self):
        result = subprocess.run(["tune", "--help"], stdout=subprocess.PIPE)

        self.assertEqual(0, result.returncode)
        self.assertIsNone(result.stderr)
        self.assertIn("Download a model from the Hugging Face Hub or Kaggle Model Hub.", result.stdout.decode("utf-8"))
