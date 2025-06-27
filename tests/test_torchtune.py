import unittest
import subprocess

class TestTorchtune(unittest.TestCase):
    def test_help(self):
        result = subprocess.run(
            ["tune", "--help"], 
            capture_output=True,
            text=True
        )

        self.assertEqual(0, result.returncode)
        self.assertIn(
            "Download a model from the Hugging Face Hub or Kaggle", 
            result.stdout
        )
