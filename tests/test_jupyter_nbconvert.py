import unittest

import subprocess

class TestJupyterNbconvert(unittest.TestCase):
    def test_nbconvert_to_notebook(self):
        result = subprocess.run([
            'jupyter',
            'nbconvert',
            '--to',
            'notebook',
            '--template',
            '/opt/kaggle/nbconvert-extensions.tpl',
            '--execute',
            '--stdout',
            '/input/tests/data/notebook.ipynb',
        ], stdout=subprocess.PIPE)

        self.assertEqual(0, result.returncode)
        self.assertTrue(b'999' in result.stdout)

    def test_nbconvert_to_html(self):
        result = subprocess.run([
            'jupyter',
            'nbconvert',
            '--to',
            'html',
            '--template',
            '/opt/kaggle/nbconvert-extensions.tpl',
            '--execute',
            '--stdout',
            '/input/tests/data/notebook.ipynb',
        ], stdout=subprocess.PIPE)

        self.assertEqual(0, result.returncode)
        self.assertTrue(b'999' in result.stdout)
