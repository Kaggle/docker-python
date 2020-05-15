import unittest

import subprocess

class TestPapermill(unittest.TestCase):
    def test_papermill(self):
        result = subprocess.run([
            'papermill',
            '/input/tests/data/notebook.ipynb',
            '-',
        ], stdout=subprocess.PIPE)

        self.assertEqual(0, result.returncode)
        self.assertTrue(b'999' in result.stdout)
